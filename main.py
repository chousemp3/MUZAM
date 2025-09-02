#!/usr/bin/env python3
"""
MUZAM Entry Point

Main entry point for the MUZAM audio recognition system.
This script allows users to quickly start using MUZAM.
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def main():
    """Main entry point for MUZAM"""
    print("🎵 MUZAM - Open Source Audio Recognition Engine")
    print("===============================================")
    print("Better than Shazam • Privacy-First • Lightning Fast")
    print()

    # Check if this is the first run
    if not (project_dir / "muzam.db").exists():
        print("🚀 First-time setup detected!")
        print("Initializing database...")

        try:
            from muzam.database.init import init_database

            init_database()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            return 1

    print("Available commands:")
    print("  python -m muzam.cli.main --help     # Show CLI help")
    print("  python -m muzam.web.app             # Start web server")
    print("  python test_muzam.py                # Run tests")
    print()
    print("Quick start:")
    print("  muzam recognize song.mp3            # Recognize a song")
    print("  muzam listen                        # Listen from microphone")
    print("  muzam serve                         # Start web interface")
    print()

    # Try to import and show basic stats
    try:
        from muzam.database.manager import DatabaseManager

        db_manager = DatabaseManager()
        stats = db_manager.get_database_size()

        print("📊 Database Statistics:")
        print(f"  Songs: {stats['songs']:,}")
        print(f"  Fingerprints: {stats['fingerprints']:,}")
        print(f"  Recognitions: {stats['recognitions']:,}")

    except Exception as e:
        print(f"⚠️  Could not load database stats: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
