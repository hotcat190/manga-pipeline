import numpy as np
from ultralytics import YOLO
from functools import cmp_to_key
from typing import List, Dict

class PanelDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def detect_and_sort(self, img_path: str) -> List[Dict]:
        results = self.model.predict(img_path, conf=0.3, verbose=False)
        panels = []
        for box in results[0].boxes:
            coords = box.xyxy[0].cpu().numpy()
            panels.append({
                'box': [int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])],
                'cx': (coords[0] + coords[2]) / 2,
                'cy': (coords[1] + coords[3]) / 2
            })

        def cmp_panels(p1, p2):
            p1_left, p1_top, p1_right, p1_bottom = p1['box']
            p2_left, p2_top, p2_right, p2_bottom = p2['box']

            # 1. Check for hard vertical break
            vertical_margin = 20
            if p1_bottom < p2_top + vertical_margin:
                return -1 
            if p2_bottom < p1_top + vertical_margin:
                return 1  

            # 2. Handle column splitting (shared Y space)
            horizontal_margin = 30
            if p1_right > p2_right + horizontal_margin:
                return -1 
            if p2_right > p1_right + horizontal_margin:
                return 1  

            # 3. Same column
            return p1_top - p2_top

        panels.sort(key=cmp_to_key(cmp_panels))
        return panels
