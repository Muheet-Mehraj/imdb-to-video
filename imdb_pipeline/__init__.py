"""
imdb_pipeline — IMDb listing → 2-minute video converter.

Subpackages
-----------
scraper     Web scraping + demo data
renderer    Frame-by-frame video slide rendering
audio       TTS narration generation
assembler   FFmpeg muxing
"""
from .models import MovieData

__all__ = ["MovieData"]
