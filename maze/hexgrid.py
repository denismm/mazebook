# grids that use hexagonal geometry

from .positions import Position, IntPosition, Direction, add_direction
from typing import Optional, Any, Sequence

from .grid import BaseGrid, SingleSizeGrid, Edge

hex_directions: tuple[Direction, ...] = ( 
    (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, 0)
)

class HexBaseGrid(SingleSizeGrid):
    neighbor_directions: tuple[tuple[Direction, ...], ...] = ()

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        all_nd = self.neighbor_directions
        directions_index = sum(start.coordinates[:2]) % len(all_nd)
        return all_nd[directions_index]

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        neighbor_directions = self.neighbor_directions_for_start(start)
        neighbors: list[Position] = [add_direction(start, dir) for dir in neighbor_directions]
        if len(neighbors) == 0:
            raise ValueError(f"why no neighbors of {start}?")
        return self.adjust_adjacents(start, neighbors)

class HexGrid(HexBaseGrid):
    def __init__(self, radius: int, **kwargs: Any) -> None:
        super().__init__(radius, **kwargs)
        self.radius = radius
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if abs(i - j) <= radius:
                    self._add_column((i, j))

    neighbor_directions: tuple[tuple[Direction, ...], ...] = (hex_directions,)

    @property
    def size_dict(self) -> dict[str, int | float | bool | list[int]]:
        return {"radius": self.radius}

    maze_type = "hexmaze"

    @property
    def external_points(self) -> Sequence[tuple[float, ...]]:
        # "physical" radius
        # fake it for now
        p_radius: float = self.radius + 0.5
        results = [ (-p_radius, -p_radius), (p_radius, p_radius)]
        return [self.transform_point(point) for point in results]

class TriGrid(HexBaseGrid):
    def __init__(self, width: int, **kwargs: Any) -> None:
        super().__init__(width, **kwargs)
        self.width = width
        max_sum = 3 * (width - 1)
        for sum in range( max_sum + 1):
            if sum % 3 != 1:
                start_i = (sum + 1) // 3
                for i in range(start_i, sum - start_i + 1):
                    j = sum - i
                    self._add_column((i, j))

    neighbor_directions: tuple[tuple[Direction, ...], ...] = (
            ((1, 1), (-1, 0), (0, -1),),
            (),
            ((0, 1), (-1, -1), (1, 0),)
        )

    @property
    def size_dict(self) -> dict[str, int | float | bool | list[int]]:
        return {"width": self.width}

    maze_type = "trimaze"

    @property
    def external_points(self) -> Sequence[tuple[float, ...]]:
        from math import sqrt
        results = [
            (self.width, 0.0),
            (self.width /2, self.width * sqrt(3) / 2),
            (0.0, 0.0),
        ]
        return [self.transform_point(point) for point in results]

    @property
    def edges(self) -> tuple[Edge, ...]:
        result: list[Edge] = []
        w = self.width
        gridname = self._gridname
        inner_borders: list[tuple[Position, ...]] = [
            tuple(IntPosition((2*w - i, i), gridname) for i in range(w - 1, 2 * w - 1)),
            tuple(IntPosition((i, 2*i), gridname) for i in reversed(range(w))),
            tuple(IntPosition((2*i, i), gridname) for i in range(w)),
        ]
        directions = self.neighbor_directions[0]
        outer_borders: list[tuple[Position, ...]] = []
        for border, d in zip(inner_borders, directions):
            outer_borders.append( tuple(add_direction(b, d) for b in border))
        return tuple(Edge(inner, outer) for inner, outer in zip(inner_borders, outer_borders))


