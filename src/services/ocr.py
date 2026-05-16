import numpy as np
import logging
from PIL import Image
from manga_ocr import MangaOcr
from paddleocr import PaddleOCR
from src.common.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OcrService:
    def __init__(self):
        # Khởi tạo sẵn MangaOcr cho tiếng Nhật
        self.mocr = MangaOcr()
        
        # 2. Module Text Recognition Only (Dành cho Manga đọc ảnh đã crop)
        self.rec_models = {
            'ko': PaddleOCR(lang="korean"),
            'zh': PaddleOCR(lang="ch")
        }

    def recognize(self, image: Image.Image, lang: str) -> str:
        if lang == 'ja':
            return self.mocr(image)
        
        if lang in self.rec_models:
            raise NotImplementedError(f"OcrService.recognize for lang {lang} is not supported")
            
        return ""