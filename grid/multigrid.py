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
        self._subgrids: dict[BaseGrid] = {}
        for grid_name, grid_spec in subgrids.items():
            grid_class, grid_args, edges = grid_spec
            self._subgrids[grid_name] = grid_class(
                *grid_args,
                grid=self._grid,
                gridname=grid_name
            )

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        gridname = start.gridname
        subgrid = self._subgrids[gridname]
        neighbors: list[Position] = list(subgrid.pos_adjacents(start))
        neighbors.extend(super().pos_adjacents(start))
        return neighbors

