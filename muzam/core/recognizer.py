"""
Core Audio Recognition Engine

Handles the main audio recognition pipeline with advanced fingerprinting
and matching algorithms.
"""

import numpy as np
import librosa
import asyncio
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import logging

from ..models import RecognitionResult
from ..fingerprint.generator import FingerprintGenerator
from ..ml.enhancer import MLEnhancer
from ..utils.audio import AudioProcessor


class AudioRecognizer:
    """
    Main audio recognition engine
    
    Features:
    - Real-time audio processing
    - Multiple fingerprinting algorithms
    - ML-enhanced matching
    - Local and cloud database support
    """
    
    def __init__(self, 
                 config_path: Optional[Path] = None,
                 use_ml_enhancement: bool = True,
                 local_db_only: bool = False):
        """
        Initialize the audio recognizer
        
        Args:
            config_path: Path to configuration file
            use_ml_enhancement: Enable ML-based enhancement
            local_db_only: Use only local database (no cloud)
        """
        self.logger = logging.getLogger(__name__)
        
        # Import here to avoid circular imports
        from ..database.manager import DatabaseManager
        
        # Initialize components
        self.fingerprint_generator = FingerprintGenerator()
        self.database_manager = DatabaseManager(local_only=local_db_only)
        self.audio_processor = AudioProcessor()
        
        if use_ml_enhancement:
            self.ml_enhancer = MLEnhancer()
        else:
            self.ml_enhancer = None
            
        self.config = self._load_config(config_path)
        
    def identify_file(self, file_path: str) -> Optional[RecognitionResult]:
        """
        Identify a song from an audio file
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            RecognitionResult if match found, None otherwise
        """
        try:
            # Load and preprocess audio
            audio_data, sample_rate = self.audio_processor.load_audio(file_path)
            
            # Generate fingerprint
            fingerprint = self.fingerprint_generator.generate(audio_data, sample_rate)
            
            # Search database
            matches = self.database_manager.search_fingerprint(fingerprint)
            
            if not matches:
                return None
                
            # Enhance with ML if available
            if self.ml_enhancer:
                matches = self.ml_enhancer.enhance_matches(matches, audio_data)
            
            # Return best match
            best_match = max(matches, key=lambda x: x.confidence)
            return best_match
            
        except Exception as e:
            self.logger.error(f"Error identifying file {file_path}: {e}")
            return None
    
    async def identify_stream(self, audio_stream) -> Optional[RecognitionResult]:
        """
        Identify a song from real-time audio stream
        
        Args:
            audio_stream: Real-time audio data stream
            
        Returns:
            RecognitionResult if match found, None otherwise
        """
        # Buffer audio data
        buffer = []
        
        async for chunk in audio_stream:
            buffer.append(chunk)
            
            # Process when we have enough data (3-5 seconds)
            if len(buffer) >= self.config.get('min_buffer_size', 5):
                audio_data = np.concatenate(buffer)
                result = await self._process_audio_async(audio_data)
                
                if result and result.confidence > self.config.get('min_confidence', 0.7):
                    return result
                    
                # Slide the buffer
                buffer = buffer[1:]
        
        return None
    
    def listen_and_identify(self, duration: int = 10) -> Optional[RecognitionResult]:
        """
        Listen to microphone and identify song
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            RecognitionResult if match found, None otherwise
        """
        try:
            # Record from microphone
            audio_data = self.audio_processor.record_from_microphone(duration)
            
            # Generate fingerprint
            fingerprint = self.fingerprint_generator.generate(
                audio_data, 
                self.audio_processor.sample_rate
            )
            
            # Search and return result
            matches = self.database_manager.search_fingerprint(fingerprint)
            
            if matches:
                if self.ml_enhancer:
                    matches = self.ml_enhancer.enhance_matches(matches, audio_data)
                return max(matches, key=lambda x: x.confidence)
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error during microphone recognition: {e}")
            return None
    
    def batch_identify(self, file_paths: List[str]) -> List[Tuple[str, Optional[RecognitionResult]]]:
        """
        Identify multiple files in batch
        
        Args:
            file_paths: List of audio file paths
            
        Returns:
            List of (file_path, result) tuples
        """
        results = []
        
        for file_path in file_paths:
            result = self.identify_file(file_path)
            results.append((file_path, result))
            
        return results
    
    async def _process_audio_async(self, audio_data: np.ndarray) -> Optional[RecognitionResult]:
        """Process audio data asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run fingerprinting in thread pool
        fingerprint = await loop.run_in_executor(
            None, 
            self.fingerprint_generator.generate,
            audio_data,
            self.audio_processor.sample_rate
        )
        
        # Search database
        matches = await loop.run_in_executor(
            None,
            self.database_manager.search_fingerprint,
            fingerprint
        )
        
        if matches:
            return max(matches, key=lambda x: x.confidence)
        return None
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'min_buffer_size': 5,
            'min_confidence': 0.7,
            'max_recognition_time': 30,
            'fingerprint_algorithm': 'chromaprint',
            'ml_enhancement': True
        }
        
        if config_path and config_path.exists():
            # Load from file (JSON/YAML)
            # Implementation depends on chosen format
            pass
            
        return default_config
    
    def get_stats(self) -> Dict:
        """Get recognition statistics"""
        return {
            'total_recognitions': getattr(self, '_total_recognitions', 0),
            'successful_matches': getattr(self, '_successful_matches', 0),
            'average_recognition_time': getattr(self, '_avg_recognition_time', 0.0),
            'database_size': self.database_manager.get_database_size()
        }
