#!/usr/bin/env python3

import maze
import argparse
import random
import re
import os
from typing import Any

algorithms = list(maze.Grid.algorithms.keys())

parser = argparse.ArgumentParser(
        prog="multimaze",
        description="Generate a maze with a variety of algorithms and a variety of outputs",
    )
parser.add_argument('size', help="either a string like '8x10' or the filename of a text or image mask")

parser.add_argument('-a', '--algorithm', default="wilson", help="the maze algorithm to use", choices=algorithms)
parser.add_argument('-o', '--output', default="ascii", help="the output format", choices=maze.Grid.outputs)
parser.add_argument('-n', '--name', help="the name to use for the output if generating a png")
parser.add_argument('--field', action='store_true', help="whether to include a field of distances from the far point")
parser.add_argument('--path', action='store_true', help="whether to include the path from the far point to the other far point")
parser.add_argument('--seed', help="if provided, the seed for the rng")

args = parser.parse_args()

if args.seed:
    random.seed(args.seed)

if m := re.match(r'(\d+)x(\d+)$', args.size):
    height, width = [int(x) for x in m.groups()]
    grid = maze.Grid(height, width)
elif os.access(args.size, os.R_OK):
    mask_filename = args.size
    if mask_filename[-4:] == '.png':
        grid = maze.Grid.from_mask_png(mask_filename)
    else:
        grid = maze.Grid.from_mask_txt(mask_filename)
else:
    raise ValueError(f"invalid size {args.size}")

grid.generate_maze(args.algorithm)
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
