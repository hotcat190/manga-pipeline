import os
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from typing import List, Dict, Union, Optional

class VisualDebugger:
    """
    Utility for visualizing bounding boxes and pipeline steps.
    Only active if DEBUG_VISUALIZE=1 environment variable is set.
    """
    
    ENABLED = os.getenv("DEBUG_VISUALIZE", "0") == "1"
    OUTPUT_DIR = "local_output/debug"
    SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
    CURRENT_CONTEXT = None  # Global name override

    @classmethod
    def _ensure_dir(cls, subpath: str = ""):
        path = os.path.join(cls.OUTPUT_DIR, subpath)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def visualize_panels(
        cls, 
        panels: List[Dict], 
        image: Optional[Union[np.ndarray, Image.Image]] = None, 
        name: str = "panels"
    ):
        if not cls.ENABLED:
            return

        cls._ensure_dir(cls.SESSION_ID)
        
        # 1. Prepare base image
        if image is None:
            # Create a blank canvas if no image provided (for unit tests)
            max_x = max([p['box'][2] for p in panels]) + 50 if panels else 500
            max_y = max([p['box'][3] for p in panels]) + 50 if panels else 500
            canvas = np.ones((int(max_y), int(max_x), 3), dtype=np.uint8) * 255
        elif isinstance(image, Image.Image):
            canvas = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            canvas = image.copy()

        # 2. Draw panels
        for i, panel in enumerate(panels):
            box = panel['box']
            # Box format [x1, y1, x2, y2]
            x1, y1, x2, y2 = map(int, box)
            
            # Draw rectangle
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw index/order
            label = f"#{i+1}"
            cv2.putText(
                canvas, label, (x1 + 5, y1 + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2
            )

        # 3. Save
        final_name = cls.CURRENT_CONTEXT if cls.CURRENT_CONTEXT else name
        filename = f"{final_name}.png"
        filepath = os.path.join(cls.OUTPUT_DIR, cls.SESSION_ID, filename)
        cv2.imwrite(filepath, canvas)
        print(f"[DEBUG] Visualized {len(panels)} panels to {filepath}")

    @classmethod
    def visualize_text_blocks(
        cls, 
        blocks: List[Dict], 
        image: Union[np.ndarray, Image.Image], 
        name: str = "text_blocks"
    ):
        if not cls.ENABLED:
            return

        cls._ensure_dir(cls.SESSION_ID)

        if isinstance(image, Image.Image):
            canvas = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            canvas = image.copy()

        for i, block in enumerate(blocks):
            box = block['box']
            # Box format [x, y, w, h] (assuming from engine.py metadata)
            x, y, w, h = map(int, box)
            
            cv2.rectangle(canvas, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(
                canvas, str(i+1), (x + 2, y + 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )

        timestamp = datetime.now().strftime("%H%M%S")
        final_name = cls.CURRENT_CONTEXT if cls.CURRENT_CONTEXT else name
        filename = f"{final_name}.png"
        filepath = os.path.join(cls.OUTPUT_DIR, cls.SESSION_ID, filename)
        cv2.imwrite(filepath, canvas)
        print(f"[DEBUG] Visualized {len(blocks)} text blocks to {filepath}")
