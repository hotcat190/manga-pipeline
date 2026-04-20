import cv2
import numpy as np
from PIL import Image
from functools import cmp_to_key
from typing import Tuple, List, Dict
import torch

from comic_text_detector.inference import TextDetector
from manga_ocr import MangaOcr
from simple_lama_inpainting import SimpleLama
from ultralytics import YOLO
from .base import BaseOcrEngine

torch.backends.cudnn.enabled = False

class MangaOcrEngine(BaseOcrEngine):
    def __init__(self):
        self.panel_detector = YOLO("yolov12x_panels.pt")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.text_detector = TextDetector(model_path="comictextdetector.pt", device=device, act='leaky')
        self.mocr = MangaOcr()
        self.lama = SimpleLama()

    def get_panels(self, img_path):
        results = self.panel_detector.predict(img_path, conf=0.3, verbose=False)
        panels = []
        for box in results[0].boxes:
            coords = box.xyxy[0].cpu().numpy()
            panels.append({
                'box': [int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])],
                'cx': (coords[0] + coords[2]) / 2,
                'cy': (coords[1] + coords[3]) / 2
            })

        # --- LOGIC SORT PANELS MỚI (CHUẨN MANGA) ---
        def cmp_panels(p1, p2):
            p1_left, p1_top, p1_right, p1_bottom = p1['box']
            p2_left, p2_top, p2_right, p2_bottom = p2['box']

            # 1. Kiểm tra ranh giới cắt ngang cứng (Hard Vertical Break)
            vertical_margin = 20
            if p1_bottom < p2_top + vertical_margin:
                return -1 
            if p2_bottom < p1_top + vertical_margin:
                return 1  

            # 2. Xử lý chia cột (Có chia sẻ không gian theo trục Y)
            horizontal_margin = 30
            if p1_right > p2_right + horizontal_margin:
                return -1 
            if p2_right > p1_right + horizontal_margin:
                return 1  

            # 3. Nằm chung một cột (Cạnh phải gần bằng nhau)
            return p1_top - p2_top

        panels.sort(key=cmp_to_key(cmp_panels))
        return panels

    def assign_and_sort_texts(self, blk_list, panels):
        boxes_info = []
        for blk in blk_list:
            bx, by, bw, bh = [int(v.item()) for v in blk.bounding_rect()]
            boxes_info.append({'blk': blk, 'box': [bx, by, bw, bh], 'cx': bx + bw/2, 'cy': by + bh/2})

        panel_groups = {i: [] for i in range(len(panels))}
        unassigned = []

        for box in boxes_info:
            assigned = False
            for i, p in enumerate(panels):
                px1, py1, px2, py2 = p['box']
                if px1 <= box['cx'] <= px2 and py1 <= box['cy'] <= py2:
                    panel_groups[i].append(box)
                    assigned = True
                    break
            if not assigned:
                unassigned.append(box)

        def cmp_texts(b1, b2):
            if b1['box'][1] + b1['box'][3] < b2['box'][1] - 40: return -1
            if b2['box'][1] + b2['box'][3] < b1['box'][1] - 40: return 1
            return b2['box'][0] - b1['box'][0]

        final_sorted_blocks = []
        for i in range(len(panels)):
            panel_groups[i].sort(key=cmp_to_key(cmp_texts))
            final_sorted_blocks.extend([b['blk'] for b in panel_groups[i]])

        unassigned.sort(key=cmp_to_key(cmp_texts))
        final_sorted_blocks.extend([b['blk'] for b in unassigned])

        return final_sorted_blocks, panels

    def process(self, image_path: str) -> Tuple[Image.Image, List[Dict]]:
        img_cv = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_h, img_w = img_cv.shape[:2]

        panels = self.get_panels(image_path)
        mask_raw, _, blk_list_raw = self.text_detector(img_cv, refine_mode=1, keep_undetected_mask=True)

        blk_list_sorted, _ = self.assign_and_sort_texts(blk_list_raw, panels)

        final_solid_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        metadata = []
        box_id = 1

        for blk in blk_list_sorted:
            bx, by, bw, bh = [int(val.item()) for val in blk.bounding_rect()]

            pad_l, pad_r, pad_t, pad_b = 5, 20, 15, 5
            x_min, y_min = max(0, bx - pad_l), max(0, by - pad_t)
            x_max, y_max = min(img_w, bx + bw + pad_r), min(img_h, by + bh + pad_b)

            roi_gray = cv2.cvtColor(img_cv[y_min:y_max, x_min:x_max], cv2.COLOR_BGR2GRAY)
            total_pixels = roi_gray.shape[0] * roi_gray.shape[1]

            if total_pixels == 0: continue

            white_pixels = np.sum(roi_gray > 210)
            white_ratio = white_pixels / total_pixels

            if white_ratio < 0.45:
                continue

            roi_mask = mask_raw[y_min:y_max, x_min:x_max]
            contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                all_pts = np.vstack(contours)
                hull_offset = cv2.convexHull(all_pts) + [x_min, y_min]
                cv2.drawContours(final_solid_mask, [hull_offset], -1, 255, -1)
                cv2.drawContours(final_solid_mask, [hull_offset], -1, 255, 3)

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

        mask_pil = Image.fromarray(final_solid_mask)
        cleaned_img = self.lama(img_pil, mask_pil)

        return cleaned_img, metadata