from .base import BaseOcrEngine
from .manga_engine import MangaOcrEngine
from .webtoon_engine import WebtoonOcrEngine

class OcrFactory:
    @staticmethod
    def get_engine(comic_type: str) -> BaseOcrEngine:
        if comic_type == 'webtoon':
            return WebtoonOcrEngine()
        return MangaOcrEngine()