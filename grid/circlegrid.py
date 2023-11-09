# grids with or without a central node surrounded by rings of cells

from positions import Position, Direction, add_direction
from typing import Optional, Any
from math import pi
from functools import cache
from sys import stderr
import random

from .maze import Cell, SingleSizeGrid, BaseGrid, Division

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

    def find_link_pos(self, first: Position, second: Position) -> Position:
        # special case for center
        if first[0] == 1 and second[0] == 1 and self.center_cell:
            if self.widths[1] == 4:
                # we're probably going across the middle
                return (0, 0)
        return super().find_link_pos(first, second)

    def region_divisions(self, region: set[Position]) -> list[Division]:
        result: list[Division] = []
        # we assert that any region is sectional
        # in-out divisions
        rs = { p[0] for p in region }
        for r in range(min(rs), max(rs)):
            inner = { p for p in region if p[0] <= r }
            outer = region - inner
            border = tuple( (p, q) 
                for p in inner if p[0] == r
                for q in self.pos_neighbors(p) if q in outer
            )
            if not border:
                raise ValueError("empty border")
            result.append(Division(f"cut r on {r}", (inner, outer), border))
        inner_width = self.widths[min(rs)]
        def get_other_side(theta: int) -> dict[int, int]:
            return  {
                r: (theta + 1) * (self.widths[r] // inner_width) for r in rs
            }
        if inner_width > 1:
            inner_thetas = sorted([p[1] for p in region if p[0] == min(rs)])
            if len(inner_thetas) == inner_width:
                # for full circle, we need two borders
                random.shuffle(inner_thetas)
                for i in range(0, 2, inner_width):
                    thetas = sorted(inner_thetas[i:i+2])
                    other_sides_by_r = [get_other_side(theta) for theta in thetas]
                    first = { p for p in region
                        if (other_sides_by_r[0][p[0]] <= p[1] < other_sides_by_r[1][p[0]])}
                    second = region - first
                    border = tuple((p, q) 
                        for p in first
                        for q in self.pos_neighbors(p) if q in second)
                    if not border:
                        raise ValueError("empty border")
                    name = f"cut full circle on {thetas}"
                    result.append(Division(name, (first, second), border))

            # do we cross 0?
            elif (0 in inner_thetas) and (inner_width - 1 in inner_thetas):
                # get inner_thetas in order
                while inner_thetas[-1] - inner_thetas[0] != len(inner_thetas) - 1:
                    inner_thetas[-1] -= inner_width
                    inner_thetas.sort()
                    if inner_thetas[-1] < 0:
                        raise ValueError("problem canonicalizing inner_thetas")
                far_side_by_r = get_other_side(inner_thetas[-1])
                near_side_by_r = get_other_side(inner_thetas[0] % inner_width - 1)
                for theta in range(inner_thetas[0], inner_thetas[-1]):
                    if theta >= 0:
                        other_side_by_r = get_other_side(theta)
                        left = { p for p in region
                            if (other_side_by_r[p[0]] <= p[1] < far_side_by_r[p[0]])
                        }
                        right = region - left
                    else:
                        effective_theta = theta % inner_width
                        other_side_by_r = get_other_side(effective_theta)
                        right = { p for p in region
                            if (near_side_by_r[p[0]] <= p[1] < other_side_by_r[p[0]])
                        }
                        left = region - right
                    border = tuple( (p, q)
                        for p in left 
                        for q in self.pos_neighbors(p) if q in right
                    )
                    name = f"cutting broken theta on {theta}"
                    if not border:
                        raise ValueError("empty border")
                    result.append(Division(name, (left, right), border))
            else:
                for theta in range(inner_thetas[0], inner_thetas[-1]):
                    other_side_by_r = get_other_side(theta)
                    right = { p for p in region
                        if (p[1] < other_side_by_r[p[0]])}
                    left = region - right
                    border = tuple( (p, q)
                        for p in right if (p[1] + 1) == other_side_by_r[p[0]]
                        for q in self.pos_neighbors(p) if q in left
                    )
                    name = f"cutting simple theta on {theta}"
                    if not border:
                        raise ValueError("empty border")
                    result.append(Division(name, (left, right), border))
        return result


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

