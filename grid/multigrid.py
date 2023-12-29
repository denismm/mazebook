# grids with cells in a square layout

from positions import Position, IntPosition, Direction, cardinal_directions, add_direction, manhattan, Coordinates
from typing import Optional, Any, Callable, Sequence, NamedTuple
import random

from .maze import BaseGrid, ps_list

EdgeSpec = NamedTuple('EdgeSpec', [
    ('target', str),               # target grid
    ('side', int),                # target side
    ('flip', bool),               # whether to flip edge connection
])
GridSpec = NamedTuple('GridSpec', [
    ('grid_class', type[BaseGrid]),             # type of subgrid
    ('args', tuple[int|bool, ...]),             # args to subgrid init
    ('edges', tuple[Optional[EdgeSpec], ...]),  # target edge of each edge
])

class MultiGrid(BaseGrid):
    def __init__(self, 
        subgrids: dict[str, GridSpec],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._subgrids: dict[str, BaseGrid] = {}
        for grid_name, grid_spec in subgrids.items():
            self._subgrids[grid_name] = grid_spec.grid_class(
                *grid_spec.args,
                grid=self._grid,
                gridname=grid_name
            )

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        gridname = start.gridname
        subgrid = self._subgrids[gridname]      # type: ignore [index]
        neighbors: list[Position] = list(subgrid.pos_adjacents(start))
        neighbors.extend(super().pos_adjacents(start))
        return neighbors

