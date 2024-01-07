#!/usr/bin/env python3
import random
from grid.rectgrid import RectGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

random.seed(97)
maze_size = 8
subgrids = {
    "F": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("R", 2, True),
            EdgeSpec("U", 3, True),
            EdgeSpec("L", 0, True),
            EdgeSpec("D", 1, True),
        ),
    ),
    "B": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("R", 0, True),
            EdgeSpec("D", 3, True, align=True),
            EdgeSpec("L", 2, True),
            EdgeSpec("U", 1, True),
        ),
    ),
    "L": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("F", 2, True, align=True),
            EdgeSpec("U", 2, True),
            EdgeSpec("B", 2, True),
            EdgeSpec("D", 2, True),
        ),
    ),
    "R": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("B", 0, True),
            EdgeSpec("U", 0, True),
            EdgeSpec("F", 0, True, align=True),
            EdgeSpec("D", 0, True),
        ),
    ),
    "U": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("R", 1, True),
            EdgeSpec("B", 3, True),
            EdgeSpec("L", 1, True),
            EdgeSpec("F", 1, True, align=True),
        ),
    ),
    "D": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("R", 3, True),
            EdgeSpec("F", 3, True, align=True),
            EdgeSpec("L", 3, True),
            EdgeSpec("B", 1, True),
        ),
    ),
}

multigrid = MultiGrid(subgrids, weave=True)

multigrid.generate_maze("backtrack")

field = multigrid.dijkstra(IntPosition((0, 0), "F"))

# multigrid.print("ps", field=field)
multigrid.print("png", field=field, maze_name="cube")
