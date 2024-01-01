# grids with cells in a square layout

from dataclasses import dataclass
from positions import Position, IntPosition, Direction, cardinal_directions, add_direction, manhattan, Coordinates
from typing import Optional, Any, Callable, Sequence, NamedTuple
import random

from .maze import BaseGrid, ps_list

EdgeSpec = NamedTuple('EdgeSpec', [
    ('target', str),               # target grid
    ('side', int),                # target side
    ('flip', bool),               # whether to flip edge connection
])
@dataclass
class GridSpec:
    grid_class: type[BaseGrid]                  # type of subgrid
    args: tuple[int|bool, ...]                  # args to subgrid init
    edges: tuple[Optional[EdgeSpec], ...]       # target edge of each edge
    location: tuple[float, float]               # translation of this grid
    rotation: float = 0.0                       # rotation of grid
    scale: float = 1.0                          # scaling of grid

@dataclass
class GridPosition:
    location: tuple[float, float]               # translation of this grid
    rotation: float = 0.0                       # rotation of grid
    scale: float = 1.0                          # scaling of grid

class MultiGrid(BaseGrid):
    def __init__(self, 
        subgrids: dict[str, GridSpec],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._subgrids: dict[str, BaseGrid] = {}
        self._edge_map: dict[Position, Position] = {}
        self.grid_positions: dict[str, GridPosition] = {}
        for gridname, grid_spec in subgrids.items():
            self._subgrids[gridname] = grid_spec.grid_class(
                *grid_spec.args,
                grid=self._grid,
                gridname=gridname,
                edge_map=self._edge_map,
                **kwargs
            )
            self.grid_positions[gridname] = GridPosition(grid_spec.location, grid_spec.rotation, grid_spec.scale)
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
                        raise ValueError(f"edge len mismatch between {gridname}:{i} ({len(source_edge)}) and {edge.target}:{edge.side} ({len(target_edge)})")
                    for s_pos, t_pos in zip(source_edge, target_edge):
                        self._edge_map[s_pos] = t_pos

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        gridname = start.gridname
        subgrid = self._subgrids[gridname]      # type: ignore [index]
        return subgrid.pos_adjacents(start)

    @property
    def external_points(self) -> list[tuple[float, ...]]:
        from math import cos, sin, radians
        points: list[tuple[float, ...]] = []
        for gridname in self._subgrids.keys():
            grid_pos = self.grid_positions[gridname]
            for point in self._subgrids[gridname].external_points:
                if grid_pos.scale:
                    point = tuple( x * grid_pos.scale for x in point)
                if grid_pos.location:
                    point = tuple( x + y for x, y in zip(point, grid_pos.location))
                if grid_pos.rotation:
                    cos_t = cos(radians(grid_pos.rotation))
                    sin_t = sin(radians(grid_pos.rotation))
                    x: float = point[0] * cos_t - point[1] * sin_t
                    y: float = point[0] * sin_t + point[1] * cos_t
                    point = (x, y)
                points.append(point)
        return points

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        for gridname in self._subgrids.keys():
            grid_pos = self.grid_positions[gridname]
            grid_offset = grid_pos.location
            translation = ' '.join([str(f) for f in grid_offset])
            output.append(f'% grid {gridname}')
            output.append('gsave')
            if grid_pos.rotation:
                output.append(f"{grid_pos.rotation} rotate")
            output.append(f"{translation} translate")
            if grid_pos.scale:
                output.append(f"{grid_pos.scale} softscale")
            output.append(self._subgrids[gridname].ps_instructions(path=path, field=field))
            output.append('grestore')
        return "\n".join(output)
