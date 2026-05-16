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
            try:
                # PaddleOCR hoạt động tốt nhất với numpy array (RGB)
                img_np = np.array(image.convert('RGB'))

                model = self.rec_models[lang]
                output = model.predict(img_np)
                
                texts = []
                for res in output:
                    res.print()
                    res_dict = res.json if hasattr(res, 'json') else res
                    logger.info(f"res_dict: {res_dict}")
                    # Pipeline text_recognition thường trả về 'rec_text' (chuỗi) hoặc 'rec_texts' (mảng)
                    if 'rec_text' in res_dict and isinstance(res_dict['rec_text'], str):
                        texts.append(res_dict['rec_text'])
                    elif 'rec_texts' in res_dict:
                        texts.extend(res_dict['rec_texts'])
                        
                    res.save_to_img("/local_output/")
                return " ".join(texts)
            except Exception as e:
                print(f"Lỗi OCR {lang}: {e}")
                return ""
            
        return ""