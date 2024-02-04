#!/usr/bin/env python3

from maze.grid import BaseGrid, SingleSizeGrid
from maze.rectgrid import RectBaseGrid, RectGrid, ZetaGrid, UpsilonGrid
from maze.circlegrid import CircleGrid, PolygonGrid
from maze.hexgrid import HexGrid, TriGrid
from maze.complex_maze import complex_grid
import argparse
import random
import re
import os
from typing import Any

parser = argparse.ArgumentParser(
        prog="multimaze",
        description="Generate a maze with a variety of algorithms and a variety of outputs",
    )
parser.add_argument('size', help="either a string like '8x10', '10@', '7s', '7d', or the filename of a text or image mask")

parser.add_argument('-a', '--algorithm', default="backtrack", help="the maze algorithm to use")
parser.add_argument('-s', '--seed', help="if provided, the seed for the rng")
parser.add_argument('-f', '--field', action='store_true', help="whether to include a field of distances from the far point")
parser.add_argument('-p', '--path', action='store_true', help="whether to include the path from the far point to the other far point")
parser.add_argument('-w', '--weave', action='store_true', help="whether to weave links above and below other links")
parser.add_argument('-b', '--braid', type=float, help="the proportion of dead ends to braid")
parser.add_argument('--room_size', type=int, help="the size of rooms in fractal mazes")
parser.add_argument('--firstring', type=int, help="cells in the first non-trivial ring of a circular maze")
parser.add_argument('--slices', type=int, help="number of slices of a polygon maze to include")
parser.add_argument('--degrees', type=float, help="angles to include in a circle maze")
parser.add_argument('-y', '--hyper', type=int, action='append', help="number of planes in each hyper dimension, repeat for more dimensions")

parser.add_argument('-o', '--output', default="png", help="the output format", choices=RectGrid.outputs)
parser.add_argument('-n', '--name', help="the name to use for the output if generating a png")
parser.add_argument('--bg', action='store_true', help="whether to draw a black background")
parser.add_argument('--pathcolor', help="string of rgb float values for path, if no field")
parser.add_argument('--linewidth', type=float, help="thickness of line, where 1 is the cell width")
parser.add_argument('--inset', type=float, help="depth of inset when weave is true, where 1 is the cell width")
parser.add_argument('--pixels', type=float, help="how many pixels to map one maze height to, when printing to png")
parser.add_argument('--noflat', action='store_true', help="whether to call out to draw_maze rather than inlining it")

args = parser.parse_args()

if args.seed:
    if args.seed.isnumeric():
        seed = int(args.seed)
    else:
        seed = args.seed
    random.seed(seed)

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

option_kwargs: dict[str, Any] = {}
if args.weave:
    option_kwargs['weave'] = True
if args.bg:
    option_kwargs['bg'] = True
if args.noflat:
    option_kwargs['noflat'] = True
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

if m := re.match(r'(\d+)x(\d+)([guz]?)$', args.size):
    height, width = [int(x) for x in m.groups()[:2]]
    rect_grid_type = rg_for_char[m.group(3)]
    grid = rect_grid_type(height, width, **option_kwargs)
elif m := re.match(r'(\d+)([sd])$', args.size):
    size = int(m.group(1))
    single_size_grid_type = ssg_for_char[m.group(2)]
    grid = single_size_grid_type(size, **option_kwargs)
elif m := re.match(r'(\d+)([\@o])(\d*)$', args.size):
    size = int(m.group(1))
    center_cell = (m.group(2) == '@')
    if len(m.group(3)):
        sides = int(m.group(3))
        if args.slices:
            option_kwargs['slices'] = args.slices
        grid = PolygonGrid(size, sides, firstring=args.firstring, center_cell=center_cell, **option_kwargs)
    else:
        if args.degrees:
            option_kwargs['degrees'] = args.degrees
        grid = CircleGrid(size, firstring=args.firstring, center_cell=center_cell, **option_kwargs)
elif ':' in args.size:
    complex_type, size = args.size.split(':')
    grid = complex_grid(complex_type, int(size), **option_kwargs)
elif os.access(args.size, os.R_OK):
    mask_filename = args.size
    if mask_filename[-4:] == '.png':
        grid = RectGrid.from_mask_png(mask_filename, **option_kwargs)
    else:
        grid = RectGrid.from_mask_txt(mask_filename, **option_kwargs)
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
    if '.' in args.name:
        args.name = args.name[:args.name.index('.')]
    print_args['maze_name'] = args.name

grid.print(args.output, **print_args)
