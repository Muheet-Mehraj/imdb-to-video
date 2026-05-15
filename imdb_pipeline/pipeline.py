"""
Pipeline orchestrator.

``run()`` is the single public entry point that calls each stage in
order and returns the path to the finished video.

    scrape → audio → render frames → assemble
"""

import logging
from pathlib import Path

from .assembler import assemble
from .audio import generate as generate_audio
from .config import DEFAULT_OUTPUT_DIR, DEFAULT_WORK_DIR
from .models import MovieData
from .renderer import render
from .scraper import scrape

log = logging.getLogger(__name__)


def run(
    imdb_url: str,
    output_path: Path | None = None,
    work_dir: Path | None = None,
) -> Path:
    """Convert an IMDb movie listing into a ~2-minute MP4 video.

    Parameters
    ----------
    imdb_url:
        Full IMDb title URL, e.g. ``https://www.imdb.com/title/tt0111161/``
    output_path:
        Destination for the finished MP4.  Defaults to
        ``/mnt/user-data/outputs/movie_spotlight.mp4``.
    work_dir:
        Scratch directory for intermediate frames and audio.
        Defaults to ``/home/claude/imdb_pipeline_run``.

    Returns
    -------
    Path
        Absolute path to the finished MP4.
    """
    output_path = Path(output_path) if output_path else DEFAULT_OUTPUT_DIR / "movie_spotlight.mp4"
    work_dir    = Path(work_dir)    if work_dir    else DEFAULT_WORK_DIR

    frames_dir = work_dir / "frames"
    audio_dir  = work_dir / "audio"

    log.info("=== IMDb → Video Pipeline ===")
    log.info("URL:    %s", imdb_url)
    log.info("Output: %s", output_path)

    # Stage 1 — Scrape
    movie: MovieData = scrape(imdb_url)

    # Stage 2 — Audio (need duration before sizing the plot section)
    audio_path, audio_duration = generate_audio(movie, audio_dir)

    # Stage 3 — Render frames
    total_frames = render(movie, frames_dir, audio_duration)

    # Stage 4 — Assemble
    assemble(frames_dir, audio_path, output_path)

    log.info("Done → %s", output_path)
    return output_path
