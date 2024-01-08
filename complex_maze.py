#!/usr/bin/env python3

from grid.maze import BaseGrid, SingleSizeGrid
from grid.multigrid import MultiGrid, GridSpec, EdgeSpec
from grid.rectgrid import RectBaseGrid, RectGrid, ZetaGrid, UpsilonGrid
from grid.circlegrid import CircleGrid, PolygonGrid
from grid.hexgrid import HexGrid, TriGrid
import argparse
import random
import re
import os
from typing import Any
from typing_extensions import Protocol

class ComplexMaze(Protocol):
    def __call__(self,
        size: int,
        **kwargs: str) -> MultiGrid: ...

complex_mazes: dict[str, ComplexMaze] = {}

def complex_maze(cmf: ComplexMaze) -> ComplexMaze:
    complex_mazes[cmf.__name__] = cmf
    return cmf

@complex_maze
def slender_star(size: int, **kwargs: str) -> MultiGrid:
    center_cell: bool = kwargs.pop('center_cell', False)
    polygon_args = (size, 5)
    polygon_kwargs = {"firstring": 10, "center_cell": center_cell}
    point_kwargs = {'slices': 1, "center_cell": center_cell}
    point_size = None

    drop_grid = PolygonGrid(*polygon_args, **polygon_kwargs)
    triangle_width = drop_grid.widths[-1] // 5
    for i in range(size, size * 3):
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
    return MultiGrid(subgrids, **kwargs)


parser = argparse.ArgumentParser(
        prog="multimaze",
        description="Generate a maze with a variety of algorithms and a variety of outputs",
    )
parser.add_argument('mazetype', help="the name of the shape to use")
parser.add_argument('size', type=int, help="size of the relevant dimension")

parser.add_argument('-a', '--algorithm', default="backtrack", help="the maze algorithm to use")
parser.add_argument('-o', '--output', default="ps", help="the output format", choices=RectGrid.outputs)
parser.add_argument('-n', '--name', help="the name to use for the output if generating a png")
parser.add_argument('-f', '--field', action='store_true', help="whether to include a field of distances from the far point")
parser.add_argument('-w', '--weave', action='store_true', help="whether to weave links above and below other links")
parser.add_argument('-s', '--seed', help="if provided, the seed for the rng")
parser.add_argument('-b', '--braid', type=float, help="the proportion of dead ends to braid")
parser.add_argument('--room_size', type=int, help="the size of rooms in fractal mazes")
parser.add_argument('--bg', action='store_true', help="whether to draw a black background")
parser.add_argument('--pathcolor', help="string of rgb float values for path, if no field")
parser.add_argument('--linewidth', type=float, help="thickness of line, where 1 is the cell width")
parser.add_argument('--inset', type=float, help="depth of inset when weave is true, where 1 is the cell width")
parser.add_argument('-y', '--hyper', type=int, action='append', help="number of planes in each hyper dimension, repeat for more dimensions")
parser.add_argument('--pixels', type=float, help="how many pixels to map one maze height to, when printing to png")

args = parser.parse_args()

if args.seed:
    if args.seed.isnumeric():
        seed = int(args.seed)
    else:
        seed = args.seed
    random.seed(seed)

grid: BaseGrid

option_kwargs: dict[str, Any] = {}
if args.weave:
    option_kwargs['weave'] = True
if args.bg:
    option_kwargs['bg'] = True
if args.pathcolor:
    option_kwargs['pathcolor'] = [float(c) for c in args.pathcolor.split()]
if args.inset:
    option_kwargs['inset'] = args.inset
if args.linewidth:
    option_kwargs['linewidth'] = args.linewidth
if args.pixels:
    option_kwargs['pixels'] = args.pixels
if args.room_size:
    option_kwargs['room_size'] = args.room_size
if args.hyper:
    option_kwargs['hyper'] = args.hyper

grid = complex_mazes[args.mazetype](args.size, **option_kwargs)

grid.generate_maze(args.algorithm)
if args.braid:
    grid.braid(args.braid)

print_args: dict[str, Any] = {}

if args.field:
    path = grid.longest_path()
    if args.field:
        print_args['field'] = grid.dijkstra(path[0])

if args.name:
    if '.' in args.name:
        args.name = args.name[:args.name.index('.')]
    print_args['maze_name'] = args.name

grid.print(args.output, **print_args)
