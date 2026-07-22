"""
SentinelShield AI — Database Schema Initialization & Mock Seeding
Automates table creations in PostgreSQL, collections setup in Qdrant,
and uniqueness constraints / suspect relationship seeding in Neo4j.
"""

import time
from loguru import logger
from sqlalchemy import text
from shared.config import get_settings
from shared.db import get_engine, get_neo4j_driver, get_qdrant_client

settings = get_settings()

def init_postgres():
    """Create complaints table and seed historical coordinates for DBSCAN clustering."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Create Table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS complaints (
                id SERIAL PRIMARY KEY,
                case_id VARCHAR(100) UNIQUE NOT NULL,
                lat DOUBLE PRECISION,
                lon DOUBLE PRECISION,
                fraud_type VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            conn.execute(text(create_table_sql))
            conn.commit()
            logger.info("PostgreSQL complaints table verified/created.")

            # Seed complaints (around Delhi coordinates for DBSCAN cluster demo)
            seed_sql = """
            INSERT INTO complaints (case_id, lat, lon, fraud_type, timestamp)
            VALUES
                ('HIST-1001', 28.6139, 77.2090, 'digital_arrest', '2026-07-22 10:00:00'),
                ('HIST-1002', 28.6145, 77.2085, 'digital_arrest', '2026-07-22 11:30:00'),
                ('HIST-1003', 28.6130, 77.2100, 'digital_arrest', '2026-07-22 12:15:00'),
                ('HIST-1004', 28.6150, 77.2075, 'digital_arrest', '2026-07-22 13:45:00'),
                ('HIST-1005', 28.6125, 77.2095, 'digital_arrest', '2026-07-22 14:00:00'),
                ('HIST-1006', 22.8046, 86.2029, 'upi_fraud', '2026-07-22 10:00:00'),
                ('HIST-1007', 22.8050, 86.2035, 'upi_fraud', '2026-07-22 11:15:00'),
                ('HIST-1008', 22.8039, 86.2020, 'upi_fraud', '2026-07-22 12:30:00'),
                ('HIST-1009', 22.8055, 86.2040, 'upi_fraud', '2026-07-22 13:00:00')
            ON CONFLICT (case_id) DO NOTHING;
            """
            conn.execute(text(seed_sql))
            conn.commit()
            logger.info("PostgreSQL complaints coordinates seeds completed.")
    except Exception as e:
        logger.warning(f"PostgreSQL initialization failed or skipped: {e}")


def init_neo4j():
    """Register Neo4j constraints and seed a historical case link for cross-case matching."""
    driver = None
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # Create uniqueness constraints
            constraints = [
                "CREATE CONSTRAINT FOR (c:Complaint) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT FOR (p:Phone) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT FOR (u:UPI) REQUIRE u.id IS UNIQUE",
                "CREATE CONSTRAINT FOR (b:BankAccount) REQUIRE b.id IS UNIQUE"
            ]
            for cypher in constraints:
                try:
                    session.run(cypher)
                except Exception as ce:
                    logger.debug(f"Constraint creation skipped (might already exist): {ce}")

            # Seed a historical case connecting to the Digital Arrest phone and UPI presets
            seed_cypher = """
            MERGE (c:Complaint {id: 'Complaint_CASE-2026-4011'}) SET c.value = 'CASE-2026-4011'
            MERGE (p:Phone {id: 'Phone_+91 81302 99421'}) SET p.value = '+91 81302 99421'
            MERGE (u:UPI {id: 'UPI_payment.police@paytm'}) SET u.value = 'payment.police@paytm'
            MERGE (c)-[:MENTIONS]->(p)
            MERGE (c)-[:MENTIONS]->(u)
            """
            session.run(seed_cypher)
            logger.info("Neo4j schemas constraints and mock case links seeded successfully.")
    except Exception as e:
        logger.warning(f"Neo4j initialization failed or skipped: {e}")
    finally:
        if driver:
            try:
                driver.close()
            except Exception:
                pass


def init_qdrant():
    """Verify and initialize case, evidence, and legal collections in Qdrant."""
    try:
        client = get_qdrant_client()
        from qdrant_client.models import Distance, VectorParams

        collections = [
            settings.QDRANT_COLLECTION_CASES,
            settings.QDRANT_COLLECTION_EVIDENCE,
            settings.QDRANT_COLLECTION_LEGAL
        ]
        
        for col in collections:
            try:
                # Check if collection exists
                client.get_collection(col)
                logger.info(f"Qdrant collection '{col}' already exists.")
            except Exception:
                logger.info(f"Creating Qdrant collection '{col}' (size={settings.EMBEDDING_DIMENSION})...")
                client.create_collection(
                    collection_name=col,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
        logger.info("Qdrant collections initialized successfully.")
    except Exception as e:
        logger.warning(f"Qdrant initialization failed or skipped: {e}")


def initialize_all_databases():
    """Main executor to prepare postgres, neo4j, and qdrant schemas."""
    logger.info("Starting system-wide database initializations...")
    init_postgres()
    init_neo4j()
    init_qdrant()
    logger.info("Database initializations completed.")


if __name__ == "__main__":
    initialize_all_databases()
