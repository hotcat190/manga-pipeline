import numpy as np
from ultralytics import YOLO
from typing import List, Dict
from .bounding_box_sorter import BoundingBoxSorter

class PanelDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def detect(self, img_path: str) -> List[Dict]:
        results = self.model.predict(img_path, conf=0.3, verbose=False)
        panels = []
        for box in results[0].boxes:
            coords = box.xyxy[0].cpu().numpy()
            panels.append({
                'box': [int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])],
                'cx': (coords[0] + coords[2]) / 2,
                'cy': (coords[1] + coords[3]) / 2
            })

        return panels
