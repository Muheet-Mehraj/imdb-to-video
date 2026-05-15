"""
IMDb scraper with OMDb API support.

Priority order:
  1. OMDb API  (set OMDB_API_KEY env var or pass via --omdb-key CLI flag)
  2. Live IMDb scrape  (JSON-LD block)
  3. Bundled demo data  (always works, no network needed)
"""

import json
import logging
import os
import re

import requests
from bs4 import BeautifulSoup

from ..models import MovieData
from .demo import DEMO_MOVIES

log = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

OMDB_API_URL = "http://www.omdbapi.com/"


# ── Public entry point ─────────────────────────────────────────────────────────

def scrape(url: str, omdb_api_key: str | None = None) -> MovieData:
    """Fetch and parse movie data for an IMDb title URL.

    Parameters
    ----------
    url:
        Full IMDb title URL, e.g. ``https://www.imdb.com/title/tt0111161/``
    omdb_api_key:
        OMDb API key. If not provided, falls back to the ``OMDB_API_KEY``
        environment variable.

    Returns
    -------
    MovieData
        Populated from OMDb → live IMDb → demo data (first source that works).
    """
    log.info("Scraping %s", url)
    imdb_id = _extract_id(url)

    # 1. Try OMDb API
    api_key = omdb_api_key or os.environ.get("OMDB_API_KEY", "")
    if api_key:
        movie = _scrape_omdb(imdb_id, url, api_key)
        if movie:
            log.info("OMDb → %s", movie.display_name())
            return movie
    else:
        log.warning("No OMDB_API_KEY found — skipping OMDb, trying live IMDb scrape")

    # 2. Try live IMDb scrape
    movie = _scrape_imdb(url, imdb_id)
    if movie:
        log.info("IMDb scrape → %s", movie.display_name())
        return movie

    # 3. Demo fallback
    return _demo_fallback(imdb_id, url)


# ── OMDb ───────────────────────────────────────────────────────────────────────

def _scrape_omdb(imdb_id: str, url: str, api_key: str) -> MovieData | None:
    """Fetch data from the OMDb API. Returns None on any failure."""
    if not imdb_id:
        log.warning("Could not extract IMDb ID from URL — skipping OMDb")
        return None

    try:
        resp = requests.get(
            OMDB_API_URL,
            params={"i": imdb_id, "apikey": api_key, "plot": "full"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        log.warning("OMDb request failed (%s)", exc)
        return None

    if data.get("Response") != "True":
        log.warning("OMDb returned error: %s", data.get("Error", "unknown"))
        return None

    return _apply_omdb(data, url)


def _apply_omdb(data: dict, url: str) -> MovieData:
    """Map an OMDb response dict to a MovieData instance."""
    movie = MovieData(imdb_url=url)

    movie.title     = data.get("Title", "")
    movie.year      = data.get("Year", "")
    movie.pg_rating = data.get("Rated", "")
    movie.duration  = _runtime_to_hm(data.get("Runtime", ""))
    movie.director  = data.get("Director", "")
    movie.plot      = data.get("Plot", "")
    movie.tagline   = ""   # OMDb doesn't provide taglines
    movie.awards    = data.get("Awards", "")

    genre_str = data.get("Genre", "")
    movie.genre = [g.strip() for g in genre_str.split(",") if g.strip()]

    actors_str = data.get("Actors", "")
    movie.cast = [a.strip() for a in actors_str.split(",") if a.strip()][:6]

    movie.rating = data.get("imdbRating", "N/A")
    votes_raw    = data.get("imdbVotes", "")
    movie.votes  = votes_raw  # already formatted as "1,234,567"

    return movie


def _runtime_to_hm(runtime: str) -> str:
    """Convert ``'142 min'`` → ``'2h 22m'``."""
    m = re.match(r"(\d+)", runtime)
    if not m:
        return runtime
    total = int(m.group(1))
    h, mn = divmod(total, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if mn:
        parts.append(f"{mn}m")
    return " ".join(parts) or runtime


# ── Live IMDb scrape ───────────────────────────────────────────────────────────

def _scrape_imdb(url: str, imdb_id: str) -> MovieData | None:
    """Try fetching directly from IMDb. Returns None on failure."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        movie = _parse_page(resp.text, url)
        return movie
    except Exception as exc:
        log.warning("Live IMDb scrape failed (%s)", exc)
        return None


def _parse_page(html: str, url: str) -> MovieData:
    soup  = BeautifulSoup(html, "html.parser")
    movie = MovieData(imdb_url=url)

    ld_tag = soup.find("script", {"type": "application/ld+json"})
    if ld_tag:
        _apply_json_ld(json.loads(ld_tag.string), movie)

    if not movie.year:
        movie.year = _html_year(soup)

    return movie


def _apply_json_ld(data: dict, movie: MovieData) -> None:
    movie.title     = data.get("name", "")
    movie.plot      = data.get("description", "")
    movie.pg_rating = data.get("contentRating", "")

    genre = data.get("genre", [])
    movie.genre = [genre] if isinstance(genre, str) else genre

    movie.duration = _parse_iso_duration(data.get("duration", ""))

    agg = data.get("aggregateRating", {})
    movie.rating = str(agg.get("ratingValue", "N/A"))
    count = agg.get("ratingCount", 0)
    movie.votes = f"{count:,}" if isinstance(count, int) else str(count)

    dirs = data.get("director", [])
    if isinstance(dirs, list) and dirs:
        movie.director = dirs[0].get("name", "")
    elif isinstance(dirs, dict):
        movie.director = dirs.get("name", "")

    movie.cast = [
        a["name"] for a in data.get("actor", [])[:6]
        if isinstance(a, dict) and "name" in a
    ]


def _html_year(soup: BeautifulSoup) -> str:
    tag = soup.find("a", href=re.compile(r"/year/\d{4}"))
    if tag:
        return tag.get_text(strip=True)
    title_str = soup.title.string if soup.title else ""
    m = re.search(r"\((\d{4})\)", title_str)
    return m.group(1) if m else ""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_id(url: str) -> str:
    m = re.search(r"tt(\d+)", url)
    return f"tt{m.group(1)}" if m else ""


def _parse_iso_duration(iso: str) -> str:
    """Convert ``PT2H22M`` → ``2h 22m``."""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso)
    if not m:
        return ""
    h, mn = m.group(1), m.group(2)
    return " ".join(filter(None, [f"{h}h" if h else "", f"{mn}m" if mn else ""]))


def _demo_fallback(imdb_id: str, url: str) -> MovieData:
    movie = DEMO_MOVIES.get(imdb_id) or next(iter(DEMO_MOVIES.values()))
    log.info("Demo fallback → %s", movie.display_name())
    return movie