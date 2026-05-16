import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict

from simple_lama_inpainting import SimpleLama

from src.engines.base import BaseOcrEngine
from src.common.config import settings
from src.common.visual_debugger import VisualDebugger
from src.common.position_debugger import PositionDebugger

class WebtoonBoxSorter:
    @staticmethod
    def sort(blk_list_raw):
        """
        Sort các text blocks từ trên xuống dưới (trục Y).
        Nếu các block nằm trên cùng một hàng ngang (sai số Y ~30 pixels), 
        thì sort từ trái qua phải (trục X).
        """
        def get_rect(blk):
            poly = blk["poly"]
            x_coords = [p[0] for p in poly]
            y_coords = [p[1] for p in poly]
            x_min, y_min = int(min(x_coords)), int(min(y_coords))
            bw, bh = int(max(x_coords)) - x_min, int(max(y_coords)) - y_min
            return x_min, y_min, bw, bh
            
        blocks_with_rect = [(blk, get_rect(blk)) for blk in blk_list_raw]
        
        # Chia tọa độ Y cho 30 (làm tròn xuống) để gom nhóm các box có Y gần nhau thành "cùng hàng"
        # Sau đó sort ưu tiên 1: Hàng (Y // 30), ưu tiên 2: Tọa độ X
        blocks_with_rect.sort(key=lambda item: (item[1][1] // 30, item[1][0]))
        
        return [item[0] for item in blocks_with_rect]


class WebtoonOcrEngine(BaseOcrEngine):
    def __init__(self, **kwargs):
        self.ocr_service = kwargs.get('ocr_service')
        self.lama = SimpleLama()

    def process(self, image_path: str, source_lang: str) -> Tuple[Image.Image, List[Dict]]:
        img_cv = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_h, img_w = img_cv.shape[:2]

        # 2. Text Detection
        raw_ocr_results = self.ocr_service.recognize_full_page(img_pil, source_lang)

        # 3. Sorting theo Webtoon Logic
        blk_list_sorted = WebtoonBoxSorter.sort(raw_ocr_results)

        final_solid_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        metadata = []
        box_id = 1

        # 4. Processing, Masking & OCR
        for blk in blk_list_sorted:
            poly = blk["poly"]
            text = blk["text"]

            x_coords = [p[0] for p in poly]
            y_coords = [p[1] for p in poly]
            x_min, y_min = max(0, int(min(x_coords))), max(0, int(min(y_coords)))
            x_max, y_max = min(img_w, int(max(x_coords))), min(img_h, int(max(y_coords)))

            poly_np = np.array(poly, dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(final_solid_mask, [poly_np], 255)

            # Build metadata (giữ nguyên format)
            metadata.append({
                "id": box_id,
                "box": [x_min, y_min, x_max - x_min, y_max - y_min],
                "original_text": text
            })
            box_id += 1
            
        if len(blk_list_sorted) > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            final_solid_mask = cv2.dilate(final_solid_mask, kernel, iterations=1)

        # Inpaint xóa chữ
        mask_pil = Image.fromarray(final_solid_mask)
        cleaned_img = self.lama(img_pil, mask_pil)

        VisualDebugger.visualize_text_blocks(metadata, image=img_rgb, name="webtoon_text_blocks")
        PositionDebugger.export_text_blocks(blocks=metadata)

        return cleaned_img, metadata