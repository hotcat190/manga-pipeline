import pytest
from src.engines.manga.bounding_box_sorter import BoundingBoxSorter
from src.common.visual_debugger import VisualDebugger

@pytest.fixture(autouse=True)
def enable_visual_debug(monkeypatch, request):
    monkeypatch.setenv("DEBUG_VISUALIZE", "1")
    VisualDebugger.ENABLED = True
    VisualDebugger.CURRENT_CONTEXT = request.node.name
    yield
    VisualDebugger.CURRENT_CONTEXT = None

def test_empty_panels():
    sorter = BoundingBoxSorter()
    assert sorter.sort([]) == []

def test_standard_grid():
    # 2x2 grid, manga order: top-right (0), top-left (1), bottom-right (2), bottom-left (3)
    panels = [
        {'box': [100, 0, 200, 100]}, # top-right
        {'box': [0, 0, 100, 100]},   # top-left
        {'box': [100, 100, 200, 200]}, # bottom-right
        {'box': [0, 100, 100, 200]}    # bottom-left
    ]
    sorter = BoundingBoxSorter()
    sorted_panels = sorter.sort(panels)

    # Debug visualization        
    VisualDebugger.visualize_panels(sorted_panels)
    
    assert sorted_panels[0]['box'] == [100, 0, 200, 100]
    assert sorted_panels[1]['box'] == [0, 0, 100, 100]
    assert sorted_panels[2]['box'] == [100, 100, 200, 200]
    assert sorted_panels[3]['box'] == [0, 100, 100, 200]

def test_nested_panels():
    # Panel A (large) contains Panel B (small)
    panels = [
        {'box': [0, 0, 200, 200]},   # Panel 0: Large background
        {'box': [50, 50, 100, 100]}, # Panel 1: Nested inside 0
        {'box': [210, 0, 300, 200]}  # Panel 2: To the right of Panel 0 (should come first)
    ]
    sorter = BoundingBoxSorter()
    sorted_panels = sorter.sort(panels)

    # Debug visualization        
    VisualDebugger.visualize_panels(sorted_panels)
    
    # Expected: Panel 2 (rightmost), then Panel 0 (parent), then Panel 1 (child)
    assert sorted_panels[0]['box'] == [210, 0, 300, 200]
    assert sorted_panels[1]['box'] == [0, 0, 200, 200]
    assert sorted_panels[2]['box'] == [50, 50, 100, 100]

def test_l_shape_non_transitive():
    # One large vertical panel on the left, two small ones on the right
    # Manga order: top-right (1), bottom-right (2), then large-left (0)
    panels = [
        {'box': [0, 0, 100, 200]},   # 0: Large vertical on left
        {'box': [110, 0, 200, 90]},  # 1: Small top-right
        {'box': [110, 110, 200, 200]} # 2: Small bottom-right
    ]
    sorter = BoundingBoxSorter()
    sorted_panels = sorter.sort(panels)

    # Debug visualization        
    VisualDebugger.visualize_panels(sorted_panels)
    
    assert sorted_panels[0]['box'] == [110, 0, 200, 90]
    assert sorted_panels[1]['box'] == [110, 110, 200, 200]
    assert sorted_panels[2]['box'] == [0, 0, 100, 200]

def test_dynamic_thresholds():
    # Tiny gap that should be ignored by dynamic thresholds
    # Large high-res panels
    panels = [
        {'box': [1005, 5, 2000, 1000]}, # 0: Right
        {'box': [0, 0, 1000, 905]}      # 1: Left (slightly offset but same row)
    ]
    sorter = BoundingBoxSorter()
    sorted_panels = sorter.sort(panels)

    # Debug visualization        
    VisualDebugger.visualize_panels(sorted_panels)
    
    assert sorted_panels[0]['box'] == [1005, 5, 2000, 1000]
    assert sorted_panels[1]['box'] == [0, 0, 1000, 905]

def test_4koma_layout():
    # 8 panels, 2 columns. Page 1000x1600.
    # Right Column (R): x=[550, 950], Left Column (L): x=[50, 450]
    # Panel size: 400x300. Vertical gap: 100.
    # Horizontal gap between columns: 100.
    
    panels = [
        {'box': [550, 100, 950, 400]},  # R1
        {'box': [550, 500, 950, 800]},  # R2
        {'box': [550, 900, 950, 1200]}, # R3
        {'box': [550, 1300, 950, 1600]},# R4
        {'box': [50, 100, 450, 400]},   # L1
        {'box': [50, 500, 450, 800]},   # L2
        {'box': [50, 900, 450, 1200]},  # L3
        {'box': [50, 1300, 450, 1600]}   # L4
    ]
    
    sorter = BoundingBoxSorter()
    sorted_panels = sorter.sort(panels)

    # Debug visualization        
    VisualDebugger.visualize_panels(sorted_panels)
    
    # Expected: R1, R2, R3, R4, L1, L2, L3, L4
    expected_order = [
        [550, 100, 950, 400],
        [550, 500, 950, 800],
        [550, 900, 950, 1200],
        [550, 1300, 950, 1600],
        [50, 100, 450, 400],
        [50, 500, 450, 800],
        [50, 900, 450, 1200],
        [50, 1300, 450, 1600]
    ]
    
    for i in range(8):
        assert sorted_panels[i]['box'] == expected_order[i], f"Mismatch at index {i}"

def test_edge_case_1():
    # Left panel is "higher" than the Right panel, but on the same row
    panels = [
        {'box': [7.0, 732.0, 265.0, 1585.0]}, # Left
        {'box': [259.0, 761.0, 1014.0, 1486.0]}, # Right
    ]

    sorter = BoundingBoxSorter()
    sorted_panels = sorter.sort(panels)

    VisualDebugger.visualize_panels(sorted_panels)
    expected_order = [
        [259.0, 761.0, 1014.0, 1486.0],
        [7.0, 732.0, 265.0, 1585.0]
    ]
    for i in range(len(panels)):
        assert sorted_panels[i]['box'] == expected_order[i], f"Mismatch at index {i}"
