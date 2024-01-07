#!/usr/bin/env python3
import random
from grid.circlegrid import PolygonGrid
from grid.hexgrid import TriGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition
from math import cos, sin, tau

random.seed(97)
maze_size = 8
point_kwargs = {'slices': 1}
subgrids = {
    "C": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (
            EdgeSpec("0", 0, True),
            EdgeSpec("1", 0, True),
            EdgeSpec("2", 0, True),
            EdgeSpec("3", 0, True),
            EdgeSpec("4", 0, True),
        ),
        (0, 0),
        rotation=54,
    ),
    "0": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 0, True, align=True),),
        kwargs = point_kwargs,
    ),
    "1": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 1, True, align=True),),
        kwargs = point_kwargs,
    ),
    "2": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 2, True, align=True),),
        kwargs = point_kwargs,
    ),
    "3": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 3, True, align=True),),
        kwargs = point_kwargs,
    ),
    "4": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 4, True, align=True),),
        kwargs = point_kwargs,
    ),
}

star = MultiGrid(subgrids)

star.generate_maze("backtrack")

field = star.dijkstra(IntPosition((0, 0), "C"))

star.print("png", field=field, maze_name="fat_star")
