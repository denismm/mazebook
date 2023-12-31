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
    ('location', tuple[int, int]),              # translation of this grid
])

class MultiGrid(BaseGrid):
    def __init__(self, 
        subgrids: dict[str, GridSpec],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._subgrids: dict[str, BaseGrid] = {}
        self._edge_map: dict[Position, Position] = {}
        self.offsets: dict[str, tuple[float, ...]] = {}
        for gridname, grid_spec in subgrids.items():
            self._subgrids[gridname] = grid_spec.grid_class(
                *grid_spec.args,
                grid=self._grid,
                gridname=gridname,
                edge_map=self._edge_map,
                **kwargs
            )
            self.offsets[gridname] = grid_spec.location
        # now that all grids exist, go through it again to deal with edges
        for gridname, grid_spec in subgrids.items():
            source_grid = self._subgrids[gridname]
            for i, edge in enumerate(grid_spec.edges):
                if edge is not None:
                    target_grid = self._subgrids[edge.target]
                    source_edge = source_grid.edges[i].outer
                    target_edge = target_grid.edges[edge.side].inner
                    if edge.flip:
                        target_edge = tuple(reversed(target_edge))
                    if len(source_edge) != len(target_edge):
                        raise ValueError(f"edge len between {gridname}:{i} and {edge.target}:{edge.side}")
                    for s_pos, t_pos in zip(source_edge, target_edge):
                        self._edge_map[s_pos] = t_pos

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        gridname = start.gridname
        subgrid = self._subgrids[gridname]      # type: ignore [index]
        return subgrid.pos_adjacents(start)

    @property
    def bounding_box(self) -> tuple[float, ...]:
        bbox: list[float] = [0.0] * 4
        for gridname in self._subgrids.keys():
            grid_bbox = self._subgrids[gridname].bounding_box
            grid_offset = self.offsets[gridname] * 2
            adjusted_bbox = [ b + o for b, o in zip(grid_bbox, grid_offset)]
            for i in range(2):
                bbox[i] = min(adjusted_bbox[i], bbox[i])
                bbox[i+2] = max(adjusted_bbox[i+2], bbox[i+2])
        return tuple(bbox)

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        for gridname in self._subgrids.keys():
            grid_offset = self.offsets[gridname]
            translation = ' '.join([str(f) for f in grid_offset])
            output.append(f'% grid {gridname}')
            output.append('gsave')
            output.append(f"{translation} translate")
            output.append(self._subgrids[gridname].ps_instructions(path=path, field=field))
            output.append('grestore')
        return "\n".join(output)
