"""
SentinelShield AI — Database Connection Helpers
Provides singleton clients for PostgreSQL, Redis, Neo4j, and Qdrant.
"""

from __future__ import annotations
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
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    logger.info(f"PostgreSQL connected: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    return engine


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
    client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info(f"Redis connected: {settings.REDIS_URL}")
    return client


# ─────────────────────────────────────────────────────────────────────────────
# Neo4j
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache()
def get_neo4j_driver():
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )
    logger.info(f"Neo4j connected: {settings.NEO4J_URI}")
    return driver


# ─────────────────────────────────────────────────────────────────────────────
# Qdrant
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache()
def get_qdrant_client():
    from qdrant_client import QdrantClient
    client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY or None,
    )
    logger.info(f"Qdrant connected: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    return client
