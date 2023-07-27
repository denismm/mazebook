#!/usr/bin/env python3
import sys
import random
from positions import Position, Direction, cardinal_directions, add_direction
from maze import Grid

maze_width = int(sys.argv[1])
maze_height = int(sys.argv[2])

grid = Grid(maze_height, maze_width)
ne = cardinal_directions[:2]

for j in range(grid.height):
    run: list[Position] = []
    for i in range(grid.width):
        position = (i, j)
        run.append(position)
        options: list[Direction] = []
        for direction in ne:
            next_position = add_direction(position, direction)
            if next_position in grid:
                options.append(direction)
        if options:
            next_direction = random.choice(options)
            if next_direction == (0, 1):
                # close run and break north
                break_room = random.choice(run)
                next_position = add_direction(break_room, next_direction)
                grid.connect(break_room, next_position)
                run = []
            else:
                # add next room to run
                next_position = add_direction(position, next_direction)
                grid.connect(position, next_position)

grid.ascii_print()
