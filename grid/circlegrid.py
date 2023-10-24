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
            target_neighbors = self.pos_neighbors_for_walls(target_pos)
            # not tunnelable if not square
            if len(target_neighbors) != 4:
                neighbors.append(target_pos)
                continue
            target_cell = self[target_pos]
            # is this already connected?
            link_count = len(target_cell.links)
            # only tunnelable if straight across
            if link_count != 2:
                neighbors.append(target_pos)
                continue
            back_index = target_neighbors.index(start)
            other_side = target_neighbors[(back_index + 2) % 4]
            if other_side in self:
                if not ({start, other_side} & target_cell.flat_links):
                    # tunnel ok!
                    neighbors.append(other_side)
        return neighbors

    def connect(self, first: Position, second: Position) -> None:
        # what if there's a distance between the two cells?
        if second[:2] in self.pos_neighbors_for_walls(first):
            return super().connect(first, second)
        # link square is between both, add third dimension
        # general solution
        first_neighbors = self.pos_neighbors_for_walls(first)
        second_neighbors = self.pos_neighbors_for_walls(second)
        intersection_positions = set(first_neighbors) & set(second_neighbors)
        if len(intersection_positions) == 0:
            raise ValueError(f"no common cell between {first} and {second}")
        if len(intersection_positions) > 1:
            raise ValueError(f"too many common cells between {first} and {second}")
        link_pos = intersection_positions.pop() + (1,)

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

