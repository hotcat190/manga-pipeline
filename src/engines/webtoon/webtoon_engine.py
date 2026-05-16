import cv2
import numpy as np
import os
from datetime import datetime
from PIL import Image
from typing import Tuple, List, Dict

from simple_lama_inpainting import SimpleLama

from src.engines.base import BaseOcrEngine
from src.common.config import settings
from src.common.visual_debugger import VisualDebugger
from src.common.position_debugger import PositionDebugger

DEBUG = os.getenv("DEBUG_VISUALIZE", "0") == "1"

class WebtoonOcrEngine(BaseOcrEngine):
    def __init__(self, **kwargs):
        self.ocr_service = kwargs.get('ocr_service')
        self.lama = SimpleLama()

    def _cluster_text_blocks(self, metadata: List[Dict], threshold: float = 60.0) -> List[Dict]:
        if not metadata:
            return []
        
        parent = {i: i for i in range(len(metadata))}
        
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        def get_center(box):
            return (box[0] + box[2] / 2, box[1] + box[3] / 2)

        for i in range(len(metadata)):
            for j in range(i + 1, len(metadata)):
                c1 = get_center(metadata[i]["box"])
                c2 = get_center(metadata[j]["box"])
                dist = ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5
                if dist < threshold:
                    union(i, j)

        clusters = {}
        for i in range(len(metadata)):
            root = find(i)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(metadata[i])

        merged_metadata = []
        new_id = 1
        for root, items in clusters.items():
            items.sort(key=lambda x: x["box"][1])
            
            min_x = min(item["box"][0] for item in items)
            min_y = min(item["box"][1] for item in items)
            max_x = max(item["box"][0] + item["box"][2] for item in items)
            max_y = max(item["box"][1] + item["box"][3] for item in items)
            
            combined_text = " ".join([item["original_text"] for item in items])
            
            merged_metadata.append({
                "id": new_id,
                "box": [min_x, min_y, max_x - min_x, max_y - min_y],
                "original_text": combined_text
            })
            new_id += 1
            
        return merged_metadata

    def process(self, image_path: str, source_lang: str) -> Tuple[Image.Image, List[Dict]]:
        img_cv = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_h, img_w = img_cv.shape[:2]

        final_solid_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        metadata = []
        box_id = 0

        model = self.ocr_service.rec_models.get(source_lang)
        if not model:
            print(f"Không tìm thấy model cho {source_lang}")
            return img_pil, metadata

        try:
            output = model.predict(
                image_path,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
            )
            
            for res in output:                
                res_json = res.json if hasattr(res, 'json') else res
                print(f"res_json: {res_json}")
                res_dict = res_json['res']
                
                texts = []
                if 'rec_text' in res_dict and isinstance(res_dict['rec_text'], str):
                    texts.append(res_dict['rec_text'])
                elif 'rec_texts' in res_dict:
                    texts.extend(res_dict['rec_texts'])
                    
                polys = []
                if 'dt_polys' in res_dict:
                    polys = res_dict['dt_polys']
                elif 'text_region' in res_dict:
                    polys = res_dict['text_region']
                elif 'text_polys' in res_dict:
                    polys = res_dict['text_polys']
                elif 'rec_polys' in res_dict:
                    polys = res_dict['rec_polys']

                try:
                    if DEBUG:
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        output_dir = os.path.join("local_output", "paddle_debug", timestamp)
                        res.save_to_img(output_dir)
                except Exception as e:
                    print(f"Lỗi save_to_img: {e}")

                for i in range(len(texts)):
                    text = texts[i]
                    if i < len(polys):
                        poly = np.array(polys[i], dtype=np.int32)
                        x_min, y_min = np.min(poly[:, 0]), np.min(poly[:, 1])
                        x_max, y_max = np.max(poly[:, 0]), np.max(poly[:, 1])
                        
                        cv2.fillPoly(final_solid_mask, [poly], 255)
                        cv2.polylines(final_solid_mask, [poly], True, 255, 3)
                    else:
                        x_min, y_min, x_max, y_max = 0, 0, 0, 0
                        
                    metadata.append({
                        "id": box_id,
                        "box": [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)],
                        "original_text": text
                    })
                    box_id += 1
                    
        except Exception as e:
            print(f"Lỗi khi chạy PaddleOCR: {e}")

        clustered_metadata = self._cluster_text_blocks(metadata)

        # Inpaint xóa chữ
        mask_pil = Image.fromarray(final_solid_mask)
        cleaned_img = self.lama(img_pil, mask_pil)

        VisualDebugger.visualize_text_blocks(clustered_metadata, image=img_rgb, name="webtoon_text_blocks")
        PositionDebugger.export_text_blocks(blocks=clustered_metadata)

        return cleaned_img, clustered_metadata