"""
Geo Intelligence Agent — Core Pipeline
DBSCAN clustering → hotspot extraction → heatmap → patrol recommendations.
"""

from __future__ import annotations
import time
from loguru import logger

from shared.config import get_settings
from shared.schemas import GeoIntelligenceResult, Hotspot, RiskLevel
from services.geo_agent.utils import (
    build_complaint_dataframe, run_dbscan, extract_hotspots,
    generate_heatmap, compute_temporal_trend, make_patrol_recommendations
)

settings = get_settings()


def run_geo_pipeline(
    complaints: list[dict],
    lat: float | None = None,
    lon: float | None = None,
    district: str | None = None,
    time_window_days: int = 30,
    case_id: str | None = None,
) -> GeoIntelligenceResult:
    """
    Geospatial intelligence pipeline.

    If complaints list is empty and lat/lon provided, we inject a single record
    for the current case location. In production, complaints are fetched from DB.

    Args:
        complaints: List of complaint dicts with {lat, lon, fraud_type, timestamp}
        lat/lon: Current complaint location (added to complaints list)
        district: Optional filter
        time_window_days: Analysis window
        case_id: Optional identifier
    """
    t0 = time.time()

    # Inject current case location if provided
    working_complaints = list(complaints)
    if lat is not None and lon is not None:
        working_complaints.append({
            "lat": lat, "lon": lon, "fraud_type": "unknown",
            "timestamp": None, "complaint_id": case_id,
        })

    if not working_complaints:
        elapsed = (time.time() - t0) * 1000
        return GeoIntelligenceResult(
            total_complaints_analyzed=0,
            processing_time_ms=elapsed,
            error="No complaint records provided.",
        )

    # Build DataFrame
    df = build_complaint_dataframe(working_complaints)
    if df.empty:
        elapsed = (time.time() - t0) * 1000
        return GeoIntelligenceResult(
            total_complaints_analyzed=0,
            processing_time_ms=elapsed,
            error="No valid lat/lon records.",
        )

    # Clustering
    labels = run_dbscan(df, eps_km=2.0, min_samples=max(2, len(df) // 10))

    # Hotspot extraction
    hotspots_raw = extract_hotspots(df, labels)
    hotspots = [Hotspot(**h) for h in hotspots_raw]

    # Heatmap
    heatmap_path = generate_heatmap(df) if len(df) >= 3 else None

    # Temporal trend
    temporal_trend = compute_temporal_trend(df)

    # Patrol recommendations
    patrol_recs = make_patrol_recommendations(hotspots_raw)

    elapsed = (time.time() - t0) * 1000
    logger.info(
        f"[GeoAgent] case={case_id} complaints={len(df)} hotspots={len(hotspots)} t={elapsed:.0f}ms"
    )

    return GeoIntelligenceResult(
        hotspots=hotspots,
        heatmap_html_path=heatmap_path,
        patrol_recommendations=patrol_recs,
        temporal_trend=temporal_trend,
        total_complaints_analyzed=len(df),
        risk_zones=[h for h in hotspots_raw if h["risk_level"] in ("HIGH", "CRITICAL")],
        processing_time_ms=elapsed,
    )
