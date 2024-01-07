#!/usr/bin/env python3
import random
from grid.circlegrid import PolygonGrid
from grid.hexgrid import TriGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

random.seed(97)
maze_size = 8
drop_grid = PolygonGrid(maze_size, 5)
triangle_width = drop_grid.widths[-1] // 5
subgrids = {
    "C": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (
            EdgeSpec("0", 2, True),
            EdgeSpec("1", 2, True),
            EdgeSpec("2", 2, True),
            EdgeSpec("3", 2, True),
            EdgeSpec("4", 2, True),
        ),
        (0, 0), rotation=54
    ),
    "0": GridSpec(
        TriGrid,
        (triangle_width,),
        (None, None, EdgeSpec("C", 0, True, align=True),),
    ),
    "1": GridSpec(
        TriGrid,
        (triangle_width,),
        (None, None, EdgeSpec("C", 1, True, align=True),),
    ),
    "2": GridSpec(
        TriGrid,
        (triangle_width,),
        (None, None, EdgeSpec("C", 2, True, align=True),),
    ),
    "3": GridSpec(
        TriGrid,
        (triangle_width,),
        (None, None, EdgeSpec("C", 3, True, align=True),),
    ),
    "4": GridSpec(
        TriGrid,
        (triangle_width,),
        (None, None, EdgeSpec("C", 4, True, align=True),),
    ),
}

star = MultiGrid(subgrids, weave=True, linewidth=0.1)

star.generate_maze("backtrack")

field = star.dijkstra(IntPosition((0, 0), "C"))

star.print("png", field=field, maze_name="star")
