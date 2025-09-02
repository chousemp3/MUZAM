#!/usr/bin/env python3
"""
MUZAM Command Line Interface

A powerful CLI for audio recognition and database management
"""

import click
import asyncio
import sys
import time
from pathlib import Path
from typing import List, Optional
import logging

# Try to import rich for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

from ..core.recognizer import AudioRecognizer
from ..database.manager import DatabaseManager, Song
from ..utils.audio import AudioProcessor
from ..fingerprint.generator import FingerprintGenerator


class MuzamCLI:
    """Main CLI class for MUZAM operations"""

    def __init__(self):
        self.recognizer = AudioRecognizer()
        self.audio_processor = AudioProcessor()
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def print_banner(self):
        """Print MUZAM banner"""
        banner = """
        🎵 MUZAM - Open Source Audio Recognition 🎵
        ============================================
        Better than Shazam • Privacy-First • Lightning Fast
        """

        if RICH_AVAILABLE:
            console.print(Panel(banner, style="bold magenta"))
        else:
            print(banner)

    def print_result(self, result, processing_time: float = 0.0):
        """Print recognition result in a nice format"""
        if not result:
            if RICH_AVAILABLE:
                console.print("❌ [red]No match found[/red]")
            else:
                print("❌ No match found")
            return

        if RICH_AVAILABLE:
            table = Table(title="🎯 Recognition Result", show_header=False)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("🎵 Title", result.title)
            table.add_row("👤 Artist", result.artist)
            if result.album:
                table.add_row("💿 Album", result.album)
            if result.year:
                table.add_row("📅 Year", str(result.year))
            table.add_row("🎯 Confidence", f"{result.confidence * 100:.1f}%")
            table.add_row("⚡ Match Time", f"{result.match_time:.2f}s")
            if processing_time:
                table.add_row("🕐 Total Time", f"{processing_time:.2f}s")

            console.print(table)
        else:
            print(f"\n🎯 Recognition Result:")
            print(f"🎵 Title: {result.title}")
            print(f"👤 Artist: {result.artist}")
            if result.album:
                print(f"💿 Album: {result.album}")
            if result.year:
                print(f"📅 Year: {result.year}")
            print(f"🎯 Confidence: {result.confidence * 100:.1f}%")
            print(f"⚡ Match Time: {result.match_time:.2f}s")
            if processing_time:
                print(f"🕐 Total Time: {processing_time:.2f}s")


# Create CLI instance
cli = MuzamCLI()


@click.group()
@click.version_option(version="1.0.0", prog_name="MUZAM")
def main():
    """MUZAM - Open Source Audio Recognition Engine"""
    cli.print_banner()


@main.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def recognize(audio_file: str, verbose: bool):
    """
    Recognize a song from an audio file

    AUDIO_FILE: Path to the audio file to recognize
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    start_time = time.time()

    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔍 Analyzing audio...", total=None)
            result = cli.recognizer.identify_file(audio_file)
    else:
        print("🔍 Analyzing audio...")
        result = cli.recognizer.identify_file(audio_file)

    processing_time = time.time() - start_time
    cli.print_result(result, processing_time)


@main.command()
@click.option("--duration", "-d", default=10, help="Recording duration in seconds")
@click.option("--device", type=int, help="Audio device ID")
def listen(duration: int, device: Optional[int]):
    """
    Listen to microphone and identify song

    Records audio from microphone for the specified duration and identifies the song.
    """
    start_time = time.time()

    if RICH_AVAILABLE:
        console.print(f"🎤 [yellow]Recording for {duration} seconds...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔍 Listening and analyzing...", total=None)
            result = cli.recognizer.listen_and_identify(duration)
    else:
        print(f"🎤 Recording for {duration} seconds...")
        print("🔍 Listening and analyzing...")
        result = cli.recognizer.listen_and_identify(duration)

    processing_time = time.time() - start_time
    cli.print_result(result, processing_time)


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--recursive", "-r", is_flag=True, help="Search directories recursively")
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
def batch(files, recursive: bool, output: Optional[str]):
    """
    Recognize multiple audio files in batch

    FILES: One or more audio files or directories to process
    """
    file_list = []

    # Collect all files
    for file_path in files:
        path = Path(file_path)
        if path.is_file():
            file_list.append(str(path))
        elif path.is_dir() and recursive:
            for ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]:
                file_list.extend(str(f) for f in path.rglob(f"*{ext}"))

    if not file_list:
        if RICH_AVAILABLE:
            console.print("❌ [red]No audio files found[/red]")
        else:
            print("❌ No audio files found")
        return

    if RICH_AVAILABLE:
        console.print(f"🔍 Processing {len(file_list)} files...")

        with Progress(console=console) as progress:
            task = progress.add_task("Processing files...", total=len(file_list))

            results = []
            for file_path in file_list:
                result = cli.recognizer.identify_file(file_path)
                results.append((file_path, result))
                progress.advance(task)
    else:
        print(f"🔍 Processing {len(file_list)} files...")
        results = cli.recognizer.batch_identify(file_list)

    # Display results
    if RICH_AVAILABLE:
        table = Table(title="Batch Recognition Results")
        table.add_column("File", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Artist", style="yellow")
        table.add_column("Confidence", style="magenta")

        for file_path, result in results:
            filename = Path(file_path).name
            if result:
                table.add_row(
                    filename,
                    result.title,
                    result.artist,
                    f"{result.confidence * 100:.1f}%",
                )
            else:
                table.add_row(filename, "No match", "-", "-")

        console.print(table)
    else:
        print("\nBatch Recognition Results:")
        print("-" * 60)
        for file_path, result in results:
            filename = Path(file_path).name
            if result:
                print(
                    f"{filename}: {result.title} by {result.artist} ({result.confidence * 100:.1f}%)"
                )
            else:
                print(f"{filename}: No match")

    # Save to file if requested
    if output:
        with open(output, "w") as f:
            f.write("File,Title,Artist,Album,Year,Confidence\n")
            for file_path, result in results:
                if result:
                    f.write(
                        f'"{file_path}","{result.title}","{result.artist}","{result.album or ""}","{result.year or ""}",{result.confidence}\n'
                    )
                else:
                    f.write(f'"{file_path}","No match","","","",0.0\n')

        if RICH_AVAILABLE:
            console.print(f"✅ [green]Results saved to {output}[/green]")
        else:
            print(f"✅ Results saved to {output}")


@main.group()
def db():
    """Database management commands"""
    pass


@db.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option("--title", prompt=True, help="Song title")
@click.option("--artist", prompt=True, help="Artist name")
@click.option("--album", help="Album name")
@click.option("--year", type=int, help="Release year")
def add(
    audio_file: str, title: str, artist: str, album: Optional[str], year: Optional[int]
):
    """
    Add a song to the database

    AUDIO_FILE: Path to the audio file to add
    """
    try:
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("🎵 Adding song to database...", total=None)

                # Load and process audio
                audio_data, sample_rate = cli.audio_processor.load_audio(audio_file)

                # Generate fingerprint
                fingerprint = cli.recognizer.fingerprint_generator.generate(
                    audio_data, sample_rate
                )

                # Create song object
                song = Song(
                    title=title,
                    artist=artist,
                    album=album,
                    year=year,
                    duration=len(audio_data) / sample_rate,
                    file_path=audio_file,
                )

                # Add to database
                song_id = cli.recognizer.database_manager.add_song(song, fingerprint)

            console.print(
                f"✅ [green]Song added successfully with ID: {song_id}[/green]"
            )
        else:
            print("🎵 Adding song to database...")

            # Load and process audio
            audio_data, sample_rate = cli.audio_processor.load_audio(audio_file)
            fingerprint = cli.recognizer.fingerprint_generator.generate(
                audio_data, sample_rate
            )

            song = Song(
                title=title,
                artist=artist,
                album=album,
                year=year,
                duration=len(audio_data) / sample_rate,
                file_path=audio_file,
            )

            song_id = cli.recognizer.database_manager.add_song(song, fingerprint)
            print(f"✅ Song added successfully with ID: {song_id}")

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Error adding song: {e}[/red]")
        else:
            print(f"❌ Error adding song: {e}")


@db.command()
@click.argument("query")
@click.option(
    "--field",
    default="title",
    type=click.Choice(["title", "artist", "album"]),
    help="Field to search",
)
def search(query: str, field: str):
    """
    Search songs in database

    QUERY: Search query string
    """
    try:
        songs = cli.recognizer.database_manager.search_songs(query, field)

        if not songs:
            if RICH_AVAILABLE:
                console.print("❌ [yellow]No songs found[/yellow]")
            else:
                print("❌ No songs found")
            return

        if RICH_AVAILABLE:
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Artist", style="yellow")
            table.add_column("Album", style="blue")
            table.add_column("Year", style="magenta")

            for song in songs:
                table.add_row(
                    str(song.id),
                    song.title,
                    song.artist,
                    song.album or "-",
                    str(song.year) if song.year else "-",
                )

            console.print(table)
        else:
            print(f"\nSearch Results for '{query}':")
            print("-" * 60)
            for song in songs:
                print(f"ID: {song.id} | {song.title} by {song.artist}")
                if song.album:
                    print(f"  Album: {song.album}")
                if song.year:
                    print(f"  Year: {song.year}")
                print()

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Error searching: {e}[/red]")
        else:
            print(f"❌ Error searching: {e}")


@db.command()
def stats():
    """Show database statistics"""
    try:
        stats = cli.recognizer.database_manager.get_database_size()

        if RICH_AVAILABLE:
            table = Table(title="📊 Database Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="green")

            table.add_row("🎵 Total Songs", f"{stats['songs']:,}")
            table.add_row("🔍 Fingerprints", f"{stats['fingerprints']:,}")
            table.add_row("📈 Recognitions", f"{stats['recognitions']:,}")

            console.print(table)
        else:
            print("\n📊 Database Statistics:")
            print("-" * 30)
            print(f"🎵 Total Songs: {stats['songs']:,}")
            print(f"🔍 Fingerprints: {stats['fingerprints']:,}")
            print(f"📈 Recognitions: {stats['recognitions']:,}")

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Error getting statistics: {e}[/red]")
        else:
            print(f"❌ Error getting statistics: {e}")


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool):
    """
    Start the MUZAM web server

    Launches the FastAPI web interface and API server.
    """
    try:
        import uvicorn
        from ..web.app import app

        if RICH_AVAILABLE:
            console.print(
                f"🚀 [green]Starting MUZAM server on http://{host}:{port}[/green]"
            )
        else:
            print(f"🚀 Starting MUZAM server on http://{host}:{port}")

        uvicorn.run(app, host=host, port=port, reload=reload)

    except ImportError:
        if RICH_AVAILABLE:
            console.print(
                "❌ [red]FastAPI and uvicorn are required for the web server[/red]"
            )
        else:
            print("❌ FastAPI and uvicorn are required for the web server")
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Error starting server: {e}[/red]")
        else:
            print(f"❌ Error starting server: {e}")


@main.command()
def devices():
    """List available audio input devices"""
    try:
        devices = cli.audio_processor.list_audio_devices()

        if not devices:
            if RICH_AVAILABLE:
                console.print("❌ [yellow]No audio input devices found[/yellow]")
            else:
                print("❌ No audio input devices found")
            return

        if RICH_AVAILABLE:
            table = Table(title="🎤 Available Audio Input Devices")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Channels", style="yellow")
            table.add_column("Sample Rate", style="blue")

            for device_id, info in devices.items():
                table.add_row(
                    str(device_id),
                    info["name"],
                    str(info["channels"]),
                    f"{info['sample_rate']:.0f} Hz",
                )

            console.print(table)
        else:
            print("\n🎤 Available Audio Input Devices:")
            print("-" * 50)
            for device_id, info in devices.items():
                print(
                    f"ID: {device_id} | {info['name']} ({info['channels']} channels, {info['sample_rate']:.0f} Hz)"
                )

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ [red]Error listing devices: {e}[/red]")
        else:
            print(f"❌ Error listing devices: {e}")


if __name__ == "__main__":
    main()
