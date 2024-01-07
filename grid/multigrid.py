# grids with cells in a square layout

from dataclasses import dataclass
from positions import Position, IntPosition, Direction, cardinal_directions, add_direction, manhattan, Coordinates
from typing import Optional, Any, Callable, Sequence, NamedTuple
import random
from math import atan2, sqrt, degrees, cos, sin, radians

from .maze import BaseGrid, ps_list, GridPosition

@dataclass
class EdgeSpec:
    target: str         # target grid
    side: int           # target side
    flip: bool          # whether to flip edge connection
    align: bool=False   # true to align grid along this edge

@dataclass
class GridSpec:
    grid_class: type[BaseGrid]                  # type of subgrid
    args: tuple[int|bool, ...]                  # args to subgrid init
    edges: tuple[Optional[EdgeSpec], ...]       # target edge of each edge
    location: tuple[float, float] = (0.0, 0.0)  # translation of this grid
    rotation: float = 0.0                       # rotation of grid
    scale: float = 1.0                          # scaling of grid
    kwargs: Optional[dict[str, Any]] = None     # kwargs for subgrid init

class MultiGrid(BaseGrid):
    def __init__(self, 
        subgrids: dict[str, GridSpec],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._subgrids: dict[str, BaseGrid] = {}
        self._edge_map: dict[Position, Position] = {}
        grid_positions: dict[str, GridPosition] = {}
        linewidth = kwargs.get('linewidth', 0.1)
        inset = kwargs.get('inset', 0.1)
        for gridname, grid_spec in subgrids.items():
            grid_kwargs = grid_spec.kwargs or {}
            grid_kwargs.update(kwargs)
            if grid_spec.scale != 1.0:
                grid_kwargs['linewidth'] = linewidth / grid_spec.scale
                grid_kwargs['inset'] = inset / grid_spec.scale
            grid_position = GridPosition(grid_spec.location, grid_spec.rotation, grid_spec.scale)
            grid_kwargs['grid_position'] = grid_position
            self._subgrids[gridname] = grid_spec.grid_class(
                *grid_spec.args,
                grid=self._grid,
                gridname=gridname,
                edge_map=self._edge_map,
                **grid_kwargs
            )
        # now that all grids exist, go through it again to deal with edges
        for gridname, grid_spec in subgrids.items():
            source_grid = self._subgrids[gridname]
            if len(grid_spec.edges) != len(source_grid.edges):
                raise ValueError(f"edges mismatch between grid and spec for {gridname} ({len(source_grid.edges)} != {len(grid_spec.edges)})")
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

        # deal with alignments
        aligned_grids: list[str] = []
        unaligned_grids: list[str] = []
        for gridname, grid_spec in subgrids.items():
            for edge in grid_spec.edges:
                if edge and edge.align:
                    unaligned_grids.append(gridname)
                    break
            if gridname not in unaligned_grids:
                aligned_grids.append(gridname)
        while unaligned_grids:
            progress = False
            alignment_candidates = list(unaligned_grids)
            for candidate in alignment_candidates:
                grid_spec = subgrids[candidate]
                grid = self._subgrids[candidate]
                alignment_edge: int = -1
                for i, edge in enumerate(grid_spec.edges):
                    if edge and edge.align:
                        alignment_edge = i
                        break
                if alignment_edge == -1:
                    raise ValueError(f"no alignment edge for {candidate}")
                alignment_edge_spec = grid_spec.edges[alignment_edge]
                assert alignment_edge_spec is not None
                target_name: str = alignment_edge_spec.target
                if target_name not in aligned_grids:
                    continue
                # align candidate with target
                target_grid = self._subgrids[target_name]
                target_side = alignment_edge_spec.side
                target_points: list[tuple[float, ...]] = list(target_grid.external_points[target_side:target_side + 2])
                if alignment_edge_spec.flip:
                    target_points = list(reversed(target_points))
                else:
                    raise NotImplementedError("aligning unflipped not supported")
                target_direction: tuple[float, ...] = tuple(t - s for s, t in zip (target_points[0], target_points[1]))

                # start from scratch
                grid.grid_position = GridPosition()
                grid_position = grid.grid_position
                # calculate rotation and scale
                local_points: list[tuple[float, ...]] = list(grid.external_points[alignment_edge:alignment_edge + 2])
                local_direction: tuple[float, ...] = tuple(t - s for s, t in zip (local_points[0], local_points[1]))
                target_angle = atan2(target_direction[1], target_direction[0])
                local_angle = atan2(local_direction[1], local_direction[0])
                grid_position.rotation = degrees(target_angle - local_angle)
                target_length = sqrt(target_direction[0]**2 + target_direction[1]**2)
                local_length = sqrt(local_direction[0]**2 + local_direction[1]**2)
                grid_position.scale = target_length / local_length
                # refetch local points, transformed
                local_points = list(grid.external_points[alignment_edge:alignment_edge + 2])
                #translated_rotate
                t_r: tuple[float, ...] = tuple(t - s for s, t in zip (local_points[0], target_points[0]))
                # since rotate is done last, I need to un-rotate the translate
                cos_r = cos(radians(-grid_position.rotation))
                sin_r = sin(radians(-grid_position.rotation))
                x: float = t_r[0] * cos_r - t_r[1] * sin_r
                y: float = t_r[0] * sin_r + t_r[1] * cos_r
                translate = (x, y)
                grid_position.location = translate
                unaligned_grids.remove(candidate)
                aligned_grids.append(candidate)
                progress = True
            if not progress:
                raise ValueError("unalignable multigrid")

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        gridname = start.gridname
        subgrid = self._subgrids[gridname]      # type: ignore [index]
        return subgrid.pos_adjacents(start)

    @property
    def external_points(self) -> list[tuple[float, ...]]:
        points: list[tuple[float, ...]] = []
        for gridname in self._subgrids.keys():
            for point in self._subgrids[gridname].external_points:
                points.append(point)
        return points

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        for gridname in self._subgrids.keys():
            output.append(f"% grid {gridname}")
            output.append(self._subgrids[gridname].ps_instructions(path=path, field=field))
        return "\n".join(output)
