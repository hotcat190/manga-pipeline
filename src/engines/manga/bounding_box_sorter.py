import statistics
from collections import defaultdict
from typing import List, Dict
from functools import cmp_to_key

class BoundingBoxSorter:
    """
    Handles sorting of manga panels/texts bounding boxes based on their spatial coordinates using a recursive XY cut algorithm.
    """
    
    def sort(self, boxes: List[Dict]) -> List[Dict]:
        """
        Sorts boxes using a recursive XY cut algorithm.
        
        Args:
            boxes: List of boxes containing 'box'.
            
        Returns:
            List[Dict]: The sorted list of boxes.
        """
        if not boxes:
            return []
            
        # 1. Dynamic Metrics for relative thresholds
        widths = [p['box'][2] - p['box'][0] for p in boxes]
        heights = [p['box'][3] - p['box'][1] for p in boxes]
        median_w = statistics.median(widths) if widths else 0
        median_h = statistics.median(heights) if heights else 0
        
        # Thresholds (e.g., 20% of median size)
        y_overlap_threshold = 0.25 
        
        # 2. Containment Analysis (Encapsulation)
        # Find boxes that are inside other boxes
        parent_indices = []
        children_map = defaultdict(list) # parent_idx -> list of child_indices
        
        for i, p1 in enumerate(boxes):
            is_child = False
            for j, p2 in enumerate(boxes):
                if i == j: continue
                if self._is_contained(p1['box'], p2['box']):
                    children_map[j].append(i)
                    is_child = True
                    break
            if not is_child:
                parent_indices.append(i)
                
        # 3. Sort parent panels using Recursive XY Cut
        parent_data = [{'original_idx': i, 'box': boxes[i]['box']} for i in parent_indices]
        sorted_parent_data = self._recursive_xy_cut(parent_data)
        
        # 4. Final Sequence with Children
        result_boxes = []
        for item in sorted_parent_data:
            idx = item['original_idx']
            result_boxes.append(boxes[idx])
            # Add and sort children of this box
            if idx in children_map:
                child_indices = children_map[idx]
                # Sort children: top-to-bottom, then right-to-left
                child_indices.sort(key=lambda c_idx: (boxes[c_idx]['box'][1], -boxes[c_idx]['box'][2]))
                for c_idx in child_indices:
                    result_boxes.append(boxes[c_idx])
                    
        return result_boxes

    def _recursive_xy_cut(self, data: List[Dict]) -> List[Dict]:
        if len(data) <= 1:
            return data
            
        # Find all possible gutters
        h_gutters = self._find_gutters(data, 'h')
        v_gutters = self._find_gutters(data, 'v')
        
        if not h_gutters and not v_gutters:
            # No clean cut possible (overlapping boxes or complex layout)
            # Fallback to simple topological heuristic
            def fallback_cmp(a, b):
                y_overlap = min(a['box'][3], b['box'][3]) - max(a['box'][1], b['box'][1])
                min_height = min(a['box'][3] - a['box'][1], b['box'][3] - b['box'][1])
                if min_height > 0 and (y_overlap / min_height) > 0.5:
                    return b['box'][2] - a['box'][2]
                return a['box'][1] - b['box'][1]
            data.sort(key=cmp_to_key(fallback_cmp))
            return data
            
        # Choose the "best" gutter
        # We prioritize the longest gutter. If tied, prefer horizontal (manga rows)
        best_gutter = None
        max_score = -1
        
        # Page bounds for scoring
        min_x = min(d['box'][0] for d in data)
        max_x = max(d['box'][2] for d in data)
        min_y = min(d['box'][1] for d in data)
        max_y = max(d['box'][3] for d in data)
        page_w = max_x - min_x
        page_h = max_y - min_y
        
        for g in h_gutters:
            # Score = width * gap_height. Since we only care about relative, width is enough
            # if we assume standard manga priority.
            score = page_w * (g[1] - g[0] + 1) # add 1 to avoid 0-width issues
            if score > max_score:
                max_score = score
                best_gutter = ('h', (g[0] + g[1]) / 2)
                
        for g in v_gutters:
            # Vertical score = height * gap_width.
            # We give horizontal a slight edge in case of tie.
            score = page_h * (g[1] - g[0])
            if score > max_score:
                max_score = score
                best_gutter = ('v', (g[0] + g[1]) / 2)
                
        # Split and recurse
        direction, pos = best_gutter
        if direction == 'h':
            # Horizontal cut: top-to-bottom
            top = [d for d in data if d['box'][3] <= pos]
            bottom = [d for d in data if d['box'][1] >= pos]
            return self._recursive_xy_cut(top) + self._recursive_xy_cut(bottom)
        else:
            # Vertical cut: right-to-left
            left = [d for d in data if d['box'][2] <= pos]
            right = [d for d in data if d['box'][0] >= pos]
            return self._recursive_xy_cut(right) + self._recursive_xy_cut(left)

    def _find_gutters(self, data: List[Dict], direction: str) -> List[tuple]:
        """Finds ranges of empty space that span the entire block."""
        if direction == 'h':
            # Sort boxes by Y
            intervals = sorted([(d['box'][1], d['box'][3]) for d in data])
            min_bound, max_bound = min(d['box'][1] for d in data), max(d['box'][3] for d in data)
        else:
            # Sort boxes by X
            intervals = sorted([(d['box'][0], d['box'][2]) for d in data])
            min_bound, max_bound = min(d['box'][0] for d in data), max(d['box'][2] for d in data)
            
        # Find gaps in intervals
        gutters = []
        curr_max = intervals[0][1]
        for i in range(1, len(intervals)):
            if intervals[i][0] > curr_max:
                gutters.append((curr_max, intervals[i][0]))
            curr_max = max(curr_max, intervals[i][1])
            
        return gutters

    def _is_contained(self, inner: List[int], outer: List[int]) -> bool:
        """Checks if 'inner' box is significantly contained within 'outer' box."""
        ix1, iy1, ix2, iy2 = inner
        ox1, oy1, ox2, oy2 = outer
        
        # Intersection area
        inter_x1 = max(ix1, ox1)
        inter_y1 = max(iy1, oy1)
        inter_x2 = min(ix2, ox2)
        inter_y2 = min(iy2, oy2)
        
        if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
            return False
            
        inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
        inner_area = (ix2 - ix1) * (iy2 - iy1)
        
        return (inter_area / inner_area) > 0.8
