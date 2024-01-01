#!/usr/bin/env python3
import random
from grid.circlegrid import PolygonGrid
from grid.hexgrid import TriGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition
from math import cos, sin, tau

random.seed(97)
maze_size = 8
drop_grid = PolygonGrid(maze_size, 5)
triangle_width = drop_grid.widths[-1] // 5
single_rotation = 72.0
pentagon_radius = maze_size + 0.5
triangle_position = (pentagon_radius * -sin(tau/10), pentagon_radius * cos(tau/10))
multiplier = 2 * cos(tau/10)
triangle_position = (pentagon_radius * -cos(tau/10) * multiplier, pentagon_radius * -sin(tau/10) * multiplier)
pullback = 144 - 18
triangle_scale = 1
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
        (EdgeSpec("C", 0, True),),
        triangle_position,
        0 * single_rotation - pullback,
        scale = triangle_scale,
        kwargs = point_kwargs,
    ),
    "1": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 1, True),),
        triangle_position,
        1 * single_rotation - pullback,
        scale = triangle_scale,
        kwargs = point_kwargs,
    ),
    "2": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 2, True),),
        triangle_position,
        2 * single_rotation - pullback,
        scale = triangle_scale,
        kwargs = point_kwargs,
    ),
    "3": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 3, True),),
        triangle_position,
        3 * single_rotation - pullback,
        scale = triangle_scale,
        kwargs = point_kwargs,
    ),
    "4": GridSpec(
        PolygonGrid,
        (maze_size, 5),
        (EdgeSpec("C", 4, True),),
        triangle_position,
        4 * single_rotation - pullback,
        scale = triangle_scale,
        kwargs = point_kwargs,
    ),
}

star = MultiGrid(subgrids)

star.generate_maze("backtrack")

field = star.dijkstra(IntPosition((0, 0), "C"))

star.print("png", field=field, maze_name="fat_star")
