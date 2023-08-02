#!/usr/bin/env python3
import sys
from maze import make_binary

maze_width = int(sys.argv[1])
maze_height = int(sys.argv[2])

grid = make_binary(maze_height, maze_width)

grid.ascii_print()
