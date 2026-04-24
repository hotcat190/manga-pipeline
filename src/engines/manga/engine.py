import cv2
import numpy as np
import torch
from PIL import Image
from typing import Tuple, List, Dict

from comic_text_detector.inference import TextDetector
from manga_ocr import MangaOcr
from simple_lama_inpainting import SimpleLama

from src.engines.base import BaseOcrEngine
from src.common.config import settings
from .panel_detector import PanelDetector
from .text_processor import TextProcessor
from .bounding_box_sorter import BoundingBoxSorter
from src.common.visual_debugger import VisualDebugger
from src.common.position_debugger import PositionDebugger

class MangaOcrEngine(BaseOcrEngine):
    def __init__(self):
        self.panel_detector = PanelDetector(settings.PANEL_MODEL_PATH)
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.text_detector = TextDetector(
            model_path=settings.TEXT_DETECTION_MODEL_PATH, 
            device=device, 
            act='leaky'
        )
        self.mocr = MangaOcr()
        self.lama = SimpleLama()
        self.bounding_box_sorter = BoundingBoxSorter()

    def process(self, image_path: str) -> Tuple[Image.Image, List[Dict]]:
        img_cv = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_h, img_w = img_cv.shape[:2]

        # 1. Detect and sort panels
        panels = self.panel_detector.detect(image_path)
        VisualDebugger.visualize_panels(panels, image=img_rgb, name="pipeline_panels_unsorted")
        PositionDebugger.export_panels(panels=panels, name="panels_unsorted")

        sorted_panels = self.bounding_box_sorter.sort(panels)
        VisualDebugger.visualize_panels(sorted_panels, image=img_rgb, name="pipeline_panels_sorted")
        PositionDebugger.export_panels(panels=panels, name="panels_sorted")
        
        # 2. Detect text blocks
        mask_raw, _, blk_list_raw = self.text_detector(img_cv, refine_mode=1, keep_undetected_mask=True)

        # 3. Assign and sort text blocks based on panels
        blk_list_sorted = TextProcessor.assign_and_sort(blk_list_raw, sorted_panels)

        final_solid_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        metadata = []
        box_id = 1

        for blk in blk_list_sorted:
            bx, by, bw, bh = [int(val.item()) for val in blk.bounding_rect()]

            pad_l, pad_r, pad_t, pad_b = 5, 20, 15, 5
            x_min, y_min = max(0, bx - pad_l), max(0, by - pad_t)
            x_max, y_max = min(img_w, bx + bw + pad_r), min(img_h, by + bh + pad_b)

            # 4. Filter invalid regions
            if not TextProcessor.is_valid_text_region(img_cv, (x_min, y_min, x_max, y_max)):
                continue

            # 5. Build inpainting mask
            roi_mask = mask_raw[y_min:y_max, x_min:x_max]
            contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                all_pts = np.vstack(contours)
                hull_offset = cv2.convexHull(all_pts) + [x_min, y_min]
                cv2.drawContours(final_solid_mask, [hull_offset], -1, 255, -1)
                cv2.drawContours(final_solid_mask, [hull_offset], -1, 255, 3)

            # 6. OCR
            try: 
                text = self.mocr(img_pil.crop((x_min, y_min, x_max, y_max)))
            except Exception: 
                text = ""

            metadata.append({
                "id": box_id,
                "box": [x_min, y_min, x_max - x_min, y_max - y_min],
                "original_text": text
            })
            box_id += 1

        # 7. Inpaint
        mask_pil = Image.fromarray(final_solid_mask)
        cleaned_img = self.lama(img_pil, mask_pil)

        VisualDebugger.visualize_text_blocks(metadata, image=img_rgb, name="pipeline_text_blocks")
        PositionDebugger.export_text_blocks(blocks=metadata)

        return cleaned_img, metadata
