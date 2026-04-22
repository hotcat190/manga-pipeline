from abc import ABC, abstractmethod
from typing import Tuple, List, Dict
from PIL import Image

class BaseOcrEngine(ABC):
    @abstractmethod
    def process(self, image_path: str) -> Tuple[Image.Image, List[Dict]]:
        pass