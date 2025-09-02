"""
Data Models for MUZAM

Common data structures used throughout the application
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class RecognitionResult:
    """Result of audio recognition"""
    title: str
    artist: str
    album: Optional[str] = None
    year: Optional[int] = None
    confidence: float = 0.0
    match_time: float = 0.0
    fingerprint_matches: int = 0
    metadata: Dict = None
