import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from grid.circlegrid import PolygonGrid
from positions import IntPosition
import random

def test_poly() -> None:
    random.seed(97)
    small_grid = PolygonGrid(3, 5)
    assert small_grid.widths == [1, 5, 15, 15]
    assert len(small_grid) == 36
    small_grid.generate_maze('backtrack')
    structure = small_grid.structured_data()
    assert structure['self']   == 'polygonmaze'
    assert structure['radius'] == 3
    assert structure['sides']  == 5
    assert structure['center_cell']  == True
    cells = structure['cells']
    # check a few cells
    assert cells[0] == {'position': [0, 0], 'links': [[1, 0], [1, 2]]}
    assert cells[1] == {'position': [1, 0], 'links': [[0, 0], [2, 0]]}
    assert cells[2] == {'position': [1, 1], 'links': [[2, 3], [2, 5]]}

    path = small_grid.longest_path()
    assert len(path) == 27
    if path[0] < path[-1]:
        path = list(reversed(path))
    assert path[0] == IntPosition((3, 2))
    assert path[-1] == IntPosition((2, 6))

    field = small_grid.dijkstra(IntPosition((0, 0)))
    assert len(field) == 22
    assert field[:4] == [
        {IntPosition ((0, 0))},
        {IntPosition ((1, 0)), IntPosition((1, 2))},
        {IntPosition ((2, 0)), IntPosition((2, 7))},
        {IntPosition ((3, 7)), IntPosition((2, 14))},
    ]

    bbox = small_grid.bounding_box
    assert bbox[2] == 3.5

    edges = small_grid.edges
    assert len(edges) == 5
    assert len(edges[0].inner) == 3
    assert edges[0].inner[0] in small_grid
    assert edges[0].outer[0] not in small_grid

    partial_grid = PolygonGrid(3, 5, slices=4)
    assert partial_grid.widths == [1, 5, 15, 15]
    assert len(partial_grid) == 29
