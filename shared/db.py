"""
SentinelShield AI — Database Connection Helpers
Provides singleton clients for PostgreSQL, Redis, Neo4j, and Qdrant with
retry mechanisms, timeouts, health checks, and graceful shutdown handlers.
"""

from __future__ import annotations
import time
from functools import lru_cache
from loguru import logger

from shared.config import get_settings

settings = get_settings()

# ─────────────────────────────────────────────────────────────────────────────
# PostgreSQL — SQLAlchemy engine
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache()
def get_engine():
    from sqlalchemy import create_engine
    
    db_url = settings.DATABASE_URL
    connect_args = {"connect_timeout": int(settings.DB_CONNECT_TIMEOUT)}
    
    for attempt in range(1, settings.DB_MAX_RETRIES + 1):
        try:
            logger.info(f"Attempting PostgreSQL connection (attempt {attempt}/{settings.DB_MAX_RETRIES})…")
            engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args=connect_args,
            )
            # Test connectivity immediately
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"PostgreSQL connected successfully: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
            return engine
        except Exception as e:
            logger.warning(f"PostgreSQL connection attempt {attempt} failed: {e}")
            if attempt == settings.DB_MAX_RETRIES:
                logger.error("Max PostgreSQL connection attempts reached. Falling back to default engine (unconnected).")
                # Return engine anyway so application doesn't crash on startup
                return create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
            time.sleep(settings.DB_RETRY_DELAY_SEC)


@lru_cache()
def get_session_factory():
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)


# ─────────────────────────────────────────────────────────────────────────────
# Redis
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache()
def get_redis_client():
    import redis
    from redis.retry import Retry
    from redis.backoff import ExponentialBackoff

    retry = Retry(ExponentialBackoff(), settings.DB_MAX_RETRIES)
    
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=settings.DB_CONNECT_TIMEOUT,
            socket_connect_timeout=settings.DB_CONNECT_TIMEOUT,
            retry=retry,
            retry_on_timeout=True,
        )
        logger.info(f"Redis client initialized: {settings.REDIS_URL}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Redis client: {e}")
        # Return simple offline/dummy redis if needed, but standard client works
        return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


# ─────────────────────────────────────────────────────────────────────────────
# Neo4j
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache()
def get_neo4j_driver():
    from neo4j import GraphDatabase
    
    try:
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            connection_timeout=settings.DB_CONNECT_TIMEOUT,
            max_connection_lifetime=30.0,
            max_transaction_retry_time=settings.DB_CONNECT_TIMEOUT * settings.DB_MAX_RETRIES,
        )
        logger.info(f"Neo4j driver initialized: {settings.NEO4J_URI}")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j driver: {e}")
        raise e


# ─────────────────────────────────────────────────────────────────────────────
# Qdrant
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache()
def get_qdrant_client():
    from qdrant_client import QdrantClient
    
    try:
        client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY or None,
            timeout=settings.DB_CONNECT_TIMEOUT,
        )
        logger.info(f"Qdrant client initialized: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {e}")
        raise e


# ─────────────────────────────────────────────────────────────────────────────
# Health Checks
# ─────────────────────────────────────────────────────────────────────────────

def check_postgres_health() -> bool:
    try:
        from sqlalchemy import text
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"PostgreSQL health check failed: {e}")
        return False


def check_redis_health() -> bool:
    try:
        client = get_redis_client()
        return bool(client.ping())
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False


def check_neo4j_health() -> bool:
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        return True
    except Exception as e:
        logger.warning(f"Neo4j health check failed: {e}")
        return False


def check_qdrant_health() -> bool:
    try:
        client = get_qdrant_client()
        # Fast query to list collections
        client.get_collections()
        return True
    except Exception as e:
        logger.warning(f"Qdrant health check failed: {e}")
        return False


def check_all_db_health() -> dict[str, bool]:
    """Check connection status of all external systems."""
    return {
        "postgres": check_postgres_health(),
        "redis": check_redis_health(),
        "neo4j": check_neo4j_health(),
        "qdrant": check_qdrant_health(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Teardown / Graceful Shutdown
# ─────────────────────────────────────────────────────────────────────────────

def close_databases():
    """Teardown connection pools gracefully."""
    logger.info("Starting graceful database shutdown…")
    
    # 1. Dispose SQLAlchemy
    try:
        engine = get_engine()
        engine.dispose()
        logger.info("PostgreSQL engine connection pool disposed.")
    except Exception as e:
        logger.debug(f"PostgreSQL connection cleanup skipped or failed: {e}")

    # 2. Close Redis
    try:
        client = get_redis_client()
        client.close()
        logger.info("Redis client connection closed.")
    except Exception as e:
        logger.debug(f"Redis connection cleanup skipped or failed: {e}")

    # 3. Close Neo4j
    try:
        driver = get_neo4j_driver()
        driver.close()
        logger.info("Neo4j driver connection closed.")
    except Exception as e:
        logger.debug(f"Neo4j connection cleanup skipped or failed: {e}")

    # 4. Close Qdrant
    try:
        client = get_qdrant_client()
        if hasattr(client, "close"):
            client.close()
        elif hasattr(client, "_client") and hasattr(client._client, "close"):
            client._client.close()
        logger.info("Qdrant client connection closed.")
    except Exception as e:
        logger.debug(f"Qdrant connection cleanup skipped or failed: {e}")

    # Clear lru_caches
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    get_redis_client.cache_clear()
    get_neo4j_driver.cache_clear()
    get_qdrant_client.cache_clear()
    logger.info("Database clients and driver caches cleared.")
