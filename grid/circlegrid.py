# grids with a central node surrounded by rings of cells

from positions import Position, cardinal_directions, add_direction
from typing import Optional
from math import pi
from functools import cache

from .maze import Cell, SingleSizeGrid, BaseGrid, ps_list

class CircleGrid(SingleSizeGrid):
    outputs = {}

    ps_function = "drawcirclemaze"

    # key and value for size in draw_maze.ps
    @property
    def ps_size(self) -> str:
        return f"/radius {self.radius} /widths {ps_list(self.widths)}"

    # ps command to size and align ps output
    @property
    def ps_alignment(self) -> str:
        return f"72 softscale 4.25 5.5 translate 4 {self.radius + 0.5} div dup scale"

    # command subset for pstopng
    @property
    def png_alignment(self) -> list[str]:
        return [str(-1 * (self.radius + 0.65)), 'd', 'd', 'd']

    def __init__(self, radius: int) -> None:
        super().__init__(radius)
        self.radius = radius
        self.widths: list[int] = [1]
        self.ratios: list[int] = [0]
        # positions in CircleGrid are (r, theta)
        self._grid[(0,0)] = Cell((0,0))
        for r in range(1,radius + 1):
            # for now, use algorithm from book
            circumference = r * pi * 2
            last_width = self.widths[r - 1]
            estimated_cell_width = circumference / last_width
            ratio = round(estimated_cell_width)
            width = last_width * ratio
            self.widths.append(width)
            self.ratios.append(ratio)
            for theta in range(width):
                position = (r, theta)
                self._grid[position] = Cell(position)

    @cache
    def pos_neighbors(self, start: Position) -> list[Position]:
        # cw and ccw around ring
        r, theta = start
        neighbors: list[Position] = []
        if r > 0:
            # left, down, right
            neighbors.append((r, (theta - 1) % self.widths[r]))
            neighbors.append((r - 1, theta // self.ratios[r]))
            neighbors.append((r, (theta + 1) % self.widths[r]))
        if r < self.radius:
            next_ratio = self.ratios[r + 1]
            neighbors += [(r + 1, theta * next_ratio + x) for x in range(next_ratio)]

        neighbors = [neighbor for neighbor in neighbors if neighbor in self]
        return neighbors

    def walls_for_cell(self, cell: Cell) -> list[bool]:
        walls: list[bool] = []
        position = cell.position
        for npos in self.pos_neighbors_for_walls(position):
            walls.append(npos not in cell.links)
        if position[0] == self.radius:
            walls.append(True)
        return walls

    outputs['ps'] = BaseGrid.ps_print
    outputs['png'] = BaseGrid.png_print

    def print(self,
            print_method: str,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        self.outputs[print_method](self, path, field, **kwargs)
