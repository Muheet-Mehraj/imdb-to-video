"""
Live IMDb scraper.

Targets the JSON-LD (schema.org/Movie) block embedded in every IMDb
page — more robust than CSS-selector scraping against layout changes.
Falls back to demo data when the request is blocked (403) or the
network is unavailable.
"""

import json
import logging
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


def scrape(url: str) -> MovieData:
    """Fetch and parse an IMDb movie page.

    Parameters
    ----------
    url:
        Full IMDb title URL, e.g. ``https://www.imdb.com/title/tt0111161/``

    Returns
    -------
    MovieData
        Populated from live data, or from the demo catalogue on failure.
    """
    log.info("Scraping %s", url)
    imdb_id = _extract_id(url)

    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        movie = _parse_page(resp.text, url)
        log.info("Scraped: %s", movie.display_name())
        return movie

    except Exception as exc:
        log.warning("Live scrape failed (%s) — falling back to demo data", exc)
        return _demo_fallback(imdb_id, url)


# ── Parsers ────────────────────────────────────────────────────────────────────

def _parse_page(html: str, url: str) -> MovieData:
    soup  = BeautifulSoup(html, "html.parser")
    movie = MovieData(imdb_url=url)

    ld_tag = soup.find("script", {"type": "application/ld+json"})
    if ld_tag:
        _apply_json_ld(json.loads(ld_tag.string), movie)

    # Fill gaps with HTML fallback
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
    movie.votes  = f"{count:,}" if isinstance(count, int) else str(count)

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
