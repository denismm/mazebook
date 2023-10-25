# grids with or without a central node surrounded by rings of cells

from positions import Position, Direction, add_direction
from typing import Optional, Any
from math import pi
from functools import cache
from sys import stderr

from .maze import Cell, SingleSizeGrid, BaseGrid, ps_list

def warn(*args: Any, **kwargs: Any) -> None:
    print(*args, file=stderr, **kwargs)

class CircleGrid(SingleSizeGrid):
    maze_type = "circlemaze"

    # key and value for size in draw_maze.ps
    @property
    def size_dict(self) -> dict[str, int | bool | list[int]]:
        return {'radius': self.radius, 'widths':  self.widths, 'center_cell': self.center_cell}

    # ps command to size and align ps output
    @property
    def ps_alignment(self) -> str:
        physical_radius: float = self.radius
        if self.center_cell:
            physical_radius += 0.5
        return f"72 softscale 4.25 5.5 translate 4 {physical_radius} div dup scale"

    # command subset for pstopng
    @property
    def png_alignment(self) -> list[str]:
        physical_radius: float = self.radius
        if self.center_cell:
            physical_radius += 0.5
        return [str(-1 * (physical_radius + 0.15)), 'd', 'd', 'd']

    def __init__(self, radius: int, firstring: Optional[int] = None, center_cell: bool = True, **kwargs: Any) -> None:
        super().__init__(radius, **kwargs)
        self.radius = radius
        # width of ring r
        self.widths: list[int] = []
        # for convenience: width of ring r / width of ring r-1
        self.ratios: list[int] = []
        # positions in CircleGrid are (r, theta)
        self.center_cell = center_cell
        if center_cell:
            physical_radius_offset = 0.0
            self._grid[(0,0)] = Cell((0,0))
            starting_r = 1
            self.widths.append(1)
            self.ratios.append(0)
        else:
            physical_radius_offset = 0.5
            starting_r = 0
        for r in range(starting_r, starting_r + radius):
            if r == starting_r and firstring is not None:
                width = firstring
                ratio = width
            else:
                # for now, use algorithm from book
                circumference = (r + physical_radius_offset) * pi * 2
                last_width = 1 if r == 0 else self.widths[r - 1]
                estimated_cell_width = circumference / last_width
                ratio = round(estimated_cell_width)
                width = last_width * ratio
            self.widths.append(width)
            self.ratios.append(ratio)
            for theta in range(width):
                position = (r, theta)
                self._grid[position] = Cell(position)

    @cache
    def pos_adjacents(self, start: Position) -> list[Position]:
        # cw and ccw around ring
        r, theta = start[:2]
        neighbors: list[Position] = []
        # right, down, left
        if self.widths[r] > 1:
            neighbors.append((r, (theta + 1) % self.widths[r]))
        if r > 0:
            neighbors.append((r - 1, theta // self.ratios[r]))
        if self.widths[r] > 1:
            neighbors.append((r, (theta - 1) % self.widths[r]))
        if r + 1 < len(self.widths):
            next_ratio = self.ratios[r + 1]
        else:
            next_ratio = 1
        neighbors += [
            (r + 1, theta * next_ratio + x) for x in range(next_ratio)]
        return neighbors

class PolygonGrid(CircleGrid):
    maze_type = "polygonmaze"

    def __init__(self, radius: int, sides: int, firstring: Optional[int] = None, center_cell: bool = True, **kwargs: Any) -> None:
        if firstring is None:
            firstring = sides
        super().__init__(radius, firstring=firstring, center_cell=center_cell, **kwargs)
        self.sides = sides

    # key and value for size in draw_maze.ps
    @property
    def size_dict(self) -> dict[str, int | bool | list[int]]:
        return {'radius': self.radius, 'sides': self.sides, 'widths':  self.widths, 'center_cell': self.center_cell}

