"""Tests for imdb_pipeline.audio.tts — script builder only (no subprocess calls)."""

from imdb_pipeline.audio.tts import _build_script
from imdb_pipeline.config import TTS_MAX_WORDS
from imdb_pipeline.models import MovieData


def _movie(**kwargs) -> MovieData:
    defaults = dict(
        title="Test Movie", year="2024", rating="8.5",
        director="Jane Director", cast=["Actor One", "Actor Two"],
        genre=["Drama", "Thriller"], duration="2h 0m",
        plot="A gripping tale of survival.", tagline="Never give up.",
        pg_rating="PG-13", awards="Won 2 Oscars",
        trivia=["Fact one.", "Fact two."],
    )
    defaults.update(kwargs)
    return MovieData(**defaults)


class TestBuildScript:
    def test_contains_title(self):
        script = _build_script(_movie())
        assert "Test Movie" in script

    def test_contains_director(self):
        script = _build_script(_movie())
        assert "Jane Director" in script

    def test_contains_plot(self):
        script = _build_script(_movie())
        assert "gripping tale" in script

    def test_word_count_within_limit(self):
        long_plot = "word " * 500
        script = _build_script(_movie(plot=long_plot))
        assert len(script.split()) <= TTS_MAX_WORDS

    def test_missing_optional_fields_omitted(self):
        script = _build_script(_movie(director="", tagline="", awards=""))
        assert "Directed by" not in script
        assert "Tagline:" not in script
        assert "Awards:" not in script

    def test_empty_cast_omitted(self):
        script = _build_script(_movie(cast=[]))
        assert "Starring" not in script
