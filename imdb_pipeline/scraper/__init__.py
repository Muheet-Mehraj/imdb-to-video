"""IMDb scraping: live HTTP + fallback demo data."""

from .imdb import scrape
from .demo import DEMO_MOVIES

__all__ = ["scrape", "DEMO_MOVIES"]
