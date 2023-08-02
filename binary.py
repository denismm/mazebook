#!/usr/bin/env python3
import random
import sys
from positions import Position, cardinal_directions, add_direction
from maze import Grid

maze_width = int(sys.argv[1])
maze_height = int(sys.argv[2])

grid = Grid(maze_height, maze_width)

ne = cardinal_directions[:2]
nw = cardinal_directions[1:3]

for j in range(grid.height):
    for i in range(grid.width):
        position = (i, j)
        possible_next: list[Position] = []
        # possible_dirs = ne if j % 2 == 0 else nw
        possible_dirs = ne
        for direction in possible_dirs:
            next_position = add_direction(position, direction)
            if next_position in grid:
                possible_next.append(next_position)
        if possible_next:
            next_position = random.choice(possible_next)
            grid.connect(position, next_position)
grid.ascii_print()
