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
            
            cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            font_scale = max(0.8, w / 100)
            thickness = max(2, int(w / 50))
            
            text_size = cv2.getTextSize(str(box_id), cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            bg_x1 = max(0, x - 2)
            bg_y1 = max(0, y - text_size[1] - 5)
            bg_x2 = x + text_size[0] + 2
            bg_y2 = y
            
            cv2.rectangle(img_cv, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 255, 0), -1)
            cv2.putText(img_cv, str(box_id), (x, max(y - 2, 0)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
            
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)