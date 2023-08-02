#!/usr/bin/env python3
import sys
from maze import make_sidewinder

maze_width = int(sys.argv[1])
maze_height = int(sys.argv[2])

grid = make_sidewinder(maze_height, maze_width)

long_path = grid.longest_path()
field = grid.dijkstra(long_path[0])
grid.ascii_print(field=field, path=long_path)
