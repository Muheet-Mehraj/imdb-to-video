"""
Frame rendering pipeline.

``render()`` is the single public entry point.  It clears the frames
directory, runs each section in order, and returns the total number of
frames written.
"""

import logging
from pathlib import Path

from ..config import FPS, PLOT_MAX_SECONDS, PLOT_MIN_SECONDS, SECTION_DURATIONS
from ..models import MovieData
from .sections import (
    section_cast,
    section_highlights,
    section_outro,
    section_plot,
    section_quote,
    section_stats,
    section_title,
)

log = logging.getLogger(__name__)


def render(movie: MovieData, frames_dir: Path, audio_duration: float) -> int:
    """Render all video frames for *movie* into *frames_dir*.

    Parameters
    ----------
    movie:
        Populated movie metadata.
    frames_dir:
        Directory to write JPEG frames into.  Existing frames are purged first.
    audio_duration:
        Length of the narration audio in seconds; used to size the plot section.

    Returns
    -------
    total_frames : int
        Total number of frames written (= video length in frames).
    """
    frames_dir.mkdir(parents=True, exist_ok=True)
    _clear_frames(frames_dir)

    plot_seconds = max(PLOT_MIN_SECONDS, min(PLOT_MAX_SECONDS, audio_duration - 14))
    plot_frames  = int(FPS * plot_seconds)

    sections = [
        ("title",      section_title,      {}),
        ("stats",      section_stats,      {}),
        ("cast",       section_cast,       {}),
        ("plot",       section_plot,       {"n_frames": plot_frames}),
        ("highlights", section_highlights, {}),
        ("quote",      section_quote,      {}),
        ("outro",      section_outro,      {}),
    ]

    idx = 0
    for name, fn, kwargs in sections:
        log.info("Rendering section: %s (from frame %d)", name, idx)
        idx = fn(movie, frames_dir, idx, **kwargs)

    total_seconds = idx / FPS
    log.info("Rendering complete: %d frames = %.1f s (%.1f min)", idx, total_seconds, total_seconds / 60)
    return idx


def _clear_frames(frames_dir: Path) -> None:
    removed = 0
    for f in frames_dir.glob("*.jpg"):
        f.unlink()
        removed += 1
    if removed:
        log.debug("Cleared %d old frames from %s", removed, frames_dir)
