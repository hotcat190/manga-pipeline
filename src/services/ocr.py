import numpy as np
from PIL import Image
from manga_ocr import MangaOcr
from paddlex import create_pipeline, create_model
from src.common.config import settings

class OcrService:
    def __init__(self):
        # Khởi tạo sẵn MangaOcr cho tiếng Nhật
        self.mocr = MangaOcr()

        # Cache các instance PaddleOCR để tránh khởi tạo lại nhiều lần
        # 1. Pipeline Full OCR (Dành cho Webtoon đọc nguyên trang)
        self.full_pipelines = {
            'ja': create_pipeline(pipeline="OCR", text_det_model="PP-OCRv5_server_det", text_rec_model="japan_PP-OCRv3_rec"),
            'ko': create_pipeline(pipeline="OCR", text_det_model="PP-OCRv5_server_det", text_rec_model="korean_PP-OCRv3_rec"),
            'zh': create_pipeline(pipeline="OCR", text_det_model="PP-OCRv5_server_det", text_rec_model="PP-OCRv5_server_rec")
        }
        
        # 2. Module Text Recognition Only (Dành cho Manga đọc ảnh đã crop)
        self.rec_models = {
            'ko': create_model(model_name="korean_PP-OCRv3_rec"),
            'zh': create_model(model_name="PP-OCRv5_server_rec")
        }

    def recognize(self, image: Image.Image, lang: str) -> str:
        if lang == 'ja':
            return self.mocr(image)
        
        if lang in self.rec_models:
            try:
                # PaddleOCR hoạt động tốt nhất với numpy array (RGB)
                img_np = np.array(image.convert('RGB'))

                pipeline = self.rec_models[lang]
                output = pipeline.predict(img_np)
                
                texts = []
                for res in output:
                    res_dict = res.json if hasattr(res, 'json') else res
                    # Pipeline text_recognition thường trả về 'rec_text' (chuỗi) hoặc 'rec_texts' (mảng)
                    if 'rec_text' in res_dict and isinstance(res_dict['rec_text'], str):
                        texts.append(res_dict['rec_text'])
                    elif 'rec_texts' in res_dict:
                        texts.extend(res_dict['rec_texts'])
                        
                return " ".join(texts)
            except Exception as e:
                print(f"Lỗi OCR {lang}: {e}")
                return ""
            
        return ""
    
    def recognize_full_page(self, image: Image.Image, lang: str) -> list:
        try:
            if lang not in self.full_pipelines:
                return []
                
            img_np = np.array(image.convert('RGB'))
            pipeline = self.full_pipelines[lang]
            output = pipeline.predict(img_np)
            
            parsed_results = []
            for res in output:
                res_dict = res.json if hasattr(res, 'json') else res
                polys = res_dict.get('dt_polys', [])
                texts = res_dict.get('rec_texts', [])
                scores = res_dict.get('rec_scores', [])
                
                for i, poly in enumerate(polys):
                    text = texts[i] if i < len(texts) else ""
                    confidence = scores[i] if i < len(scores) else 0.0
                    
                    if lang == 'ja':
                        x_coords = [p[0] for p in poly]
                        y_coords = [p[1] for p in poly]
                        x_min, x_max = int(max(0, min(x_coords))), int(min(image.width, max(x_coords)))
                        y_min, y_max = int(max(0, min(y_coords))), int(min(image.height, max(y_coords)))
                        if x_max > x_min and y_max > y_min:
                            img_crop = image.crop((x_min, y_min, x_max, y_max))
                            text = self.mocr(img_crop)
                        else:
                            text = ""
                    parsed_results.append({"poly": poly, "text": text, "confidence": float(confidence)})
            return parsed_results
        except Exception as e:
            print(f"Lỗi recognize_full_page {lang}: {e}")
            return []