"""
FastAPI Web Application for MUZAM

Provides a modern web interface and REST API for audio recognition
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import os
import asyncio
import logging

from ..core.recognizer import AudioRecognizer, RecognitionResult
from ..database.manager import DatabaseManager, Song
from ..utils.audio import load_audio, record_audio
from ..utils.audio import AudioProcessor


# Pydantic models for API
class RecognitionResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None
    processing_time: float


class SongInfo(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    year: Optional[int] = None


class DatabaseStats(BaseModel):
    total_songs: int
    total_fingerprints: int
    total_recognitions: int


# Initialize FastAPI app
app = FastAPI(
    title="MUZAM API",
    description="Open Source Audio Recognition - Better than Shazam",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MUZAM components
recognizer = AudioRecognizer()
logger = logging.getLogger(__name__)

# Templates and static files
templates = Jinja2Templates(directory="muzam/web/templates")
app.mount("/static", StaticFiles(directory="muzam/web/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MUZAM - GhostKitty Audio Recognition</title>
        
        <!-- Stylesheets -->
        <link rel="stylesheet" href="/static/style.css">
        
        <!-- Favicon -->
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>👻</text></svg>">
        
        <!-- Meta tags -->
        <meta name="description" content="MUZAM - Open Source Audio Recognition Engine powered by GhostKitty">
        <meta name="author" content="MUZAM Community">
        <meta name="keywords" content="audio recognition, music identification, open source, privacy">
        
        <!-- Open Graph -->
        <meta property="og:title" content="MUZAM - GhostKitty Audio Recognition">
        <meta property="og:description" content="Open Source Audio Recognition - Better than Shazam">
        <meta property="og:type" content="website">
        
        <!-- Preload critical fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    </head>
    <body>
        <!-- Animated Background -->
        <div class="bg-animated"></div>
        
        <!-- Main Container -->
        <div class="container">
            <!-- Header Section -->
            <header class="header">
                <div class="logo-container">
                    <div class="ghost-kitty">👻🐱</div>
                    <h1 class="title">MUZAM</h1>
                    <p class="subtitle">GhostKitty Audio Recognition</p>
                    <p class="tagline">Open Source • Privacy-First • Lightning Fast</p>
                </div>
            </header>
            
            <!-- Upload Zone -->
            <section class="upload-zone" tabindex="0" role="button" aria-label="Upload audio file">
                <div class="upload-icon">🎵</div>
                <h3 class="upload-text">Drop your beats here or click to select</h3>
                <p class="upload-subtext">Supports MP3, WAV, FLAC, M4A, OGG • Max 50MB</p>
                <input type="file" id="audioFile" accept=".mp3,.wav,.flac,.m4a,.ogg,.aac" hidden>
            </section>
            
            <!-- Action Buttons -->
            <section class="actions">
                <button class="btn btn-primary" onclick="startMicrophoneRecording()" title="Record from microphone (Ctrl+R)">
                    🎙️ Listen Mode
                </button>
                <button class="btn btn-secondary" onclick="stopRecording()" id="stopBtn" style="display:none;" title="Stop recording">
                    ⏹️ Stop Recording
                </button>
                <button class="btn btn-secondary" onclick="document.getElementById('audioFile').click()" title="Upload file (Ctrl+U)">
                    📁 Upload File
                </button>
            </section>
            
            <!-- Loading Animation -->
            <section class="loading hidden" id="loading">
                <div class="loading-spinner"></div>
                <h3 class="loading-text">Analyzing your sick beats...</h3>
                <p class="loading-subtext">GhostKitty is working its magic... 👻</p>
            </section>
            
            <!-- Results Section -->
            <section class="result hidden" id="result">
                <div id="resultContent">
                    <!-- Results will be populated by JavaScript -->
                </div>
            </section>
            
            <!-- Features Grid -->
            <section class="features">
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <h4 class="feature-title">Lightning Fast</h4>
                    <p class="feature-description">Sub-second recognition with GhostKitty's advanced algorithms</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🛡️</div>
                    <h4 class="feature-title">Privacy Ghost</h4>
                    <p class="feature-description">Local processing means your data never leaves your device</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <h4 class="feature-title">Deadly Accurate</h4>
                    <p class="feature-description">ML-enhanced matching for superior recognition accuracy</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🌐</div>
                    <h4 class="feature-title">Open Source Spirit</h4>
                    <p class="feature-description">Community-driven, fully customizable, and completely free</p>
                </div>
            </section>
            
            <!-- Statistics -->
            <section class="stats" id="stats">
                <div class="stat">
                    <div class="stat-value" id="totalSongs">-</div>
                    <div class="stat-label">Tracks in Database</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="totalRecognitions">-</div>
                    <div class="stat-label">Total Recognitions</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="accuracy">-</div>
                    <div class="stat-label">Ghost Accuracy</div>
                </div>
            </section>
            
            <!-- Footer -->
            <footer class="text-center" style="margin-top: 4rem; padding: 2rem; color: #666;">
                <p>🎵 <strong>MUZAM</strong> - Powered by GhostKitty Magic</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">
                    Open Source • MIT License • Community Driven
                </p>
                <p style="font-size: 0.8rem; margin-top: 1rem; opacity: 0.7;">
                    Keyboard Shortcuts: <kbd>Ctrl+U</kbd> Upload • <kbd>Ctrl+R</kbd> Record
                </p>
            </footer>
        </div>
        
        <!-- Scripts -->
        <script src="/static/app.js"></script>
        
        <!-- Service Worker for PWA -->
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js').catch(console.error);
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/recognize/file", response_model=RecognitionResponse)
async def recognize_audio_file(audio_file: UploadFile = File(...)):
    """
    Recognize song from uploaded audio file

    Args:
        audio_file: Uploaded audio file

    Returns:
        Recognition result with song information
    """
    start_time = asyncio.get_event_loop().time()

    try:
        # Validate file type
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="File must be an audio file")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Recognize the audio
            result = recognizer.identify_file(temp_file_path)
            processing_time = asyncio.get_event_loop().time() - start_time

            if result:
                return RecognitionResponse(
                    success=True,
                    result={
                        "title": result.title,
                        "artist": result.artist,
                        "album": result.album,
                        "year": result.year,
                        "confidence": result.confidence,
                        "match_time": result.match_time,
                        "fingerprint_matches": result.fingerprint_matches,
                    },
                    processing_time=processing_time,
                )
            else:
                return RecognitionResponse(
                    success=False,
                    error="No matching song found",
                    processing_time=processing_time,
                )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error recognizing audio file: {e}")
        processing_time = asyncio.get_event_loop().time() - start_time
        return RecognitionResponse(
            success=False, error=str(e), processing_time=processing_time
        )


@app.post("/api/recognize/microphone", response_model=RecognitionResponse)
async def recognize_from_microphone(duration: int = 10):
    """
    Recognize song from microphone recording

    Args:
        duration: Recording duration in seconds (max 30)

    Returns:
        Recognition result
    """
    start_time = asyncio.get_event_loop().time()

    try:
        # Limit duration for server resources
        duration = min(duration, 30)

        # Record from microphone
        audio_data = recognizer.listen_and_identify(duration)
        processing_time = asyncio.get_event_loop().time() - start_time

        if audio_data:
            return RecognitionResponse(
                success=True,
                result={
                    "title": audio_data.title,
                    "artist": audio_data.artist,
                    "album": audio_data.album,
                    "year": audio_data.year,
                    "confidence": audio_data.confidence,
                    "match_time": audio_data.match_time,
                    "fingerprint_matches": audio_data.fingerprint_matches,
                },
                processing_time=processing_time,
            )
        else:
            return RecognitionResponse(
                success=False,
                error="No matching song found",
                processing_time=processing_time,
            )

    except Exception as e:
        logger.error(f"Error with microphone recognition: {e}")
        processing_time = asyncio.get_event_loop().time() - start_time
        return RecognitionResponse(
            success=False, error=str(e), processing_time=processing_time
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "service": "MUZAM GhostKitty Audio Recognition",
        "version": "1.0.0",
        "timestamp": "2025-09-02",
    }


@app.get("/api/stats", response_model=DatabaseStats)
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = recognizer.database_manager.get_database_size()
        return DatabaseStats(
            total_songs=stats.get("songs", 0),
            total_fingerprints=stats.get("fingerprints", 0),
            total_recognitions=stats.get("recognitions", 0),
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return DatabaseStats(total_songs=0, total_fingerprints=0, total_recognitions=0)


@app.post("/api/songs/add")
async def add_song_to_database(song_info: SongInfo, audio_file: UploadFile = File(...)):
    """
    Add a new song to the database

    Args:
        song_info: Song metadata
        audio_file: Audio file to fingerprint

    Returns:
        Success status and song ID
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Load and process audio
            audio_data, sample_rate = load_audio(temp_file_path)

            # Generate fingerprint
            fingerprint = recognizer.fingerprint_generator.generate(
                audio_data, sample_rate
            )

            # Create song object
            song = Song(
                title=song_info.title,
                artist=song_info.artist,
                album=song_info.album,
                year=song_info.year,
                duration=len(audio_data) / sample_rate,
                file_path=audio_file.filename,
            )

            # Add to database
            song_id = recognizer.database_manager.add_song(song, fingerprint)

            return {
                "success": True,
                "song_id": song_id,
                "message": "Song added successfully",
            }

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error adding song: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/songs/search")
async def search_songs(query: str, field: str = "title"):
    """
    Search songs in database

    Args:
        query: Search query
        field: Field to search in (title, artist, album)

    Returns:
        List of matching songs
    """
    try:
        songs = recognizer.database_manager.search_songs(query, field)
        return {
            "success": True,
            "results": [
                {
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist,
                    "album": song.album,
                    "year": song.year,
                    "duration": song.duration,
                }
                for song in songs
            ],
        }
    except Exception as e:
        logger.error(f"Error searching songs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MUZAM Audio Recognition API",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
