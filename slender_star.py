#!/usr/bin/env python3
import random
from grid.circlegrid import PolygonGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition
from math import cos, sin, tau

center_cell = False

random.seed(97)
maze_size = 10
polygon_args = (maze_size, 5)
polygon_kwargs = {"firstring": 10, "center_cell": center_cell}
point_kwargs = {'slices': 1, "center_cell": center_cell}
point_size = None

drop_grid = PolygonGrid(*polygon_args, **polygon_kwargs)
triangle_width = drop_grid.widths[-1] // 5
for i in range(maze_size, maze_size * 3):
    drop_grid = PolygonGrid(i, 10, **point_kwargs)
    outer_width = drop_grid.widths[-1] // 10
    if outer_width == triangle_width:
        point_size = i
    if outer_width > triangle_width:
        if point_size is None:
            raise ValueError("no matching size")
        break
assert point_size is not None
point_args = (point_size, 10)

single_rotation = 72.0
pentagon_radius = maze_size + 0.5 * center_cell
point_radius = point_size + 0.5 * center_cell
point_scale = pentagon_radius * sin(tau/10) / (point_radius * sin(tau/20))
multiplier = pentagon_radius * cos(tau/10) + point_scale * point_radius * cos(tau/20)
triangle_position = (
    -cos(tau/20) * multiplier,
    -sin(tau/20) * multiplier
)
pullback = 144 - 36
subgrids = {
    "C": GridSpec( PolygonGrid, polygon_args,
        (
            EdgeSpec("0", 0, True),
            EdgeSpec("1", 0, True),
            EdgeSpec("2", 0, True),
            EdgeSpec("3", 0, True),
            EdgeSpec("4", 0, True),
        ),
        (0, 0),
        rotation=54,
        kwargs=polygon_kwargs
    ),
    "0": GridSpec( PolygonGrid, point_args,
        (EdgeSpec("C", 0, True, align=True),),
        kwargs=point_kwargs,
    ),
    "1": GridSpec( PolygonGrid, point_args,
        (EdgeSpec("C", 1, True, align=True),),
        kwargs=point_kwargs,
    ),
    "2": GridSpec( PolygonGrid, point_args,
        (EdgeSpec("C", 2, True, align=True),),
        kwargs=point_kwargs,
    ),
    "3": GridSpec( PolygonGrid, point_args,
        (EdgeSpec("C", 3, True, align=True),),
        kwargs=point_kwargs,
    ),
    "4": GridSpec( PolygonGrid, point_args,
        (EdgeSpec("C", 4, True, align=True),),
        kwargs=point_kwargs,
    ),
}

star = MultiGrid(subgrids, weave=True)

star.generate_maze("backtrack")

field = star.dijkstra(IntPosition((0, 0), "C"))

star.print("png", field=field, maze_name="slender_star")
