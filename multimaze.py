#!/usr/bin/env python3

import maze
import sys
import argparse

algorithms = maze.algorithms

parser = argparse.ArgumentParser(
        prog="multimaze",
        description="Generate a maze with a variety of algorithms and a variety of outputs",
    )
parser.add_argument('width', type=int)
parser.add_argument('height', type=int)

parser.add_argument('--algorithm', default="wilson", help="the maze algorithm to use", choices=algorithms)
parser.add_argument('--output', default="ascii", help="the output format", choices=maze.outputs)
parser.add_argument('--output_name', help="the name to use for the output if generating a png")
parser.add_argument('--field', type=bool, help="whether to include a field of distances from the far point")
parser.add_argument('--path', type=bool, help="whether to include the path from the far point to the other far point")
parser.add_argument('--seed', help="if provided, the seed for the rng")

args = parser.parse_args()
