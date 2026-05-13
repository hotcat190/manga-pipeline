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

@pytest.fixture
def sorter():
    return BoundingBoxSorter()

def test_empty_data(sorter):
    data = []
    result = sorter._find_gutters(data, "h")
    assert result == []

def test_single_box(sorter):
    data = [{'box': [10, 10, 100, 100]}]
    result = sorter._find_gutters(data, "v")
    assert result == []

def test_clear_vertical_gutter(sorter):
    data = [
        {'box': [0, 0, 100, 100]},
        {'box': [150, 0, 250, 100]}
    ]
    result = sorter._find_gutters(data, "h")
    assert result == [(100, 150)]

def test_clear_horizontal_gutter(sorter):
    data = [
        {'box': [0, 0, 100, 100]},
        {'box': [0, 120, 100, 220]}
    ]
    result = sorter._find_gutters(data, "v")
    assert result == [(100, 120)]

def test_multiple_gutters(sorter):
    data = [
        {'box': [0, 0, 50, 50]},
        {'box': [70, 0, 120, 50]},
        {'box': [150, 0, 200, 50]}
    ]
    result = sorter._find_gutters(data, "h")
    assert result == [(50, 70), (120, 150)]

def test_unsorted_input_data(sorter):
    data = [
        {'box': [150, 0, 250, 100]},
        {'box': [0, 0, 100, 100]}
    ]
    result = sorter._find_gutters(data, "h")
    assert result == [(100, 150)]

def test_overlap_within_tolerance(sorter):
    data = [
        {'box': [0, 0, 100, 100]},
        {'box': [98, 0, 200, 100]}
    ]
    result = sorter._find_gutters(data, "h")
    assert len(result) == 1

def test_overlap_exceeding_tolerance(sorter):
    data = [
        {'box': [0, 0, 100, 100]},
        {'box': [50, 0, 150, 100]}
    ]
    result = sorter._find_gutters(data, "h")
    assert result == []