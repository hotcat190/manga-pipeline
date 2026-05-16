import cv2
import numpy as np
from PIL import Image
from typing import List, Dict

class SomDrawer:
    @staticmethod
    def draw(image_path: str, metadata: List[Dict]) -> Image.Image:
        img_cv = cv2.imread(image_path)
        
        for item in metadata:
            box = item['box']
            box_id = item['id']
            x, y, w, h = box
            
            cv2.rectangle(img_cv, (x, y), (x + w, y + h), (255, 0, 255), 2)            
            
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)