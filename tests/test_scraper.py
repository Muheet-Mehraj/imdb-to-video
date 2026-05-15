"""Tests for imdb_pipeline.scraper."""

import pytest
from imdb_pipeline.scraper.imdb import _parse_iso_duration, _extract_id
from imdb_pipeline.scraper.demo import DEMO_MOVIES
from imdb_pipeline.models import MovieData


class TestExtractId:
    def test_standard_url(self):
        assert _extract_id("https://www.imdb.com/title/tt0111161/") == "tt0111161"

    def test_url_with_trailing_params(self):
        assert _extract_id("https://www.imdb.com/title/tt0068646/?ref_=fn_al") == "tt0068646"

    def test_no_id_returns_empty(self):
        assert _extract_id("https://www.imdb.com/") == ""


class TestParseIsoDuration:
    def test_hours_and_minutes(self):
        assert _parse_iso_duration("PT2H22M") == "2h 22m"

    def test_hours_only(self):
        assert _parse_iso_duration("PT3H") == "3h"

    def test_minutes_only(self):
        assert _parse_iso_duration("PT45M") == "45m"

    def test_empty_string(self):
        assert _parse_iso_duration("") == ""

    def test_invalid_string(self):
        assert _parse_iso_duration("notaduration") == ""


class TestDemoMovies:
    def test_shawshank_present(self):
        assert "tt0111161" in DEMO_MOVIES

    def test_godfather_present(self):
        assert "tt0068646" in DEMO_MOVIES

    def test_all_entries_are_movie_data(self):
        for key, movie in DEMO_MOVIES.items():
            assert isinstance(movie, MovieData), f"{key} is not a MovieData"

    def test_shawshank_fields(self):
        m = DEMO_MOVIES["tt0111161"]
        assert m.title == "The Shawshank Redemption"
        assert m.year == "1994"
        assert float(m.rating) > 9.0
        assert len(m.cast) > 0
        assert len(m.genre) > 0
        assert m.plot != ""
