#!/usr/bin/env python3
"""
Command-line entry point for the IMDb → video pipeline.

Usage
-----
    python -m imdb_pipeline <imdb_url> [output_path] [--omdb-key KEY] [--work-dir DIR] [--verbose]

Examples
--------
    # Recommended: set your key once as an env var
    set OMDB_API_KEY=your_key_here          # Windows
    export OMDB_API_KEY=your_key_here       # Linux / macOS
    python -m imdb_pipeline https://www.imdb.com/title/tt0111161/

    # Or pass it inline
    python -m imdb_pipeline https://www.imdb.com/title/tt0111161/ --omdb-key your_key_here

    # Custom output path
    python -m imdb_pipeline https://www.imdb.com/title/tt0068646/ ./godfather.mp4 --verbose

Get a free API key at https://www.omdbapi.com/apikey.aspx
"""

import argparse
import logging
import sys
from pathlib import Path

from imdb_pipeline.pipeline import run


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert an IMDb movie listing into a ~2-minute video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("url",         help="IMDb title URL")
    parser.add_argument("output",      nargs="?", default=None,
                        help="Output MP4 path (default: outputs/movie_spotlight.mp4)")
    parser.add_argument("--omdb-key",  default=None,
                        help="OMDb API key (overrides OMDB_API_KEY env var). "
                             "Get one free at https://www.omdbapi.com/apikey.aspx")
    parser.add_argument("--work-dir",  default=None,
                        help="Scratch directory for frames/audio")
    parser.add_argument("--verbose",   action="store_true",
                        help="Enable DEBUG logging")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )

    output = run(
        imdb_url=args.url,
        output_path=Path(args.output) if args.output else None,
        work_dir=Path(args.work_dir)  if args.work_dir else None,
        omdb_api_key=args.omdb_key,
    )
    print(f"\n✅  Video ready → {output}")


if __name__ == "__main__":
    main()