#!/usr/bin/env python3
"""
Database Initialization Script for MUZAM

Creates and initializes the local SQLite database with proper schema.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from muzam.database.manager import DatabaseManager
from muzam.core.recognizer import AudioRecognizer


def init_database():
    """Initialize the MUZAM database"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        logger.info("🎵 Initializing MUZAM database...")

        # Create database manager (this will create tables)
        db_manager = DatabaseManager()

        # Get initial stats
        stats = db_manager.get_database_size()

        logger.info("✅ Database initialized successfully!")
        logger.info(f"📊 Database Statistics:")
        logger.info(f"   Songs: {stats['songs']}")
        logger.info(f"   Fingerprints: {stats['fingerprints']}")
        logger.info(f"   Recognitions: {stats['recognitions']}")

        return True

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
