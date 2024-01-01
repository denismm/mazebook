#!/usr/bin/env python3
import random
from grid.rectgrid import RectGrid
from grid.hexgrid import TriGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

random.seed(97)
maze_size = 4
outer_width = maze_size * 2
single_rotation = 90
triangle_position = (-maze_size, maze_size)
pullback = 90
triangle_scale = 1
subgrids = {
    "C": GridSpec(
        RectGrid,
        (maze_size * 2, maze_size * 2),
        (
            EdgeSpec("0", 2, True),
            EdgeSpec("1", 2, True),
            EdgeSpec("2", 2, True),
            EdgeSpec("3", 2, True),
        ),
        (-maze_size, -maze_size),
    ),
    "0": GridSpec(
        TriGrid,
        (outer_width,),
        (None, None, EdgeSpec("C", 0, True),),
        triangle_position,
        0 * single_rotation - pullback,
        scale = triangle_scale,
    ),
    "1": GridSpec(
        TriGrid,
        (outer_width,),
        (None, None, EdgeSpec("C", 1, True),),
        triangle_position,
        1 * single_rotation - pullback,
        scale = triangle_scale,
    ),
    "2": GridSpec(
        TriGrid,
        (outer_width,),
        (None, None, EdgeSpec("C", 2, True),),
        triangle_position,
        2 * single_rotation - pullback,
        scale = triangle_scale,
    ),
    "3": GridSpec(
        TriGrid,
        (outer_width,),
        (None, None, EdgeSpec("C", 3, True),),
        triangle_position,
        3 * single_rotation - pullback,
        scale = triangle_scale,
    ),
}

star = MultiGrid(subgrids, weave=True, linewidth=0.01)

star.generate_maze("backtrack")

field = star.dijkstra(IntPosition((0, 0), "C"))

star.print("ps", field=field, maze_name="star")
