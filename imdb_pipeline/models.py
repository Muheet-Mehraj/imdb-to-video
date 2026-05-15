"""Shared data model used across all pipeline stages."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class MovieData:
    title: str = "Unknown Title"
    year: str = ""
    rating: str = "N/A"
    votes: str = ""
    genre: List[str] = field(default_factory=list)
    duration: str = ""
    director: str = ""
    cast: List[str] = field(default_factory=list)
    plot: str = ""
    tagline: str = ""
    imdb_url: str = ""
    pg_rating: str = ""
    awards: str = ""
    trivia: List[str] = field(default_factory=list)

    def display_name(self) -> str:
        return f"{self.title} ({self.year})" if self.year else self.title
