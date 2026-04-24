import os
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Union, Optional, Any

class PositionDebugger:
    ENABLED = os.getenv("DEBUG_VISUALIZE", "0") == "1"
    OUTPUT_DIR = "local_output/debug"
    SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
    CURRENT_CONTEXT = None

    @classmethod
    def _ensure_dir(cls, subpath: str = ""):
        path = os.path.join(cls.OUTPUT_DIR, subpath)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def _write_json(cls, data: Any, name: str, item_count: int, prefix: str = ""):
        if not cls.ENABLED:
            return
            
        cls._ensure_dir(cls.SESSION_ID)
        final_name = cls.CURRENT_CONTEXT if cls.CURRENT_CONTEXT else name
        filename = f"{final_name}.json"
        filepath = os.path.join(cls.OUTPUT_DIR, cls.SESSION_ID, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"[DEBUG] Exported {item_count} {prefix} to {filepath}")

    @classmethod
    def export_panels(
        cls, 
        panels: List[Dict], 
        image: Optional[Any] = None, 
        name: str = "panels"
    ):
        if not cls.ENABLED:
            return
            
        data = []
        for i, panel in enumerate(panels):
            box = [float(x) for x in panel['box']]
            data.append({
                "id": i + 1,
                "box": box,
                "format": "[x1, y1, x2, y2]"
            })
            
        cls._write_json(data, name, len(panels), "panels")

    @classmethod
    def export_text_blocks(
        cls, 
        blocks: List[Dict], 
        image: Optional[Any] = None, 
        name: str = "text_blocks"
    ):
        if not cls.ENABLED:
            return

        data = []
        for i, block in enumerate(blocks):
            box = [float(x) for x in block['box']]
            data.append({
                "id": i + 1,
                "box": box,
                "format": "[x, y, w, h]"
            })
            
        cls._write_json(data, name, len(blocks), "text blocks")

    @classmethod
    def export_obb(
        cls, 
        obb_boxes: List[np.ndarray], 
        image: Optional[Any] = None, 
        name: str = "obb_results"
    ):
        if not cls.ENABLED:
            return

        data = []
        for i, box in enumerate(obb_boxes):
            pts = box.reshape((-1, 2)).tolist()
            data.append({
                "id": i + 1,
                "box": pts,
                "format": "Polygon points [[x1, y1], [x2, y2], ...]"
            })

        cls._write_json(data, name, len(obb_boxes), "OBBs")