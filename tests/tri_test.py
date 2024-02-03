import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from maze.hexgrid import TriGrid
from maze.positions import IntPosition as IntPos
from maze.grid import Edge
import random

def test_rect() -> None:
    random.seed(97)
    small_grid = TriGrid(3)
    assert len(small_grid) == 9

    edges = small_grid.edges
    assert edges == (
        Edge((
                IntPos((4, 2)), IntPos((3, 3)), IntPos((2, 4))
            ), (
                IntPos((5, 3)), IntPos((4, 4)), IntPos((3, 5))
        )),
        Edge((
                IntPos((2, 4)), IntPos((1, 2)), IntPos((0, 0))
            ), (
                IntPos((1, 4)), IntPos((0, 2)), IntPos((-1, 0))
        )),
        Edge((
                IntPos((0, 0)), IntPos((2, 1)), IntPos((4, 2)),
            ), (
                IntPos((0, -1)), IntPos((2, 0)), IntPos((4, 1)),
        )),
    )

    small_grid.generate_maze('wilson')
    structure = small_grid.structured_data()
    assert structure['self'] == 'trimaze'
    assert structure['width'] == 3

    path = small_grid.longest_path()
    expected_path = [
        IntPos((4, 2)),
        IntPos((3, 2)),
        IntPos((3, 3)),
        IntPos((2, 3)),
        IntPos((1, 2)),
        IntPos((1, 1)),
        IntPos((0, 0)),
    ]
    if path[0] < path[-1]:
        path = list(reversed(path))
    assert path == expected_path

    field = small_grid.dijkstra(IntPos((0, 0)))
    assert field == [
        {IntPos((0, 0))},
        {IntPos((1, 1))},
        {IntPos((1, 2)), IntPos((2, 1))},
        {IntPos((2, 3))},
        {IntPos((2, 4)), IntPos((3, 3))},
        {IntPos((3, 2))},
        {IntPos((4, 2))},
    ]
