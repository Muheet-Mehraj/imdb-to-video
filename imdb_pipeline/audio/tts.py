"""
Text-to-speech narration via espeak-ng.

Produces a WAV via espeak-ng, converts to MP3, then applies a light
echo + EQ pass with FFmpeg to give the voice a warmer, more cinematic
character.

Returns the path to the final audio file and its duration in seconds.
"""

import logging
import subprocess
from pathlib import Path

from ..config import (
    TTS_AMPLITUDE, TTS_MAX_WORDS, TTS_PITCH, TTS_SPEED, TTS_VOICE,
)
from ..models import MovieData

log = logging.getLogger(__name__)


def generate(movie: MovieData, work_dir: Path) -> tuple[Path, float]:
    """Generate narration audio for *movie* and write it into *work_dir*.

    Returns
    -------
    (audio_path, duration_seconds)
    """
    work_dir.mkdir(parents=True, exist_ok=True)

    script = _build_script(movie)
    log.info("TTS script: %d words", len(script.split()))

    wav  = work_dir / "narration.wav"
    mp3  = work_dir / "narration.mp3"
    warm = work_dir / "narration_warm.mp3"

    _run_espeak(script, wav)
    _convert_to_mp3(wav, mp3)
    _apply_warmth(mp3, warm)

    final = warm if warm.exists() else mp3
    duration = _probe_duration(final)
    log.info("Audio ready: %.1f s → %s", duration, final)
    return final, duration


# ── Script builder ─────────────────────────────────────────────────────────────

def _build_script(movie: MovieData) -> str:
    parts = [
        f"Now presenting: {movie.title}.",
        f"Released in {movie.year}." if movie.year else "",
        f"A {movie.pg_rating} rated film." if movie.pg_rating else "",
        f"Rated {movie.rating} out of 10 on IMDb." if movie.rating != "N/A" else "",
        f"Runtime: {movie.duration}." if movie.duration else "",
        f"Directed by {movie.director}." if movie.director else "",
        f"Starring {', '.join(movie.cast[:3])}." if movie.cast else "",
        f"Genres: {', '.join(movie.genre)}." if movie.genre else "",
        f"Synopsis. {movie.plot}" if movie.plot else "",
        f"Tagline: {movie.tagline}." if movie.tagline else "",
        f"Awards: {movie.awards}." if movie.awards else "",
        "Why watch this film?",
        ". ".join(movie.trivia[:3]) + "." if movie.trivia else "",
        f"{movie.title}. A film that will stay with you long after the credits roll.",
    ]
    full = " ".join(p for p in parts if p)
    return " ".join(full.split()[:TTS_MAX_WORDS])


# ── FFmpeg / espeak-ng wrappers ────────────────────────────────────────────────

def _run_espeak(script: str, out: Path) -> None:
    _run([
        "espeak-ng",
        "-v", TTS_VOICE,
        "-s", str(TTS_SPEED),
        "-p", str(TTS_PITCH),
        "-a", str(TTS_AMPLITUDE),
        script,
        "-w", str(out),
    ], label="espeak-ng")


def _convert_to_mp3(src: Path, dst: Path) -> None:
    _run(["ffmpeg", "-y", "-i", str(src), "-q:a", "2", str(dst)], label="wav→mp3")


def _apply_warmth(src: Path, dst: Path) -> None:
    """Subtle echo + low-mid EQ boost for a warmer narrator sound."""
    _run([
        "ffmpeg", "-y", "-i", str(src),
        "-af", "aecho=0.8:0.7:40:0.15,equalizer=f=250:width_type=o:width=2:g=2",
        str(dst),
    ], label="warmth")


def _probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         str(path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip() or "30")


def _run(cmd: list[str], label: str) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log.warning("%s stderr: %s", label, result.stderr[-200:])
