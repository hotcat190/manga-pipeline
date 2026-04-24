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

def test_is_contained_fully():
    sorter = BoundingBoxSorter()
    inner_box = [100, 100, 900, 900]
    outer_box = [0, 0, 1000, 1000]

    VisualDebugger.visualize_panels([{'box': outer_box}, {'box': inner_box}])
    
    assert sorter._is_contained(inner_box, outer_box) is True

def test_is_contained_greater_than_80_percent():
    sorter = BoundingBoxSorter()
    inner_box = [0, 0, 1000, 1000]
    outer_box = [0, 0, 1000, 900]

    VisualDebugger.visualize_panels([{'box': outer_box}, {'box': inner_box}])
    
    assert sorter._is_contained(inner_box, outer_box) is True

def test_is_contained_exactly_80_percent():
    sorter = BoundingBoxSorter()
    inner_box = [0, 0, 1000, 1000]
    outer_box = [0, 0, 1000, 800]

    VisualDebugger.visualize_panels([{'box': outer_box}, {'box': inner_box}])
    
    assert sorter._is_contained(inner_box, outer_box) is False

def test_is_not_contained_less_than_80_percent():
    sorter = BoundingBoxSorter()
    inner_box = [0, 0, 1000, 1000]
    outer_box = [0, 0, 1000, 500]

    VisualDebugger.visualize_panels([{'box': outer_box}, {'box': inner_box}])
    
    assert sorter._is_contained(inner_box, outer_box) is False

def test_is_not_contained_no_intersection():
    sorter = BoundingBoxSorter()
    inner_box = [0, 0, 1000, 1000]
    outer_box = [2000, 2000, 3000, 3000]

    VisualDebugger.visualize_panels([{'box': outer_box}, {'box': inner_box}])
    
    assert sorter._is_contained(inner_box, outer_box) is False

def test_is_contained_identical_boxes():
    sorter = BoundingBoxSorter()
    inner_box = [0, 0, 1000, 1000]
    outer_box = [0, 0, 1000, 1000]

    VisualDebugger.visualize_panels([{'box': outer_box}, {'box': inner_box}])
    
    assert sorter._is_contained(inner_box, outer_box) is True

def test_is_not_contained_barely_intersect():
    sorter = BoundingBoxSorter()
    inner_box = [259.0, 761.0, 1014.0, 1486.0]
    outer_box = [7.0, 732.0, 265.0, 1585.0]

    VisualDebugger.visualize_panels([{'box': outer_box}, {'box': inner_box}])
    
    assert sorter._is_contained(inner_box, outer_box) is False