import numpy as np
import logging
from ultralytics import YOLO
from typing import List, Dict
from .bounding_box_sorter import BoundingBoxSorter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PanelDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def detect(self, img_path: str) -> List[Dict]:
        results = self.model.predict(img_path, conf=0.3, verbose=False)
        logger.info(f"Panel Detector predict result len: {len(results)} ")
        logger.info(f"Panel Detector first result boxes len: {len(results[0].boxes)} ")
        panels = []
        for box in results[0].boxes:
            coords = box.xyxy[0].cpu().numpy()
            panels.append({
                'box': [int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])],
                'cx': (coords[0] + coords[2]) / 2,
                'cy': (coords[1] + coords[3]) / 2
            })

        return panels
