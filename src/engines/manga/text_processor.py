import cv2
import numpy as np
from functools import cmp_to_key
from typing import List, Dict, Tuple

class TextProcessor:
    @staticmethod
    def assign_and_sort(blk_list, panels: List[Dict]):
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

        return final_sorted_blocks

    @staticmethod
    def is_valid_text_region(img_cv: np.ndarray, box: Tuple[int, int, int, int], threshold: float = 0.45) -> bool:
        x_min, y_min, x_max, y_max = box
        roi_gray = cv2.cvtColor(img_cv[y_min:y_max, x_min:x_max], cv2.COLOR_BGR2GRAY)
        total_pixels = roi_gray.shape[0] * roi_gray.shape[1]

        if total_pixels == 0:
            return False

        white_pixels = np.sum(roi_gray > 210)
        white_ratio = white_pixels / total_pixels
        return white_ratio >= threshold
