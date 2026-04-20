from typing import Tuple, List, Dict
from PIL import Image
from .base import BaseOcrEngine

class WebtoonOcrEngine(BaseOcrEngine):
    def __init__(self):
        pass

    def process(self, image_path: str) -> Tuple[Image.Image, List[Dict]]:
        # TODO
        return Image.new('RGB', (100, 100)), []