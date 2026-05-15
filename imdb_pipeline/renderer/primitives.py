"""
Low-level drawing helpers used by every slide section.

All helpers accept a Pillow ``ImageDraw`` (or ``Image``) and return
plain values so they stay pure and easy to test in isolation.
"""

import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from ..config import (
    COLORS, FONTS, GRAIN_STRENGTH, VIDEO_HEIGHT as H,
    VIDEO_WIDTH as W, VIGNETTE_STRENGTH,
)

# Pre-compute vignette mask once at import time (expensive NumPy op).
# Reusing this array across ~2 400 frames saves several minutes of CPU.
_cx, _cy = W / 2, H / 2
_Y, _X = np.ogrid[:H, :W]
_dist = np.sqrt(((_X - _cx) / _cx) ** 2 + ((_Y - _cy) / _cy) ** 2)
VIGNETTE_MASK = (1 - np.clip(_dist * VIGNETTE_STRENGTH, 0, 1))[:, :, np.newaxis].astype(np.float32)


# ── Fonts ──────────────────────────────────────────────────────────────────────

def font(style: str, size: int) -> ImageFont.FreeTypeFont:
    """Return a cached Poppins font variant at *size* pixels."""
    path = FONTS.get(style, FONTS["regular"])
    return ImageFont.truetype(str(path), size)


# ── Backgrounds ────────────────────────────────────────────────────────────────

def gradient_bg(top=None, bottom=None) -> Image.Image:
    """Create a vertical linear gradient background image."""
    top    = top    or COLORS["bg_dark"]
    bottom = bottom or COLORS["bg_mid"]
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for c in range(3):
        col = np.linspace(top[c], bottom[c], H, dtype=np.float32)
        arr[:, :, c] = col[:, np.newaxis].astype(np.uint8)
    return Image.fromarray(arr)


# ── Post-processing ────────────────────────────────────────────────────────────

def apply_post(img: Image.Image) -> Image.Image:
    """Apply vignette darkening and film-grain noise to *img* in-place."""
    arr = np.array(img, dtype=np.float32) * VIGNETTE_MASK
    noise = np.random.randint(-GRAIN_STRENGTH, GRAIN_STRENGTH, arr.shape, dtype=np.int16)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


# ── Animation ─────────────────────────────────────────────────────────────────

def ease_out(t: float, power: float = 2.5) -> float:
    """Ease-out curve: fast start, decelerates to 1.0."""
    return 1 - (1 - max(0.0, min(1.0, t))) ** power


# ── UI Components ─────────────────────────────────────────────────────────────

def draw_pill(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int, y: int,
    f: ImageFont.FreeTypeFont,
    bg=None,
    fg=None,
    pad_x: int = 16,
    pad_y: int = 7,
) -> int:
    """Draw a rounded pill badge and return the x coordinate of its right edge."""
    bg = bg or COLORS["accent"]
    fg = fg or COLORS["white"]
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x2 = x + tw + pad_x * 2
    y2 = y + th + pad_y * 2
    draw.rounded_rectangle([x, y, x2, y2], radius=18, fill=bg)
    draw.text((x + pad_x, y + pad_y), text, font=f, fill=fg)
    return x2


def draw_star_rating(
    draw: ImageDraw.ImageDraw,
    rating_str: str,
    x: int, y: int,
    size: int = 22,
) -> None:
    """Render ★ / ☆ glyphs for a numeric rating string (e.g. '9.3')."""
    try:
        rating = float(rating_str)
    except (ValueError, TypeError):
        return
    full  = int(rating / 2)
    frac  = (rating / 2) - full
    empty = 5 - full - (1 if frac > 0.1 else 0)
    sf = font("bold", size)
    cx = x
    for _ in range(full):
        draw.text((cx, y), "★", font=sf, fill=COLORS["star_gold"]); cx += size + 2
    if frac > 0.1:
        draw.text((cx, y), "½", font=sf, fill=COLORS["star_gold"]); cx += size + 2
    for _ in range(max(0, empty)):
        draw.text((cx, y), "☆", font=sf, fill=COLORS["gray"]); cx += size + 2


def wrap_text(text: str, f: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap *text* so every line fits within *max_width* pixels."""
    words, lines, current = text.split(), [], []
    for word in words:
        candidate = " ".join(current + [word])
        if f.getbbox(candidate)[2] > max_width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines
