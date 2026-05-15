import cv2
import numpy as np
import torch
from PIL import Image
from typing import Tuple, List, Dict

from comic_text_detector.inference import TextDetector
from simple_lama_inpainting import SimpleLama

from src.engines.base import BaseOcrEngine
from src.common.config import settings
from src.engines.manga.text_processor import TextProcessor
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
            bx, by, bw, bh = [int(val.item()) for val in blk.bounding_rect()]
            return bx, by, bw, bh
            
        blocks_with_rect = [(blk, get_rect(blk)) for blk in blk_list_raw]
        
        # Chia tọa độ Y cho 30 (làm tròn xuống) để gom nhóm các box có Y gần nhau thành "cùng hàng"
        # Sau đó sort ưu tiên 1: Hàng (Y // 30), ưu tiên 2: Tọa độ X
        blocks_with_rect.sort(key=lambda item: (item[1][1] // 30, item[1][0]))
        
        return [item[0] for item in blocks_with_rect]


class WebtoonOcrEngine(BaseOcrEngine):
    def __init__(self, **kwargs):
        # 1. Bỏ qua PanelDetector, chỉ dùng TextDetector
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.text_detector = TextDetector(
            model_path=settings.TEXT_DETECTION_MODEL_PATH, 
            device=device, 
            act='leaky'
        )
        self.ocr_service = kwargs.get('ocr_service')
        self.lama = SimpleLama()

    def process(self, image_path: str, source_lang: str) -> Tuple[Image.Image, List[Dict]]:
        img_cv = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_h, img_w = img_cv.shape[:2]

        # 2. Text Detection
        mask_raw, _, blk_list_raw = self.text_detector(img_cv, refine_mode=1, keep_undetected_mask=True)

        # 3. Sorting theo Webtoon Logic
        blk_list_sorted = WebtoonBoxSorter.sort(blk_list_raw)

        final_solid_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        metadata = []
        box_id = 1

        # 4. Processing, Masking & OCR
        for blk in blk_list_sorted:
            bx, by, bw, bh = [int(val.item()) for val in blk.bounding_rect()]

            pad_l, pad_r, pad_t, pad_b = 5, 20, 15, 5
            x_min, y_min = max(0, bx - pad_l), max(0, by - pad_t)
            x_max, y_max = min(img_w, bx + bw + pad_r), min(img_h, by + bh + pad_b)

            # Lọc vùng không hợp lệ (tái sử dụng từ Manga)
            if not TextProcessor.is_valid_text_region(img_cv, (x_min, y_min, x_max, y_max)):
                continue

            # Xây dựng inpainting mask
            roi_mask = mask_raw[y_min:y_max, x_min:x_max]
            contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                all_pts = np.vstack(contours)
                hull_offset = cv2.convexHull(all_pts) + [x_min, y_min]
                cv2.drawContours(final_solid_mask, [hull_offset], -1, 255, -1)
                cv2.drawContours(final_solid_mask, [hull_offset], -1, 255, 3)

            # Gọi OCR thông qua OcrService đa ngôn ngữ
            try: 
                img_crop = img_pil.crop((x_min, y_min, x_max, y_max))
                text = self.ocr_service.recognize(img_crop, source_lang)
            except Exception as e: 
                print(f"Lỗi OCR tại box {box_id}: {e}")
                text = ""

            # Build metadata (giữ nguyên format)
            metadata.append({
                "id": box_id,
                "box": [x_min, y_min, x_max - x_min, y_max - y_min],
                "original_text": text
            })
            box_id += 1

        # Inpaint xóa chữ
        mask_pil = Image.fromarray(final_solid_mask)
        cleaned_img = self.lama(img_pil, mask_pil)

        VisualDebugger.visualize_text_blocks(metadata, image=img_rgb, name="webtoon_text_blocks")
        PositionDebugger.export_text_blocks(blocks=metadata)

        return cleaned_img, metadata