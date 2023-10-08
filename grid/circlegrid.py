# grids with a central node surrounded by rings of cells

from positions import Position, Direction, add_direction
from typing import Optional
from math import pi
from functools import cache
from sys import stderr

from .maze import Cell, SingleSizeGrid, BaseGrid, ps_list

def warn(*args, **kwargs) -> None:
    print(*args, file=stderr, **kwargs)

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
    def pos_neighbors_with_dirs(self, start: Position) -> list[tuple[Position, Direction]]:
        # cw and ccw around ring
        r, theta = start[:2]
        neighbors_and_dirs: list[tuple[Position, Direction]] = []
        if r > 0:
            # right, down, left
            neighbors_and_dirs.append(((r, (theta + 1) % self.widths[r]), (0, 1)))
            neighbors_and_dirs.append(((r - 1, theta // self.ratios[r]), (-1, 0)))
            neighbors_and_dirs.append(((r, (theta - 1) % self.widths[r]), (0, -1)))
        if r < self.radius:
            next_ratio = self.ratios[r + 1]
            neighbors_and_dirs += [
                ((r + 1, theta * next_ratio + x), (1, 0)) for x in range(next_ratio)]

        return neighbors_and_dirs

    @cache
    def pos_neighbors_for_walls(self, start: Position) -> list[Position]:
        return [neighbor for neighbor, _ in self.pos_neighbors_with_dirs(start) if neighbor in self]

    def pos_neighbors(self, start: Position) -> list[Position]:
        if not self.weave:
            return self.pos_neighbors_for_walls(start)
        # for each direction, check for weave-ability
        neighbors_and_dirs = self.pos_neighbors_with_dirs(start)
        neighbors: list[Position] = []
        for target_pos, dir in neighbors_and_dirs:
            if target_pos not in self:
                continue
            target_r, target_theta = target_pos
            if target_r + 1 >= len(self.ratios) or self.ratios[target_r + 1] != 1:
                # not tunnelable if not square
                neighbors.append(target_pos)
                continue
            target_cell = self[target_pos]
            # is this already connected?
            link_count = len(target_cell.links)
            # only tunnelable if straight across
            if link_count != 2:
                neighbors.append(target_pos)
                continue
            if dir == (-1, 0) and self.ratios[target_r] != 1:
                other_side = (target_r - 1, target_theta // self.ratios[target_r])
            else:
                other_side = add_direction(target_pos, dir) # type: ignore [assignment]
            other_side = (other_side[0], other_side[1] % self.widths[other_side[0]])
            if other_side in self:
                if not ({start, other_side} & target_cell.flat_links):
                    # tunnel ok!
                    neighbors.append(other_side)
        return neighbors

    def connect(self, first: Position, second: Position) -> None:
        # what if there's a distance between the two cells?
        if second in self.pos_neighbors_for_walls(first):
            return super().connect(first, second)
        # link square is between both, add third dimension
        # do this the hard way for now
        # same ring?
        link_pos: Position
        if first[0] == second[0]:
            ring = first[0]
            # not across origin?
            if abs(first[1] - second[1]) == 2:
                link_pos = (ring, (first[1] + second[1]) // 2, 1)
            else:
                # we need to add N to one coord and it doesn't matter which
                link_pos = (
                    ring,
                    ((first[1] + second[1] + self.widths[ring]) // 2) % self.widths[ring],
                    1
                )
        else:
            # different rings but this is one below whichever is higher
            link_pos = (max([first[0], second[0]]) - 1, first[1], 1)

        link_cell = Cell(link_pos)
        self._grid[link_pos] = link_cell
        super().connect(first, link_pos)
        super().connect(second, link_pos)


    def walls_for_cell(self, cell: Cell) -> list[bool]:
        walls: list[bool] = []
        position = cell.position
        for npos in self.pos_neighbors_for_walls(position):
            walls.append(npos not in cell.flat_links)
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
