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
        self.edge_map: dict[Position, Position] = {}
        for grid_name, grid_spec in subgrids.items():
            self._subgrids[grid_name] = grid_spec.grid_class(
                *grid_spec.args,
                grid=self._grid,
                gridname=grid_name
            )
        # now that all grids exist, go through it again to deal with edges
        for grid_name, grid_spec in subgrids.items():
            source_grid = self._subgrids[grid_name]
            for i, edge in enumerate(grid_spec.edges):
                if edge is not None:
                    target_grid = self._subgrids[edge.target]
                    source_edge = source_grid.edges[i].outer
                    target_edge = target_grid.edges[edge.side].inner
                    if edge.flip:
                        target_edge = tuple(reversed(target_edge))
                    if len(source_edge) != len(target_edge):
                        raise ValueError(f"edge len between {grid_name}:{i} and {edge.target}:{edge.side}")
                    for s_pos, t_pos in zip(source_edge, target_edge):
                        self.edge_map[s_pos] = t_pos

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        gridname = start.gridname
        subgrid = self._subgrids[gridname]      # type: ignore [index]
        neighbors: list[Position] = list(subgrid.pos_adjacents(start))
        neighbors = [self.edge_map.get(n, n) for n in neighbors]
        neighbors.extend(super().pos_adjacents(start))
        return neighbors

