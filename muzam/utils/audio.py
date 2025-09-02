"""
Audio Processing Utilities

High-performance audio processing functions for MUZAM
"""

import numpy as np
import librosa
import sounddevice as sd
from typing import Tuple, Optional
import logging
from pathlib import Path


class AudioProcessor:
    """
    High-performance audio processing utilities

    Features:
    - Multi-format audio loading
    - Real-time microphone capture
    - Audio normalization and enhancement
    - Noise reduction
    - Format conversion
    """

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio processor

        Args:
            sample_rate: Target sample rate for processing
        """
        self.logger = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.supported_formats = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"]

    def load_audio(
        self, file_path: str, offset: float = 0.0, duration: Optional[float] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Load audio file with automatic format detection

        Args:
            file_path: Path to audio file
            offset: Start time in seconds
            duration: Duration to load in seconds

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")

            if file_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported audio format: {file_path.suffix}")

            # Load with librosa (handles most formats)
            audio_data, sr = librosa.load(
                str(file_path),
                sr=self.sample_rate,
                offset=offset,
                duration=duration,
                mono=True,  # Convert to mono
            )

            # Normalize audio
            audio_data = self._normalize_audio(audio_data)

            self.logger.debug(
                f"Loaded audio: {file_path.name}, duration: {len(audio_data)/sr:.2f}s"
            )

            return audio_data, sr

        except Exception as e:
            self.logger.error(f"Error loading audio file {file_path}: {e}")
            raise

    def record_from_microphone(
        self, duration: int, device: Optional[int] = None
    ) -> np.ndarray:
        """
        Record audio from microphone

        Args:
            duration: Recording duration in seconds
            device: Audio device ID (None for default)

        Returns:
            Recorded audio data
        """
        try:
            self.logger.info(f"Recording from microphone for {duration} seconds...")

            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,  # Mono
                device=device,
                dtype=np.float32,
            )

            # Wait for recording to complete
            sd.wait()

            # Convert to 1D array and normalize
            audio_data = audio_data.flatten()
            audio_data = self._normalize_audio(audio_data)

            self.logger.info("Recording completed successfully")

            return audio_data

        except Exception as e:
            self.logger.error(f"Error recording from microphone: {e}")
            raise

    def save_audio(
        self, audio_data: np.ndarray, file_path: str, sample_rate: Optional[int] = None
    ) -> bool:
        """
        Save audio data to file

        Args:
            audio_data: Audio data to save
            file_path: Output file path
            sample_rate: Sample rate (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            if sample_rate is None:
                sample_rate = self.sample_rate

            # Use soundfile for saving (supports multiple formats)
            import soundfile as sf

            sf.write(file_path, audio_data, sample_rate)
            self.logger.info(f"Audio saved to {file_path}")

            return True

        except ImportError:
            # Fallback to librosa
            try:
                librosa.output.write_wav(file_path, audio_data, sample_rate)
                return True
            except Exception as e:
                self.logger.error(f"Error saving audio: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Error saving audio: {e}")
            return False

    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio data

        Args:
            audio_data: Input audio data

        Returns:
            Normalized audio data
        """
        # Remove DC offset
        audio_data = audio_data - np.mean(audio_data)

        # Normalize to [-1, 1] range
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val

        return audio_data

    def apply_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply basic noise reduction

        Args:
            audio_data: Input audio data

        Returns:
            Noise-reduced audio data
        """
        try:
            # Simple spectral gating approach
            # Calculate spectral magnitude
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)

            # Estimate noise floor (bottom 10% of spectrum)
            noise_floor = np.percentile(magnitude, 10, axis=1, keepdims=True)

            # Apply spectral gating
            gate_threshold = noise_floor * 2.0  # 6dB above noise floor
            mask = magnitude > gate_threshold

            # Apply mask
            stft_clean = stft * mask

            # Convert back to time domain
            audio_clean = librosa.istft(stft_clean)

            return self._normalize_audio(audio_clean)

        except Exception as e:
            self.logger.warning(f"Noise reduction failed: {e}")
            return audio_data  # Return original if processing fails

    def trim_silence(
        self, audio_data: np.ndarray, threshold: float = 0.01
    ) -> np.ndarray:
        """
        Trim silence from beginning and end of audio

        Args:
            audio_data: Input audio data
            threshold: Silence threshold (0-1)

        Returns:
            Trimmed audio data
        """
        try:
            # Find non-silent regions
            trimmed_audio, _ = librosa.effects.trim(
                audio_data, top_db=int(-20 * np.log10(threshold))  # Convert to dB
            )

            return trimmed_audio

        except Exception as e:
            self.logger.warning(f"Silence trimming failed: {e}")
            return audio_data

    def resample_audio(
        self, audio_data: np.ndarray, orig_sr: int, target_sr: int
    ) -> np.ndarray:
        """
        Resample audio to target sample rate

        Args:
            audio_data: Input audio data
            orig_sr: Original sample rate
            target_sr: Target sample rate

        Returns:
            Resampled audio data
        """
        try:
            if orig_sr == target_sr:
                return audio_data

            resampled = librosa.resample(
                audio_data, orig_sr=orig_sr, target_sr=target_sr
            )
            return resampled

        except Exception as e:
            self.logger.error(f"Resampling failed: {e}")
            return audio_data

    def convert_to_mono(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Convert stereo audio to mono

        Args:
            audio_data: Input audio data (may be stereo)

        Returns:
            Mono audio data
        """
        if audio_data.ndim == 1:
            return audio_data  # Already mono
        elif audio_data.ndim == 2:
            # Average the channels
            return np.mean(audio_data, axis=0)
        else:
            raise ValueError("Audio data must be 1D or 2D")

    def get_audio_info(self, file_path: str) -> dict:
        """
        Get audio file information without loading the full file

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with audio information
        """
        try:
            import soundfile as sf

            with sf.SoundFile(file_path) as f:
                info = {
                    "duration": len(f) / f.samplerate,
                    "sample_rate": f.samplerate,
                    "channels": f.channels,
                    "format": f.format,
                    "subtype": f.subtype,
                    "frames": len(f),
                }

            return info

        except ImportError:
            # Fallback using librosa
            try:
                duration = librosa.get_duration(filename=file_path)
                info = {
                    "duration": duration,
                    "sample_rate": "unknown",
                    "channels": "unknown",
                    "format": "unknown",
                }
                return info
            except Exception as e:
                self.logger.error(f"Error getting audio info: {e}")
                return {}
        except Exception as e:
            self.logger.error(f"Error getting audio info: {e}")
            return {}

    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate if file is a supported audio format

        Args:
            file_path: Path to audio file

        Returns:
            True if valid audio file, False otherwise
        """
        try:
            file_path = Path(file_path)

            # Check extension
            if file_path.suffix.lower() not in self.supported_formats:
                return False

            # Try to get basic info
            info = self.get_audio_info(str(file_path))
            return bool(info)

        except Exception:
            return False

    def list_audio_devices(self) -> dict:
        """
        List available audio input devices

        Returns:
            Dictionary of available devices
        """
        try:
            devices = sd.query_devices()
            input_devices = {}

            for i, device in enumerate(devices):
                if device["max_input_channels"] > 0:
                    input_devices[i] = {
                        "name": device["name"],
                        "channels": device["max_input_channels"],
                        "sample_rate": device["default_samplerate"],
                    }

            return input_devices

        except Exception as e:
            self.logger.error(f"Error listing audio devices: {e}")
            return {}
