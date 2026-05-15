"""Tests for imdb_pipeline.renderer.primitives."""

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from imdb_pipeline.renderer.primitives import (
    ease_out,
    gradient_bg,
    wrap_text,
    font,
    VIGNETTE_MASK,
)
from imdb_pipeline.config import VIDEO_WIDTH as W, VIDEO_HEIGHT as H


# ---------------------------------------------------------------------------
# Fixture: skip font-dependent tests when no TTF is available.
#
# The Poppins .ttf files live at /usr/share/fonts/truetype/google-fonts/ on
# Linux CI but are not present on a stock Windows machine.  Bundle them in
# imdb_pipeline/assets/fonts/ to make these tests pass everywhere.
# ---------------------------------------------------------------------------

def _has_truetype_font() -> bool:
    """Return True if font() resolves to a real FreeType font."""
    return isinstance(font("regular", 12), ImageFont.FreeTypeFont)


requires_ttf = pytest.mark.skipif(
    not _has_truetype_font(),
    reason=(
        "Poppins TTF not found. "
        "Copy the four Poppins .ttf files into imdb_pipeline/assets/fonts/ "
        "or install them via: "
        "sudo apt-get install fonts-google-poppins  (Linux)."
    ),
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEaseOut:
    def test_zero_returns_zero(self):
        assert ease_out(0.0) == pytest.approx(0.0)

    def test_one_returns_one(self):
        assert ease_out(1.0) == pytest.approx(1.0)

    def test_midpoint_greater_than_half(self):
        # ease-out accelerates at the start
        assert ease_out(0.5) > 0.5

    def test_clamped_below_zero(self):
        assert ease_out(-1.0) == pytest.approx(0.0)

    def test_clamped_above_one(self):
        assert ease_out(2.0) == pytest.approx(1.0)


class TestGradientBg:
    def test_returns_correct_size(self):
        img = gradient_bg()
        assert img.size == (W, H)

    def test_top_pixel_matches_top_color(self):
        top = (255, 0, 0)
        img = gradient_bg(top=top, bottom=(0, 0, 255))
        pixel = img.getpixel((W // 2, 0))
        assert pixel[0] > 200  # red channel dominant at top

    def test_bottom_pixel_matches_bottom_color(self):
        bottom = (0, 0, 255)
        img = gradient_bg(top=(255, 0, 0), bottom=bottom)
        pixel = img.getpixel((W // 2, H - 1))
        assert pixel[2] > 200  # blue channel dominant at bottom


class TestVignetteMask:
    def test_shape(self):
        assert VIGNETTE_MASK.shape == (H, W, 1)

    def test_centre_is_bright(self):
        centre = VIGNETTE_MASK[H // 2, W // 2, 0]
        assert centre > 0.9

    def test_corners_are_dark(self):
        corner = VIGNETTE_MASK[0, 0, 0]
        assert corner < 0.6


class TestWrapText:
    @requires_ttf
    def test_short_text_single_line(self):
        f = font("regular", 20)
        lines = wrap_text("Hi", f, 500)
        assert lines == ["Hi"]

    @requires_ttf
    def test_long_text_wraps(self):
        f = font("regular", 20)
        text = "This is a very long sentence that should definitely be wrapped into multiple lines."
        lines = wrap_text(text, f, 200)
        assert len(lines) > 1

    @requires_ttf
    def test_no_line_exceeds_max_width(self):
        f = font("regular", 20)
        text = "Word " * 30
        lines = wrap_text(text, f, 300)
        for line in lines:
            assert f.getbbox(line)[2] <= 300