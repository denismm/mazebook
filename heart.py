#!/usr/bin/env python3
import random
from grid.rectgrid import RectGrid
from grid.circlegrid import SemiCircleGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

random.seed(97)
maze_size = 9
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
        rotation=45,
    ),
    "L": GridSpec(
        SemiCircleGrid,
        (maze_size,),
        (
            EdgeSpec("C", 0, True, align=True),
        ),
    ),
    "R": GridSpec(
        SemiCircleGrid,
        (maze_size,),
        (
            EdgeSpec("C", 1, True, align=True),
        ),
    ),
}

heart = MultiGrid(subgrids, weave=True, linewidth=0.01, pixels=30)

heart.generate_maze("backtrack")

field = heart.dijkstra(IntPosition((0, 0), "C"))

heart.print("png", field=field, maze_name="heart")
