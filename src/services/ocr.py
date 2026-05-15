import numpy as np
from PIL import Image
from manga_ocr import MangaOcr
from paddlex import create_pipeline
from src.common.config import settings

class OcrService:
    def __init__(self):
        # Khởi tạo sẵn MangaOcr cho tiếng Nhật
        self.mocr = MangaOcr()
        # Cache các instance PaddleOCR để tránh khởi tạo lại nhiều lần
        self.paddle_instances = {
            'ko': create_pipeline(pipeline="OCR", text_rec_model="korean_PP-OCRv4_mobile_rec"),
            'zh': create_pipeline(pipeline="OCR", text_rec_model="ch_PP-OCRv4_mobile_rec")
        }

    def recognize(self, image: Image.Image, lang: str) -> str:
        if lang == 'ja':
            return self.mocr(image)
        
        if lang in self.paddle_instances:
            try:
                # PaddleOCR hoạt động tốt nhất với numpy array (RGB)
                img_np = np.array(image.convert('RGB'))
                pipeline = self.paddle_instances[lang]
                
                # Thực hiện nhận diện
                output = pipeline.predict(img_np)
                
                texts = []
                for res in output:
                    # Pipeline trả về generator, lấy dictionary thông qua thuộc tính json
                    res_dict = res.json if hasattr(res, 'json') else res
                    
                    if 'rec_texts' in res_dict:
                        texts.extend(res_dict['rec_texts'])
                        
                return " ".join(texts)
            except Exception as e:
                print(f"Lỗi OCR {lang}: {e}")
                return ""
            
        return ""