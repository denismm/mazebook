import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random
from maze.rectgrid import RectGrid
from maze.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

def test_two_square() -> None:
    random.seed(97)
    subgrids = {
        "A": GridSpec(
            RectGrid, (4, 4),
            (EdgeSpec('B', 2, True), None, None, None),
            (0, 0),
        ),
        "B": GridSpec(
            RectGrid, (4, 4),
            (None, None, EdgeSpec('A', 0, True), None),
            (4, 0),
        ),
    }

    multigrid = MultiGrid( subgrids )

    assert len(multigrid) == 32

    b_adjacents = multigrid.pos_adjacents(IntPosition((0, 0), 'B'))
    assert IntPosition((3, 0), 'A') in b_adjacents

    multigrid.generate_maze('backtrack')

    # maze should connect 32 points
    analysis = multigrid.node_analysis()
    assert analysis == {1: 5, 2: 24, 3: 3}

    ps_instructions = multigrid.ps_instructions()

    twobox_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'twobox.ps'))
    with open(twobox_path, 'r') as f:
        expected_instructions = f.read()
    assert ps_instructions == expected_instructions.rstrip()
