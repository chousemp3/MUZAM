"""
Database Manager

Handles local and cloud database operations for audio fingerprints
and metadata storage.
"""

import sqlite3
import json
import asyncio
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
import time

from ..fingerprint.generator import Fingerprint
from ..models import RecognitionResult


@dataclass
class Song:
    """Song metadata structure"""
    id: Optional[int] = None
    title: str = ""
    artist: str = ""
    album: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[float] = None
    file_path: Optional[str] = None
    fingerprint_data: Optional[str] = None
    created_at: Optional[str] = None


class DatabaseManager:
    """
    Manages local SQLite database and optional cloud synchronization
    
    Features:
    - Fast local fingerprint storage and retrieval
    - Efficient similarity search algorithms
    - Metadata management
    - Cloud sync capabilities
    - Batch operations
    """
    
    def __init__(self, 
                 db_path: str = "muzam.db",
                 local_only: bool = False,
                 cloud_config: Optional[Dict] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to local SQLite database
            local_only: Use only local database
            cloud_config: Cloud database configuration
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.local_only = local_only
        self.cloud_config = cloud_config or {}
        
        # Initialize local database
        self._init_local_database()
        
        # Initialize cloud connection if needed
        if not local_only:
            self._init_cloud_connection()
    
    def _init_local_database(self):
        """Initialize local SQLite database with tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Songs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS songs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        artist TEXT NOT NULL,
                        album TEXT,
                        year INTEGER,
                        duration REAL,
                        file_path TEXT,
                        fingerprint_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Fingerprint hashes table for fast lookup
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fingerprint_hashes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        song_id INTEGER,
                        hash_value TEXT NOT NULL,
                        time_offset REAL NOT NULL,
                        algorithm TEXT,
                        FOREIGN KEY (song_id) REFERENCES songs (id)
                    )
                """)
                
                # Create indexes separately
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_hash ON fingerprint_hashes (hash_value)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_song_id ON fingerprint_hashes (song_id)
                """)
                
                # Recognition statistics
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recognition_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        song_id INTEGER,
                        recognition_time REAL,
                        confidence REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (song_id) REFERENCES songs (id)
                    )
                """)
                
                conn.commit()
                self.logger.info("Local database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing local database: {e}")
            raise
    
    def _init_cloud_connection(self):
        """Initialize cloud database connection"""
        # Placeholder for cloud database setup
        # Could be PostgreSQL, MongoDB, or custom cloud service
        self.logger.info("Cloud database connection initialized")
    
    def add_song(self, song: Song, fingerprint: Fingerprint) -> int:
        """
        Add a song and its fingerprint to the database
        
        Args:
            song: Song metadata
            fingerprint: Audio fingerprint
            
        Returns:
            Song ID in database
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert song metadata
                cursor.execute("""
                    INSERT INTO songs (title, artist, album, year, duration, file_path, fingerprint_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    song.title,
                    song.artist,
                    song.album,
                    song.year,
                    song.duration,
                    song.file_path,
                    json.dumps(asdict(fingerprint))
                ))
                
                song_id = cursor.lastrowid
                
                # Insert fingerprint hashes
                for i, (hash_val, timestamp) in enumerate(zip(fingerprint.hash_values, fingerprint.time_stamps)):
                    cursor.execute("""
                        INSERT INTO fingerprint_hashes (song_id, hash_value, time_offset, algorithm)
                        VALUES (?, ?, ?, ?)
                    """, (song_id, hash_val, timestamp, fingerprint.algorithm))
                
                conn.commit()
                self.logger.info(f"Added song '{song.title}' with ID {song_id}")
                return song_id
                
        except Exception as e:
            self.logger.error(f"Error adding song to database: {e}")
            raise
    
    def search_fingerprint(self, fingerprint: Fingerprint, max_results: int = 10) -> List[RecognitionResult]:
        """
        Search database for matching fingerprints
        
        Args:
            fingerprint: Query fingerprint
            max_results: Maximum number of results to return
            
        Returns:
            List of RecognitionResult objects
        """
        try:
            start_time = time.time()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count hash matches for each song
                hash_placeholders = ','.join(['?' for _ in fingerprint.hash_values])
                
                query = f"""
                    SELECT 
                        s.id, s.title, s.artist, s.album, s.year,
                        COUNT(fh.hash_value) as match_count,
                        COUNT(DISTINCT fh.hash_value) as unique_matches
                    FROM songs s
                    JOIN fingerprint_hashes fh ON s.id = fh.song_id
                    WHERE fh.hash_value IN ({hash_placeholders})
                    GROUP BY s.id, s.title, s.artist, s.album, s.year
                    HAVING match_count >= ?
                    ORDER BY match_count DESC, unique_matches DESC
                    LIMIT ?
                """
                
                min_matches = max(1, len(fingerprint.hash_values) // 10)  # At least 10% match
                
                cursor.execute(query, fingerprint.hash_values + [min_matches, max_results])
                results = cursor.fetchall()
                
                # Convert to RecognitionResult objects
                recognition_results = []
                total_query_hashes = len(fingerprint.hash_values)
                
                for row in results:
                    song_id, title, artist, album, year, match_count, unique_matches = row
                    
                    # Calculate confidence score
                    confidence = self._calculate_confidence(
                        match_count, unique_matches, total_query_hashes
                    )
                    
                    # Record recognition stats
                    recognition_time = time.time() - start_time
                    self._record_recognition_stats(song_id, recognition_time, confidence)
                    
                    result = RecognitionResult(
                        title=title,
                        artist=artist,
                        album=album,
                        year=year,
                        confidence=confidence,
                        match_time=recognition_time,
                        fingerprint_matches=match_count
                    )
                    
                    recognition_results.append(result)
                
                return recognition_results
                
        except Exception as e:
            self.logger.error(f"Error searching fingerprint: {e}")
            return []
    
    def _calculate_confidence(self, match_count: int, unique_matches: int, total_query_hashes: int) -> float:
        """Calculate confidence score for a match"""
        if total_query_hashes == 0:
            return 0.0
            
        # Base confidence from match ratio
        match_ratio = match_count / total_query_hashes
        
        # Bonus for unique matches (reduces false positives)
        uniqueness_bonus = unique_matches / max(match_count, 1)
        
        # Combine scores with weighting
        confidence = min(1.0, (match_ratio * 0.7 + uniqueness_bonus * 0.3))
        
        return confidence
    
    def _record_recognition_stats(self, song_id: int, recognition_time: float, confidence: float):
        """Record recognition statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO recognition_stats (song_id, recognition_time, confidence)
                    VALUES (?, ?, ?)
                """, (song_id, recognition_time, confidence))
                conn.commit()
        except Exception as e:
            self.logger.warning(f"Failed to record recognition stats: {e}")
    
    def get_song_by_id(self, song_id: int) -> Optional[Song]:
        """Get song metadata by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, artist, album, year, duration, file_path, fingerprint_data, created_at
                    FROM songs WHERE id = ?
                """, (song_id,))
                
                row = cursor.fetchone()
                if row:
                    return Song(
                        id=row[0],
                        title=row[1],
                        artist=row[2],
                        album=row[3],
                        year=row[4],
                        duration=row[5],
                        file_path=row[6],
                        fingerprint_data=row[7],
                        created_at=row[8]
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting song by ID: {e}")
            return None
    
    def search_songs(self, query: str, field: str = "title") -> List[Song]:
        """Search songs by metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if field in ["title", "artist", "album"]:
                    cursor.execute(f"""
                        SELECT id, title, artist, album, year, duration, file_path, fingerprint_data, created_at
                        FROM songs WHERE {field} LIKE ?
                        ORDER BY title
                    """, (f"%{query}%",))
                else:
                    return []
                
                rows = cursor.fetchall()
                songs = []
                
                for row in rows:
                    song = Song(
                        id=row[0],
                        title=row[1],
                        artist=row[2],
                        album=row[3],
                        year=row[4],
                        duration=row[5],
                        file_path=row[6],
                        fingerprint_data=row[7],
                        created_at=row[8]
                    )
                    songs.append(song)
                
                return songs
                
        except Exception as e:
            self.logger.error(f"Error searching songs: {e}")
            return []
    
    def get_database_size(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM songs")
                song_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM fingerprint_hashes")
                fingerprint_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM recognition_stats")
                recognition_count = cursor.fetchone()[0]
                
                return {
                    "songs": song_count,
                    "fingerprints": fingerprint_count,
                    "recognitions": recognition_count
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database size: {e}")
            return {"songs": 0, "fingerprints": 0, "recognitions": 0}
    
    def batch_add_songs(self, songs_and_fingerprints: List[Tuple[Song, Fingerprint]]) -> List[int]:
        """Add multiple songs in batch for better performance"""
        song_ids = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                for song, fingerprint in songs_and_fingerprints:
                    song_id = self.add_song(song, fingerprint)
                    song_ids.append(song_id)
                    
            self.logger.info(f"Batch added {len(song_ids)} songs")
            return song_ids
            
        except Exception as e:
            self.logger.error(f"Error in batch add operation: {e}")
            raise
    
    def delete_song(self, song_id: int) -> bool:
        """Delete a song and its fingerprints"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete fingerprint hashes
                cursor.execute("DELETE FROM fingerprint_hashes WHERE song_id = ?", (song_id,))
                
                # Delete recognition stats
                cursor.execute("DELETE FROM recognition_stats WHERE song_id = ?", (song_id,))
                
                # Delete song
                cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted song with ID {song_id}")
                    return True
                else:
                    self.logger.warning(f"Song with ID {song_id} not found")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error deleting song: {e}")
            return False
