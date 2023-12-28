import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from grid.rectgrid import RectGrid
from positions import IntPosition
import random

def test_rect() -> None:
    random.seed(97)
    small_grid = RectGrid(3, 4)
    assert len(small_grid) == 12
    small_grid.generate_maze('binary')
    structure = small_grid.structured_data()
    assert structure['self'] == 'rectmaze'
    assert structure['width'] == 4
    assert structure['height'] == 3
    cells = structure['cells']
    assert cells == [
        {'position': [0, 0], 'links': [[1, 0]]},
        {'position': [0, 1], 'links': [[1, 1]]},
        {'position': [0, 2], 'links': [[1, 2]]},
        {'position': [1, 0], 'links': [[0, 0], [1, 1]]},
        {'position': [1, 1], 'links': [[0, 1], [1, 0], [2, 1]]},
        {'position': [1, 2], 'links': [[0, 2], [2, 2]]},
        {'position': [2, 0], 'links': [[2, 1]]},
        {'position': [2, 1], 'links': [[1, 1], [2, 0], [3, 1]]},
        {'position': [2, 2], 'links': [[1, 2], [3, 2]]},
        {'position': [3, 0], 'links': [[3, 1]]},
        {'position': [3, 1], 'links': [[2, 1], [3, 0], [3, 2]]},
        {'position': [3, 2], 'links': [[2, 2], [3, 1]]}
    ]

    path = small_grid.longest_path()
    expected_path = [
        IntPosition((0, 2)),
        IntPosition((1, 2)),
        IntPosition((2, 2)),
        IntPosition((3, 2)),
        IntPosition((3, 1)),
        IntPosition((2, 1)),
        IntPosition((1, 1)),
        IntPosition((1, 0)),
        IntPosition((0, 0)),
    ]
    assert path in (expected_path, list(reversed(expected_path)))
