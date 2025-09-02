"""
Audio Fingerprint Generator

Advanced fingerprinting algorithms for audio recognition including:
- Chromaprint (AcoustID)
- Custom spectral fingerprints
- Mel-frequency cepstral coefficients (MFCC)
- Chroma features
"""

import numpy as np
import librosa
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class Fingerprint:
    """Audio fingerprint data structure"""
    hash_values: List[str]
    time_stamps: List[float]
    confidence: float
    algorithm: str
    duration: float
    sample_rate: int


class FingerprintGenerator:
    """
    Generate audio fingerprints using multiple algorithms
    
    Combines traditional methods with custom enhancements for
    superior recognition accuracy
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Default parameters
        self.hop_length = 512
        self.n_fft = 2048
        self.window_size = 4096
        self.overlap = 0.5
        
    def generate(self, audio_data: np.ndarray, sample_rate: int) -> Fingerprint:
        """
        Generate comprehensive fingerprint from audio data
        
        Args:
            audio_data: Audio signal as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Fingerprint object containing all hash data
        """
        try:
            # Normalize audio
            audio_data = self._normalize_audio(audio_data)
            
            # Generate multiple fingerprint types
            chromaprint_hashes = self._generate_chromaprint(audio_data, sample_rate)
            spectral_hashes = self._generate_spectral_fingerprint(audio_data, sample_rate)
            mfcc_hashes = self._generate_mfcc_fingerprint(audio_data, sample_rate)
            
            # Combine all hashes
            all_hashes = chromaprint_hashes + spectral_hashes + mfcc_hashes
            
            # Generate timestamps
            timestamps = self._generate_timestamps(len(all_hashes), len(audio_data), sample_rate)
            
            return Fingerprint(
                hash_values=all_hashes,
                time_stamps=timestamps,
                confidence=self._calculate_fingerprint_confidence(all_hashes),
                algorithm="hybrid",
                duration=len(audio_data) / sample_rate,
                sample_rate=sample_rate
            )
            
        except Exception as e:
            self.logger.error(f"Error generating fingerprint: {e}")
            raise
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio to optimal range"""
        # Remove DC offset
        audio_data = audio_data - np.mean(audio_data)
        
        # Normalize amplitude
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
            
        return audio_data
    
    def _generate_chromaprint(self, audio_data: np.ndarray, sample_rate: int) -> List[str]:
        """Generate chromaprint-style fingerprint"""
        # Calculate chroma features
        chroma = librosa.feature.chroma_stft(
            y=audio_data,
            sr=sample_rate,
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        
        # Generate hash sequences
        hashes = []
        for i in range(chroma.shape[1] - 1):
            # Create feature vector from adjacent frames
            features = np.concatenate([chroma[:, i], chroma[:, i + 1]])
            
            # Convert to binary hash
            hash_val = self._features_to_hash(features)
            hashes.append(hash_val)
            
        return hashes
    
    def _generate_spectral_fingerprint(self, audio_data: np.ndarray, sample_rate: int) -> List[str]:
        """Generate spectral-based fingerprint"""
        # Calculate spectral features
        spectral_centroids = librosa.feature.spectral_centroid(
            y=audio_data, sr=sample_rate, hop_length=self.hop_length
        )[0]
        
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio_data, sr=sample_rate, hop_length=self.hop_length
        )[0]
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio_data, sr=sample_rate, hop_length=self.hop_length
        )[0]
        
        # Combine features and generate hashes
        hashes = []
        min_len = min(len(spectral_centroids), len(spectral_rolloff), len(spectral_bandwidth))
        
        for i in range(min_len - 1):
            features = np.array([
                spectral_centroids[i], spectral_centroids[i + 1],
                spectral_rolloff[i], spectral_rolloff[i + 1],
                spectral_bandwidth[i], spectral_bandwidth[i + 1]
            ])
            
            hash_val = self._features_to_hash(features)
            hashes.append(hash_val)
            
        return hashes
    
    def _generate_mfcc_fingerprint(self, audio_data: np.ndarray, sample_rate: int) -> List[str]:
        """Generate MFCC-based fingerprint"""
        # Calculate MFCC features
        mfccs = librosa.feature.mfcc(
            y=audio_data,
            sr=sample_rate,
            n_mfcc=13,
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        
        # Generate delta features
        delta_mfccs = librosa.feature.delta(mfccs)
        
        # Combine and hash
        hashes = []
        for i in range(mfccs.shape[1] - 1):
            features = np.concatenate([
                mfccs[:, i],
                mfccs[:, i + 1],
                delta_mfccs[:, i],
                delta_mfccs[:, i + 1]
            ])
            
            hash_val = self._features_to_hash(features)
            hashes.append(hash_val)
            
        return hashes
    
    def _features_to_hash(self, features: np.ndarray) -> str:
        """Convert feature vector to hash string"""
        # Normalize features
        features = (features - np.mean(features)) / (np.std(features) + 1e-8)
        
        # Quantize to binary
        binary_features = (features > 0).astype(int)
        
        # Convert to hex hash
        binary_string = ''.join(binary_features.astype(str))
        hash_object = hashlib.md5(binary_string.encode())
        return hash_object.hexdigest()[:16]  # Use first 16 characters
    
    def _generate_timestamps(self, num_hashes: int, audio_length: int, sample_rate: int) -> List[float]:
        """Generate timestamps for each hash"""
        duration = audio_length / sample_rate
        time_step = duration / num_hashes
        return [i * time_step for i in range(num_hashes)]
    
    def _calculate_fingerprint_confidence(self, hashes: List[str]) -> float:
        """Calculate confidence score for fingerprint quality"""
        if not hashes:
            return 0.0
            
        # Calculate uniqueness ratio
        unique_hashes = len(set(hashes))
        total_hashes = len(hashes)
        uniqueness = unique_hashes / total_hashes
        
        # Factor in total number of hashes
        coverage = min(1.0, total_hashes / 100)  # Optimal ~100 hashes
        
        return (uniqueness * 0.7 + coverage * 0.3)
    
    def compare_fingerprints(self, fp1: Fingerprint, fp2: Fingerprint) -> float:
        """
        Compare two fingerprints and return similarity score
        
        Args:
            fp1, fp2: Fingerprint objects to compare
            
        Returns:
            Similarity score between 0 and 1
        """
        if not fp1.hash_values or not fp2.hash_values:
            return 0.0
            
        # Convert to sets for intersection
        set1 = set(fp1.hash_values)
        set2 = set(fp2.hash_values)
        
        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
            
        return intersection / union
