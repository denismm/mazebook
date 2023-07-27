#!/usr/bin/env python3
import random
from positions import Position, cardinal_directions, add_direction
from maze import Grid

maze_width = 5
maze_height = 5

grid = Grid(maze_height, maze_width)

ne = cardinal_directions[:2]

for j in range(grid.height):
    for i in range(grid.width):
        position = (i, j)
        possible_next: list[Position] = []
        for direction in ne:
            next_position = add_direction(position, direction)
            if next_position in grid:
                possible_next.append(next_position)
        if possible_next:
            next_position = random.choice(possible_next)
            grid.connect(position, next_position)
grid.ascii_print()
