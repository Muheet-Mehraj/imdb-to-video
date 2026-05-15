"""Tests for imdb_pipeline.renderer.primitives."""

import numpy as np
import pytest
from PIL import Image, ImageDraw

from imdb_pipeline.renderer.primitives import (
    ease_out,
    gradient_bg,
    wrap_text,
    font,
    VIGNETTE_MASK,
)
from imdb_pipeline.config import VIDEO_WIDTH as W, VIDEO_HEIGHT as H


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
    def test_short_text_single_line(self):
        f = font("regular", 20)
        lines = wrap_text("Hi", f, 500)
        assert lines == ["Hi"]

    def test_long_text_wraps(self):
        f = font("regular", 20)
        text = "This is a very long sentence that should definitely be wrapped into multiple lines."
        lines = wrap_text(text, f, 200)
        assert len(lines) > 1

    def test_no_line_exceeds_max_width(self):
        f = font("regular", 20)
        text = "Word " * 30
        lines = wrap_text(text, f, 300)
        for line in lines:
            assert f.getbbox(line)[2] <= 300
