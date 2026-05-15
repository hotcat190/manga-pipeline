import numpy as np
from PIL import Image
from manga_ocr import MangaOcr
from paddleocr import PaddleOCR
from src.common.config import settings

class OcrService:
    def __init__(self):
        # Khởi tạo sẵn MangaOcr cho tiếng Nhật
        self.mocr = MangaOcr()
        # Cache các instance PaddleOCR để tránh khởi tạo lại nhiều lần
        self.paddle_instances = {
            'ko': PaddleOCR(use_angle_cls=True, lang='korean', show_log=False, use_gpu=False),
            'zh': PaddleOCR(use_angle_cls=True, lang='ch', show_log=False, use_gpu=False)
        }

    def recognize(self, image: Image.Image, lang: str) -> str:
        if lang == 'ja':
            return self.mocr(image)
        
        if lang in self.paddle_instances:
            try:
                # PaddleOCR hoạt động tốt nhất với numpy array (RGB)
                img_np = np.array(image.convert('RGB'))
                ocr = self.paddle_instances[lang]
                
                # Thực hiện nhận diện
                result = ocr.ocr(img_np, cls=True)
                
                if not result or not result[0]:
                    return ""
                
                # Trích xuất text từ kết quả (PaddleOCR trả về list các box và text)
                texts = [line[1][0] for line in result[0]]
                return " ".join(texts)
            except Exception as e:
                print(f"Lỗi OCR {lang}: {e}")
                return ""
            
        return ""