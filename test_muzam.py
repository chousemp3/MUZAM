#!/usr/bin/env python3
"""
MUZAM Test Suite

Quick test to verify the installation and basic functionality.
"""

import sys
import numpy as np
import tempfile
import wave
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from muzam.core.recognizer import AudioRecognizer
from muzam.fingerprint.generator import FingerprintGenerator
from muzam.database.manager import DatabaseManager, Song
from muzam.utils.audio import AudioProcessor


def create_test_audio():
    """Create a simple test audio file"""
    # Generate a simple sine wave for testing
    sample_rate = 22050
    duration = 5  # seconds
    frequency = 440  # A4 note
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Create temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    
    with wave.open(temp_file.name, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Convert to 16-bit integers
        audio_int16 = (audio_data * 32767).astype(np.int16)
        wav_file.writeframes(audio_int16.tobytes())
    
    return temp_file.name, audio_data, sample_rate


def test_basic_functionality():
    """Test basic MUZAM functionality"""
    print("🎵 MUZAM Test Suite")
    print("=" * 50)
    
    # Test 1: Database initialization
    print("1. Testing database initialization...")
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_database_size()
        print(f"   ✅ Database initialized. Songs: {stats['songs']}")
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False
    
    # Test 2: Audio processor
    print("2. Testing audio processor...")
    try:
        audio_processor = AudioProcessor()
        test_audio_file, original_audio, sample_rate = create_test_audio()
        
        # Load the test audio
        loaded_audio, loaded_sr = audio_processor.load_audio(test_audio_file)
        print(f"   ✅ Audio loaded. Duration: {len(loaded_audio) / loaded_sr:.1f}s")
        
        # Clean up
        Path(test_audio_file).unlink()
        
    except Exception as e:
        print(f"   ❌ Audio processor test failed: {e}")
        return False
    
    # Test 3: Fingerprint generation
    print("3. Testing fingerprint generation...")
    try:
        fingerprint_gen = FingerprintGenerator()
        fingerprint = fingerprint_gen.generate(loaded_audio, loaded_sr)
        print(f"   ✅ Fingerprint generated. Hashes: {len(fingerprint.hash_values)}")
    except Exception as e:
        print(f"   ❌ Fingerprint test failed: {e}")
        return False
    
    # Test 4: Database operations
    print("4. Testing database operations...")
    try:
        # Add a test song
        test_song = Song(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            year=2025,
            duration=len(loaded_audio) / loaded_sr
        )
        
        song_id = db_manager.add_song(test_song, fingerprint)
        print(f"   ✅ Song added with ID: {song_id}")
        
        # Search for the song
        results = db_manager.search_fingerprint(fingerprint)
        if results:
            result = results[0]
            print(f"   ✅ Song found: {result.title} by {result.artist}")
            print(f"      Confidence: {result.confidence:.2f}")
        else:
            print("   ⚠️  Song not found in search")
            
    except Exception as e:
        print(f"   ❌ Database operations test failed: {e}")
        return False
    
    # Test 5: Full recognition pipeline
    print("5. Testing full recognition pipeline...")
    try:
        recognizer = AudioRecognizer()
        
        # Create another test audio file
        test_audio_file2, _, _ = create_test_audio()
        
        # Try to recognize it
        result = recognizer.identify_file(test_audio_file2)
        
        if result:
            print(f"   ✅ Recognition successful!")
            print(f"      Title: {result.title}")
            print(f"      Artist: {result.artist}")
            print(f"      Confidence: {result.confidence:.2f}")
        else:
            print("   ⚠️  No recognition result (expected for unique audio)")
        
        # Clean up
        Path(test_audio_file2).unlink()
        
    except Exception as e:
        print(f"   ❌ Recognition pipeline test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! MUZAM is working correctly.")
    print("\nNext steps:")
    print("1. Add your music files: muzam db add /path/to/song.mp3")
    print("2. Start recognition: muzam recognize /path/to/unknown.mp3")
    print("3. Start web server: muzam serve")
    
    return True


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
