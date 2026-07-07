"""
Geo Intelligence Agent — Utilities
Geospatial data helpers, clustering utilities, folium heatmap generation.
"""

from __future__ import annotations
import os
from typing import TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    import pandas as pd
    import numpy as np

try:
    import pandas as _pd  # noqa: F401
    import numpy as _np  # noqa: F401
except ImportError:
    pass


def build_complaint_dataframe(complaints: list[dict]) -> pd.DataFrame:
    """Convert complaint records to a pandas DataFrame for clustering."""
    import pandas as pd
    df = pd.DataFrame(complaints)
    required = {"lat", "lon", "fraud_type", "timestamp"}
    for col in required:
        if col not in df.columns:
            df[col] = None
    df = df.dropna(subset=["lat", "lon"])
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)
    return df


def run_dbscan(df: pd.DataFrame, eps_km: float = 2.0, min_samples: int = 3) -> np.ndarray:
    """
    DBSCAN clustering on lat/lon coordinates.
    eps_km: radius in km (converted to radians for haversine metric).
    Returns cluster labels array.
    """
    import numpy as np  # noqa: F811
    from sklearn.cluster import DBSCAN
    coords = df[["lat", "lon"]].values
    # Convert km to radians for haversine
    eps_rad = eps_km / 6371.0
    coords_rad = np.radians(coords)
    db = DBSCAN(eps=eps_rad, min_samples=min_samples, algorithm="ball_tree", metric="haversine")
    labels: np.ndarray = db.fit_predict(coords_rad)  # type: ignore[assignment]
    return labels


def extract_hotspots(df: pd.DataFrame, labels: np.ndarray) -> list[dict]:
    """Convert DBSCAN cluster labels to hotspot dicts."""
    import numpy as np
    from shared.schemas import RiskLevel

    hotspots = []
    unique_labels = set(labels)
    unique_labels.discard(-1)  # -1 = noise

    for label in unique_labels:
        mask = labels == label
        cluster_df = df[mask]
        centroid_lat = float(cluster_df["lat"].mean())
        centroid_lon = float(cluster_df["lon"].mean())
        count = int(mask.sum())
        # Dominant fraud type
        if "fraud_type" in cluster_df.columns:
            dominant = cluster_df["fraud_type"].value_counts().idxmax()
        else:
            dominant = "unknown"
        # Radius: max distance from centroid (degrees → km approx)
        dists = np.sqrt((cluster_df["lat"] - centroid_lat)**2 + (cluster_df["lon"] - centroid_lon)**2)
        radius_km = round(float(dists.max()) * 111, 2)

        risk_level = RiskLevel.CRITICAL if count >= 20 else RiskLevel.HIGH if count >= 10 else RiskLevel.MEDIUM

        hotspots.append({
            "lat": centroid_lat,
            "lon": centroid_lon,
            "radius_km": radius_km,
            "complaint_count": count,
            "dominant_fraud_type": dominant,
            "risk_level": risk_level.value,
        })

    return sorted(hotspots, key=lambda h: h["complaint_count"], reverse=True)


def generate_heatmap(df: pd.DataFrame) -> str | None:
    """Generate folium HeatMap HTML and save to temp file. Returns file path."""
    try:
        import folium
        from folium.plugins import HeatMap

        center_lat = df["lat"].mean()
        center_lon = df["lon"].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="CartoDB dark_matter")
        heat_data = df[["lat", "lon"]].values.tolist()
        HeatMap(heat_data, radius=15, blur=10, min_opacity=0.4).add_to(m)

        os.makedirs("reports", exist_ok=True)
        out_path = os.path.join("reports", "geo_heatmap.html")
        m.save(out_path)
        logger.info(f"Heatmap saved to {out_path}")
        return out_path
    except Exception as e:
        logger.warning(f"Heatmap generation failed: {e}")
        return None


def compute_temporal_trend(df: pd.DataFrame) -> dict[str, int]:
    """Count complaints by hour of day."""
    try:
        import pandas as pd
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df["hour"] = df["timestamp"].dt.hour  # type: ignore[union-attr]
        trend = df.groupby("hour").size().to_dict()
        return {str(k): v for k, v in trend.items()}
    except Exception as e:
        logger.warning(f"Temporal trend failed: {e}")
        return {}


def make_patrol_recommendations(hotspots: list[dict]) -> list[str]:
    recs = []
    for hs in hotspots[:5]:
        recs.append(
            f"Deploy patrol to ({hs['lat']:.4f}, {hs['lon']:.4f}) — "
            f"{hs['complaint_count']} {hs['dominant_fraud_type']} complaints, radius {hs['radius_km']} km."
        )
    return recs
