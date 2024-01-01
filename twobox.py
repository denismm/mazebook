#!/usr/bin/env python3
import random
from grid.rectgrid import RectGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

random.seed(97)
maze_size = 8
subgrids = {
    "A": GridSpec(RectGrid, (maze_size, maze_size), (EdgeSpec('B', 2, True), None, None, None), (0, 0)),
    "B": GridSpec(RectGrid, (maze_size, maze_size), (None, None, EdgeSpec('A', 0, True), None), (maze_size, 0)),
}

multigrid = MultiGrid( subgrids, weave=True )

multigrid.generate_maze('kruskal')

field = multigrid.dijkstra(IntPosition((0, 0), 'A'))

# multigrid.print("ps", field=field)
multigrid.print("png", field=field, maze_name="twobox")
