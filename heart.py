#!/usr/bin/env python3
import random
from grid.rectgrid import RectGrid
from grid.circlegrid import SemiCircleGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

random.seed(97)
maze_size = 8
subgrids = {
    "C": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("L", 0, True),
            EdgeSpec("R", 0, True),
            None,
            None,
        ),
        (-maze_size / 2, -maze_size/2),
    ),
    "L": GridSpec(
        SemiCircleGrid,
        (maze_size,),
        (
            EdgeSpec("C", 0, True),
        ),
        ( 0, maze_size / 2),
        rotation=270,

    ),
    "R": GridSpec(
        SemiCircleGrid,
        (maze_size,),
        (
            EdgeSpec("C", 1, True),
        ),
        ( 0, maze_size / 2),
        rotation=0,
    ),
}

heart = MultiGrid(subgrids, weave=False, linewidth=0.01)

heart.generate_maze("backtrack")

field = heart.dijkstra(IntPosition((0, 0), "C"))

heart.print("ps", field=field, maze_name="heart")
