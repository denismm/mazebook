#!/usr/bin/env python3
import random
from grid.rectgrid import RectGrid
from grid.hexgrid import TriGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

random.seed(97)
maze_size = 8
subgrids = {
    "C": GridSpec(
        RectGrid,
        (maze_size, maze_size),
        (
            EdgeSpec("0", 2, True),
            EdgeSpec("1", 2, True),
            EdgeSpec("2", 2, True),
            EdgeSpec("3", 2, True),
        ),
    ),
    "0": GridSpec(
        TriGrid,
        (maze_size,),
        (None, None, EdgeSpec("C", 0, True, align=True),),
    ),
    "1": GridSpec(
        TriGrid,
        (maze_size,),
        (None, None, EdgeSpec("C", 1, True, align=True),),
    ),
    "2": GridSpec(
        TriGrid,
        (maze_size,),
        (None, None, EdgeSpec("C", 2, True, align=True),),
    ),
    "3": GridSpec(
        TriGrid,
        (maze_size,),
        (None, None, EdgeSpec("C", 3, True, align=True),),
    ),
}

star = MultiGrid(subgrids, weave=True, linewidth=0.01)

star.generate_maze("backtrack")

field = star.dijkstra(IntPosition((0, 0), "C"))

star.print("png", field=field, maze_name="fourstar")
