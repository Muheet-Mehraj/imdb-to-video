"""
FFmpeg muxing step.

Combines the rendered JPEG frame sequence with the TTS audio track
to produce the final H.264 / AAC MP4.
"""

import logging
import subprocess
from pathlib import Path

from ..config import (
    FFMPEG_AUDIO_BITRATE, FFMPEG_CRF, FFMPEG_PRESET, FPS,
)

log = logging.getLogger(__name__)


def assemble(frames_dir: Path, audio_path: Path, output_path: Path) -> None:
    """Mux *frames_dir* + *audio_path* into an MP4 at *output_path*.

    Raises
    ------
    RuntimeError
        If FFmpeg exits with a non-zero return code.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.jpg"),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-preset", FFMPEG_PRESET,
        "-crf", str(FFMPEG_CRF),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", FFMPEG_AUDIO_BITRATE,
        "-shortest",
        str(output_path),
    ]

    log.info("Running FFmpeg: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.error("FFmpeg failed:\n%s", result.stderr[-800:])
        raise RuntimeError(f"FFmpeg exited with code {result.returncode}")

    size_mb = output_path.stat().st_size / 1e6
    log.info("Output: %s (%.1f MB)", output_path, size_mb)
