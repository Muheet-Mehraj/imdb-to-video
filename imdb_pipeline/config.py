"""
Pipeline configuration.

All magic numbers live here. Import from this module rather than
hard-coding values in individual pipeline stages.
"""

import sys
from pathlib import Path

# ── Video ──────────────────────────────────────────────────────────────────────
VIDEO_WIDTH  = 1280
VIDEO_HEIGHT = 720
FPS          = 24

# ── Fonts ──────────────────────────────────────────────────────────────────────
# Resolution order:
#   1. Bundled fonts shipped with the repo  (imdb_pipeline/assets/fonts/)
#   2. Linux system Poppins                 (/usr/share/fonts/truetype/google-fonts/)
#   3. Windows system fonts dir             (C:\Windows\Fonts\)  — uses Arial as fallback
#
# To guarantee identical rendering on every OS, drop the four Poppins .ttf
# files into  imdb_pipeline/assets/fonts/  and commit them.  The pipeline
# always prefers the bundled copies when present.

_BUNDLED   = Path(__file__).parent / "assets" / "fonts"
_LINUX_SYS = Path("/usr/share/fonts/truetype/google-fonts")
_WIN_SYS   = Path("C:/Windows/Fonts")

def _find_font(name: str) -> Path:
    """Return the first existing path for *name*, searching bundled → system."""
    candidates = [
        _BUNDLED   / name,
        _LINUX_SYS / name,
    ]
    if sys.platform == "win32":
        # Windows fallback: Arial ships on every Windows install.
        win_fallback = name.replace("Poppins-", "Arial").replace(".ttf", ".ttf")
        candidates.append(_WIN_SYS / win_fallback)
        candidates.append(_WIN_SYS / "arial.ttf")

    for p in candidates:
        if p.exists():
            return p

    # Last resort: let Pillow use its built-in bitmap font.
    # font() in primitives.py must handle the None case.
    return candidates[0]   # keep the preferred path even if missing


FONTS = {
    "bold":    _find_font("Poppins-Bold.ttf"),
    "regular": _find_font("Poppins-Regular.ttf"),
    "light":   _find_font("Poppins-Light.ttf"),
    "medium":  _find_font("Poppins-Medium.ttf"),
}

# ── Colour palette ─────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":    (8,   8,  18),
    "bg_mid":     (15,  15, 35),
    "deep_blue":  (5,   10, 30),
    "gold":       (255, 200, 50),
    "gold_dim":   (180, 140, 30),
    "star_gold":  (255, 185,  0),
    "white":      (255, 255, 255),
    "light_gray": (200, 200, 210),
    "gray":       (140, 140, 155),
    "accent":     (60,  140, 220),
}

# ── TTS ────────────────────────────────────────────────────────────────────────
TTS_VOICE     = "en+f3"
TTS_SPEED     = 140          # words per minute
TTS_PITCH     = 48
TTS_AMPLITUDE = 180
TTS_MAX_WORDS = 200          # truncate script to this many words

# ── Section durations (seconds) ────────────────────────────────────────────────
SECTION_DURATIONS = {
    "title":      4,
    "stats":      5,
    "cast":       5,
    "highlights": 30,
    "quote":      10,
    "outro":      6,
}
PLOT_MIN_SECONDS = 20
PLOT_MAX_SECONDS = 55

# ── Rendering ──────────────────────────────────────────────────────────────────
FRAME_FORMAT  = "JPEG"
FRAME_QUALITY = 88
VIGNETTE_STRENGTH = 0.6
GRAIN_STRENGTH    = 8

# ── FFmpeg ─────────────────────────────────────────────────────────────────────
FFMPEG_CRF     = 20
FFMPEG_PRESET  = "fast"
FFMPEG_AUDIO_BITRATE = "192k"

# ── Paths (defaults, overridable at runtime) ───────────────────────────────────
# Paths are relative to the project root so they work on Windows and Linux.
# Override at runtime with --work-dir / --output CLI flags.
DEFAULT_WORK_DIR   = Path.home() / ".imdb_pipeline_cache"
DEFAULT_OUTPUT_DIR = Path.cwd() / "outputs"