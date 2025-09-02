"""
MUZAM - Open Source Audio Recognition Engine
Better than Shazam

A powerful, privacy-first audio recognition system with local processing,
machine learning enhancement, and superior accuracy.
"""

__version__ = "1.0.0"
__author__ = "MUZAM Community"
__license__ = "MIT"

from .core.recognizer import AudioRecognizer
from .fingerprint.generator import FingerprintGenerator as AudioFingerprinter
from .database.manager import DatabaseManager
from .models import RecognitionResult

__all__ = ["AudioRecognizer", "AudioFingerprinter", "DatabaseManager", "RecognitionResult"]
