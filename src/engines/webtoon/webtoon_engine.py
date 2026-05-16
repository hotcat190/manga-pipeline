import cv2
import numpy as np
import torch
from PIL import Image
from typing import Tuple, List, Dict

from simple_lama_inpainting import SimpleLama

from src.engines.base import BaseOcrEngine
from src.common.config import settings
from src.common.visual_debugger import VisualDebugger
from src.common.position_debugger import PositionDebugger

class WebtoonOcrEngine(BaseOcrEngine):
    def __init__(self, **kwargs):
        self.ocr_service = kwargs.get('ocr_service')
        self.lama = SimpleLama()

    def process(self, image_path: str, source_lang: str) -> Tuple[Image.Image, List[Dict]]:
        img_cv = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_h, img_w = img_cv.shape[:2]

        final_solid_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        metadata = []
        box_id = 1

        model = self.ocr_service.rec_models.get(source_lang)
        if not model:
            print(f"Không tìm thấy model cho {source_lang}")
            return img_pil, metadata

        try:
            output = model.predict(image_path)
            
            for res in output:                
                res_json = res.json if hasattr(res, 'json') else res
                print(f"res_json: {res_json}")
                res_dict = res_json['res']
                
                texts = []
                if 'rec_text' in res_dict and isinstance(res_dict['rec_text'], str):
                    texts.append(res_dict['rec_text'])
                elif 'rec_texts' in res_dict:
                    texts.extend(res_dict['rec_texts'])
                    
                polys = []
                if 'dt_polys' in res_dict:
                    polys = res_dict['dt_polys']
                elif 'text_region' in res_dict:
                    polys = res_dict['text_region']
                elif 'text_polys' in res_dict:
                    polys = res_dict['text_polys']
                elif 'rec_polys' in res_dict:
                    polys = res_dict['rec_polys']

                try:
                    res.save_to_img("/local_output/")
                except Exception as e:
                    print(f"Lỗi save_to_img: {e}")

                for i in range(len(texts)):
                    text = texts[i]
                    if i < len(polys):
                        poly = np.array(polys[i], dtype=np.int32)
                        x_min, y_min = np.min(poly[:, 0]), np.min(poly[:, 1])
                        x_max, y_max = np.max(poly[:, 0]), np.max(poly[:, 1])
                        
                        cv2.fillPoly(final_solid_mask, [poly], 255)
                        cv2.polylines(final_solid_mask, [poly], True, 255, 3)
                    else:
                        x_min, y_min, x_max, y_max = 0, 0, 0, 0
                        
                    metadata.append({
                        "id": box_id,
                        "box": [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)],
                        "original_text": text
                    })
                    box_id += 1
                    
        except Exception as e:
            print(f"Lỗi khi chạy PaddleOCR: {e}")

        # Inpaint xóa chữ
        mask_pil = Image.fromarray(final_solid_mask)
        cleaned_img = self.lama(img_pil, mask_pil)

        VisualDebugger.visualize_text_blocks(metadata, image=img_rgb, name="webtoon_text_blocks")
        PositionDebugger.export_text_blocks(blocks=metadata)

        return cleaned_img, metadata