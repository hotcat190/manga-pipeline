from .base import BaseOcrEngine
from .manga.engine import MangaOcrEngine
from .webtoon.webtoon_engine import WebtoonOcrEngine

class OcrFactory:
    @staticmethod
    def get_engine(comic_type: str, **kwargs) -> BaseOcrEngine:
        if comic_type == 'webtoon':
            return WebtoonOcrEngine(**kwargs)
        return MangaOcrEngine(**kwargs)