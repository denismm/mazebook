import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from maze.circlegrid import SemiCircleGrid
from positions import IntPosition as IntPos
import random

def test_semi() -> None:
    random.seed(97)
    even_semicircle = SemiCircleGrid(6)
    assert even_semicircle.widths == [6, 12, 12]
    assert len(even_semicircle) == 15
    structure = even_semicircle.structured_data()
    assert structure['radius'] == 3
    assert structure['degrees']  == 180.0
    assert structure['center_cell']  == False

    edges = even_semicircle.edges
    assert len(edges) == 1
    assert len(edges[0].inner) == 6
    assert edges[0].inner == (
        IntPos((2,6)), IntPos((1,6)), IntPos((0,3)),
        IntPos((0,0)), IntPos((1,0)), IntPos((2,0)),
    )
    assert edges[0].outer == (
        IntPos((2,7)), IntPos((1,7)), IntPos((0,4)),
        IntPos((0,-1)), IntPos((1,-1)), IntPos((2,-1)),
    )

    assert even_semicircle.pos_adjacents(IntPos((0,0))) == [
        IntPos((0, 1)),
        IntPos((0, -1)),
        IntPos((1, 0)),
        IntPos((1, 1)),
    ]

    odd_semicircle = SemiCircleGrid(5)
    assert odd_semicircle.widths == [1, 6, 12]
    assert len(odd_semicircle) == 10
    structure = odd_semicircle.structured_data()
    assert structure['radius'] == 2
    assert structure['degrees']  == 180.0
    assert structure['center_cell']  == True

    edges = odd_semicircle.edges
    assert len(edges) == 1
    assert len(edges[0].inner) == 5
    assert edges[0].inner == (
        IntPos((2,6)), IntPos((1,3)), IntPos((0,0)), IntPos((1,0)), IntPos((2,0)),
    )
    assert edges[0].outer == (
        IntPos((2,7)), IntPos((1,4)), IntPos((-1,0)), IntPos((1,-1)), IntPos((2,-1)),
    )

    assert odd_semicircle.pos_adjacents(IntPos((0,0))) == [
        IntPos((1, 0)),
        IntPos((1, 1)),
        IntPos((1, 2)),
        IntPos((-1, 0)),
    ]
