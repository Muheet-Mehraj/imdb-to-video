"""
Pipeline configuration.

All magic numbers live here. Import from this module rather than
hard-coding values in individual pipeline stages.
"""

from pathlib import Path

# ── Video ──────────────────────────────────────────────────────────────────────
VIDEO_WIDTH  = 1280
VIDEO_HEIGHT = 720
FPS          = 24

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_DIR = Path("/usr/share/fonts/truetype/google-fonts")
FONTS = {
    "bold":    FONT_DIR / "Poppins-Bold.ttf",
    "regular": FONT_DIR / "Poppins-Regular.ttf",
    "light":   FONT_DIR / "Poppins-Light.ttf",
    "medium":  FONT_DIR / "Poppins-Medium.ttf",
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
DEFAULT_WORK_DIR   = Path("/home/claude/imdb_pipeline_run")
DEFAULT_OUTPUT_DIR = Path("/mnt/user-data/outputs")
