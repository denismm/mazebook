#!/usr/bin/env python3

from grid.maze import BaseGrid, SingleSizeGrid
from grid.rectgrid import RectBaseGrid, RectGrid, ZetaGrid, UpsilonGrid
from grid.circlegrid import CircleGrid
from grid.hexgrid import HexGrid, TriGrid
import argparse
import random
import re
import os
from typing import Any

algorithms = list(BaseGrid.algorithms.keys())

parser = argparse.ArgumentParser(
        prog="multimaze",
        description="Generate a maze with a variety of algorithms and a variety of outputs",
    )
parser.add_argument('size', help="either a string like '8x10', '10@', '7s', '7d', or the filename of a text or image mask")

parser.add_argument('-a', '--algorithm', default="backtrack", help="the maze algorithm to use", choices=algorithms)
parser.add_argument('-o', '--output', default="ascii", help="the output format", choices=RectGrid.outputs)
parser.add_argument('-n', '--name', help="the name to use for the output if generating a png")
parser.add_argument('-f', '--field', action='store_true', help="whether to include a field of distances from the far point")
parser.add_argument('-p', '--path', action='store_true', help="whether to include the path from the far point to the other far point")
parser.add_argument('-s', '--seed', help="if provided, the seed for the rng")
parser.add_argument('-b', '--braid', type=float, help="the proportion of dead ends to braid")

args = parser.parse_args()

if args.seed:
    random.seed(args.seed)

grid: BaseGrid

ssg_for_char: dict[str, type[SingleSizeGrid]] = {
    's': HexGrid,
    '@': CircleGrid,
    'd': TriGrid,
}

rg_for_char: dict[str, type[RectBaseGrid]] = {
    '': RectGrid,
    'g': RectGrid,
    'z': ZetaGrid,
    'u': UpsilonGrid,
}

if m := re.match(r'(\d+)x(\d+)([guz]?)$', args.size):
    height, width = [int(x) for x in m.groups()[:2]]
    rect_grid_type = rg_for_char[m.group(3)]
    grid = rect_grid_type(height, width)
elif m := re.match(r'(\d+)([\@sd])$', args.size):
    size = int(m.group(1))
    single_size_grid_type = ssg_for_char[m.group(2)]
    grid = single_size_grid_type(size)
elif os.access(args.size, os.R_OK):
    mask_filename = args.size
    if mask_filename[-4:] == '.png':
        grid = RectGrid.from_mask_png(mask_filename)
    else:
        grid = RectGrid.from_mask_txt(mask_filename)
else:
    raise ValueError(f"invalid size {args.size}")

grid.generate_maze(args.algorithm)
if args.braid:
    grid.braid(args.braid)

print_args: dict[str, Any] = {}

if args.path or args.field:
    path = grid.longest_path()
    if args.path:
        print_args['path'] = path
    if args.field:
        print_args['field'] = grid.dijkstra(path[0])

if args.name:
    print_args['maze_name'] = args.name

grid.print(args.output, **print_args)
