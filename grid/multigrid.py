# grids with cells in a square layout

from positions import Position, IntPosition, Direction, cardinal_directions, add_direction, manhattan, Coordinates
from typing import Optional, Any, Callable, Sequence
import random

from .maze import BaseGrid, ps_list

EdgeSpec = tuple[
    str,                # target grid
    int,                # target side (1-based)
    bool,               # whether to flip edge connection
]
GridSpec = tuple[
    type[BaseGrid],                     # type of subgrid
    tuple[int|bool, ...],               # args to subgrid init
    tuple[Optional[EdgeSpec], ...]      # target edge of each edge
]

class MultiGrid(BaseGrid):
    def __init__(self, 
        subgrids: dict[str, GridSpec],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.subgrids: dict[BaseGrid] = {}
        for grid_name, grid_spec in subgrids.items():
            grid_class, grid_args, edges = grid_spec
            self.subgrids[grid_name] = grid_spec[0](*grid_spec[1], grid=self._grid, gridname=grid_name)

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        raise ValueError("not overridden")

