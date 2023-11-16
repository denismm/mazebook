# grids that use hexagonal geometry

from positions import Position, IntPosition, Direction, add_direction
from typing import Optional, Any, Sequence

from .maze import BaseGrid, SingleSizeGrid, ps_list

hex_directions: tuple[Direction, ...] = ( 
    (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, 0)
)

class HexBaseGrid(SingleSizeGrid):
    neighbor_directions: tuple[tuple[Direction, ...], ...] = ()

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        all_nd = self.neighbor_directions
        directions_index = sum(start.coordinates) % len(all_nd)
        return all_nd[directions_index]

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        neighbor_directions = self.neighbor_directions_for_start(start)
        neighbors = [add_direction(start, dir) for dir in neighbor_directions]
        return neighbors

class HexGrid(HexBaseGrid):
    def __init__(self, radius: int, **kwargs: Any) -> None:
        super().__init__(radius, **kwargs)
        self.radius = radius
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if abs(i - j) <= radius:
                    self._add_cell((i, j))

    neighbor_directions: tuple[tuple[Direction, ...], ...] = (hex_directions,)

    @property
    def size_dict(self) -> dict[str, int | list[int]]:
        return {"radius": self.radius}

    maze_type = "hexmaze"

    @property
    def png_alignment(self) -> list[str]:
        return [str(-1 * (self.radius + 0.65)), 'd', 'd', 'd']

    @property
    def ps_alignment(self) -> str:
        return f"72 softscale 4.25 5.5 translate 4 {self.radius + 0.5} div dup scale"

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
                    self._add_cell((i, j))

    neighbor_directions: tuple[tuple[Direction, ...], ...] = (
            ((1, 1), (-1, 0), (0, -1),),
            (),
            ((0, 1), (-1, -1), (1, 0),)
        )

    @property
    def size_dict(self) -> dict[str, int | list[int]]:
        return {"width": self.width}

    maze_type = "trimaze"

    @property
    def png_alignment(self) -> list[str]:
        from math import sqrt
        return [str(-1.3), 'd', str((self.width - 1) * sqrt(3) + 1.3), str(self.width * 1.5 + 0.5)]

    @property
    def ps_alignment(self) -> str:
        return f"72 softscale 0.25 dup translate 8 {self.width} 3 sqrt mul div dup scale 3 sqrt half dup translate"
