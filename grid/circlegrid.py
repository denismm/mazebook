# grids with or without a central node surrounded by rings of cells

from positions import Position, IntPosition, Direction, add_direction
from typing import Optional, Any, Sequence
from math import pi
from functools import cache
from sys import stderr
import random

from .maze import SingleSizeGrid, BaseGrid, Division, Edge

def warn(*args: Any, **kwargs: Any) -> None:
    print(*args, file=stderr, **kwargs)

class CircleGrid(SingleSizeGrid):
    maze_type = "circlemaze"

    def __init__(self, radius: int, firstring: Optional[int] = None, center_cell: bool = True, degrees: float = 360.0, **kwargs: Any) -> None:
        super().__init__(radius, **kwargs)
        self.radius = radius
        self.center_cell = center_cell
        self.degrees = degrees

        # width of ring r
        self.widths: list[int] = []
        # for convenience: width of ring r / width of ring r-1
        self.ratios: list[int] = []
        # positions in CircleGrid are (r, theta)
        if center_cell:
            physical_radius_offset = 0.0
            self._add_column((0, 0))
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
                if (theta + 0.5) * 360 / width >= degrees:
                    break
                self._add_column((r, theta))

    @property
    def external_points(self) -> Sequence[tuple[float, ...]]:
        # fake it as a box
        # "physical" radius
        p_radius: float = self.radius
        if self.center_cell:
            p_radius += 0.5
        return [(-p_radius, -p_radius), (p_radius, p_radius)]

    # key and value for size in draw_maze.ps
    @property
    def size_dict(self) -> dict[str, int | float | bool | list[int]]:
        return {'radius': self.radius, 'widths':  self.widths, 'center_cell': self.center_cell, 'degrees': self.degrees}

    @property
    def edges(self) -> tuple[Edge, ...]:
        return ()

    @cache
    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        # cw and ccw around ring
        r, theta, *remainder = start.coordinates
        neighbors: list[Position] = []
        gridname = self._gridname
        # right, down, left
        if self.widths[r] > 1:
            neighbors.append(IntPosition((r, (theta + 1) % self.widths[r], *remainder), gridname))
        if r > 0:
            neighbors.append(IntPosition((r - 1, theta // self.ratios[r], *remainder), gridname))
        if self.widths[r] > 1:
            neighbors.append(IntPosition((r, (theta - 1) % self.widths[r], *remainder), gridname))
        if r + 1 < len(self.widths):
            next_ratio = self.ratios[r + 1]
        else:
            next_ratio = 1
        neighbors += [
            IntPosition((r + 1, theta * next_ratio + x, *remainder), gridname) for x in range(next_ratio)]
        return self.adjust_adjacents(start, neighbors)

    def find_link_pos(self, first: Position, second: Position) -> Position:
        # special case for center
        if first.coordinates[0] == 1 and second.coordinates[0] == 1 and self.center_cell:
            if self.widths[1] == 4:
                # we're probably going across the middle
                return IntPosition((0, 0))
        return super().find_link_pos(first, second)

    def region_divisions(self, region: set[Position]) -> list[Division]:
        result: list[Division] = []
        # we assert that any region is sectional
        # in-out divisions
        rs = { p.coordinates[0] for p in region }
        for r in range(min(rs), max(rs)):
            inner = { p for p in region if p.coordinates[0] <= r }
            outer = region - inner
            result.append(Division(f"cut r on {r}", (inner, outer)))
        inner_width = self.widths[min(rs)]
        def get_other_side(theta: int) -> dict[int, int]:
            return  {
                r: (theta + 1) * (self.widths[r] // inner_width) for r in rs
            }
        if inner_width > 1:
            inner_thetas = sorted([p.coordinates[1] for p in region if p.coordinates[0] == min(rs)])
            if len(inner_thetas) == inner_width:
                # for full circle, we need two borders
                random.shuffle(inner_thetas)
                for i in range(0, 2, inner_width):
                    thetas = sorted(inner_thetas[i:i+2])
                    other_sides_by_r = [get_other_side(theta) for theta in thetas]
                    first = { p for p in region
                        if (other_sides_by_r[0][p.coordinates[0]] <= p.coordinates[1] < other_sides_by_r[1][p.coordinates[0]])}
                    second = region - first
                    name = f"cut full circle on {thetas}"
                    result.append(Division(name, (first, second)))

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
                            if (other_side_by_r[p.coordinates[0]] <= p.coordinates[1] < far_side_by_r[p.coordinates[0]])
                        }
                        right = region - left
                    else:
                        effective_theta = theta % inner_width
                        other_side_by_r = get_other_side(effective_theta)
                        right = { p for p in region
                            if (near_side_by_r[p.coordinates[0]] <= p.coordinates[1] < other_side_by_r[p.coordinates[0]])
                        }
                        left = region - right
                    name = f"cutting broken theta on {theta}"
                    result.append(Division(name, (left, right)))
            else:
                for theta in range(inner_thetas[0], inner_thetas[-1]):
                    other_side_by_r = get_other_side(theta)
                    right = { p for p in region
                        if (p.coordinates[1] < other_side_by_r[p.coordinates[0]])}
                    left = region - right
                    name = f"cutting simple theta on {theta}"
                    result.append(Division(name, (left, right)))
        return result


class PolygonGrid(CircleGrid):
    maze_type = "polygonmaze"

    def __init__(self, radius: int, sides: int, firstring: Optional[int] = None, center_cell: bool = True, slices: Optional[int] = None, **kwargs: Any) -> None:
        if firstring is None:
            firstring = sides
        self.sides = sides
        self.slices: int = sides
        if slices is not None:
            self.slices = slices
            kwargs['degrees'] = 360 * slices / sides
        super().__init__(radius, firstring=firstring, center_cell=center_cell, **kwargs)

    # key and value for size in draw_maze.ps
    @property
    def size_dict(self) -> dict[str, int | float | bool | list[int]]:
        return {'radius': self.radius, 'sides': self.sides, 'widths':  self.widths, 'center_cell': self.center_cell, 'slices': self.slices}

    @property
    def external_points(self) -> Sequence[tuple[float, ...]]:
        from math import cos, sin, tau
        # "physical" radius
        side_angle = tau / self.sides
        p_radius: float = self.radius
        if self.center_cell:
            p_radius += 0.5
        return [(0.0, 0.0)] + [
            (cos(side_angle * i) * p_radius, sin(side_angle * i) * p_radius)
            for i in range(self.slices + 1)
        ]

    @property
    def edges(self) -> tuple[Edge, ...]:
        result: list[Edge] = list(super().edges)
        inner_borders: list[tuple[Position, ...]] = []
        outer_r = len(self.widths) - 1
        side_len = self.widths[-1] // self.sides
        for i in range(self.slices):
            inner_borders.append(
                tuple(IntPosition((outer_r, (i * side_len) + j), self._gridname) for j in range(side_len))
            )
        outer_borders: list[tuple[Position, ...]] = []
        out = (1, 0)
        for border in inner_borders:
            outer_borders.append( tuple(add_direction(b, out) for b in border))
        return tuple(Edge(inner, outer) for inner, outer in zip(inner_borders, outer_borders))
