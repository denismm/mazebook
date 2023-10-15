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

    def __init__(self, radius: int, firstring: Optional[int] = None, center_cell: bool = True) -> None:
        super().__init__(radius)
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
    def pos_neighbors_with_dirs(self, start: Position) -> list[tuple[Position, Direction]]:
        # cw and ccw around ring
        r, theta = start[:2]
        neighbors_and_dirs: list[tuple[Position, Direction]] = []
        # right, down, left
        if self.widths[r] > 1:
            neighbors_and_dirs.append(((r, (theta + 1) % self.widths[r]), (0, 1)))
        if r > 0:
            neighbors_and_dirs.append(((r - 1, theta // self.ratios[r]), (-1, 0)))
        if self.widths[r] > 1:
            neighbors_and_dirs.append(((r, (theta - 1) % self.widths[r]), (0, -1)))
        if r + 1 < len(self.widths):
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
            # not tunnelable if not square
            if target_r + 1 >= len(self.ratios) or self.ratios[target_r + 1] != 1:
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
            # different rings but this is one in from whichever is higher
            higher = max([first, second])
            link_pos = (higher[0] - 1, higher[1], 1)

        link_cell = Cell(link_pos)
        self._grid[link_pos] = link_cell
        super().connect(first, link_pos)
        super().connect(second, link_pos)


    def walls_for_cell(self, cell: Cell) -> list[bool]:
        walls: list[bool] = []
        position = cell.position
        for npos in self.pos_neighbors_for_walls(position):
            walls.append(npos not in cell.flat_links)
        if position[0] == len(self.widths) - 1:
            walls.append(True)
        return walls

class PolygonGrid(CircleGrid):
    maze_type = "polygonmaze"

    def __init__(self, radius: int, sides: int, firstring: Optional[int] = None, center_cell: bool = True, ) -> None:
        if firstring is None:
            firstring = sides
        super().__init__(radius, firstring=firstring, center_cell=center_cell)
        self.sides = sides

    # key and value for size in draw_maze.ps
    @property
    def size_dict(self) -> dict[str, int | bool | list[int]]:
        return {'radius': self.radius, 'sides': self.sides, 'widths':  self.widths, 'center_cell': self.center_cell}

