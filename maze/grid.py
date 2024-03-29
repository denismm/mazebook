from .positions import Position, LinkPosition, IntPosition, Direction, cardinal_directions, add_direction, Coordinates
import random
import os
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Optional, Callable, NamedTuple, Sequence
from typing_extensions import Protocol
from itertools import product
from numbers import Real
from dataclasses import dataclass
import json

class Cell():
    def __init__(self, location: Position) -> None:
        self.position = location
        self.links: set[Position] = set()

    def add_link(self, link: Position) -> None:
        self.links.add(link)

    def remove_link(self, link: Position) -> None:
        self.links.discard(link)

    @property
    def flat_links(self) -> set[tuple[Optional[str], Coordinates]]:
        # for weaving it can be useful to ignore the position type
        return set([p.flattened for p in self.links])

# convenience for ps printing
def ps_list(iterable: Iterable[Any]) -> str:
    return '[' + ' '.join([str(x) for x in iterable]) + ']'

def toppath():
    return os.path.dirname(__file__) + '/..'

class PrinterFunction(Protocol): 
    def __call__(self,
        maze: 'BaseGrid',
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str) -> None: ...

class MazeFunction(Protocol):
    def __call__(self,
        maze: 'BaseGrid') -> None: ...

Division = NamedTuple("Division", [
    ("name", str),
    ("regions", tuple[set[Position], set[Position]]),
])

# an edge of a grid is the positions inside and the positions outside
Edge = NamedTuple('Edge', [
    ('inner', tuple[Position, ...]),
    ('outer', tuple[Position, ...]),
])

@dataclass
class GridPosition:
    location: tuple[float, float] = (0.0, 0.0)  # translation of this grid
    rotation: float = 0.0                       # rotation of grid
    scale: float = 1.0                          # scaling of grid
NullPosition = GridPosition()

class BaseGrid():
    _grid: dict[Position, Cell]
    _gridname: Optional[str]
    _edge_map: dict[Position, Position]

    def __init__(self, **kwargs: Any) -> None:
        if 'grid' in kwargs:
            self._grid = kwargs.pop('grid')
            self._gridname = kwargs.pop('gridname')
        else:
            self._grid = {}
            self._gridname = None

        self._edge_map = kwargs.pop('edge_map', {})
        self.set_options(**kwargs)

    def _add_column(self, coordinates: Coordinates) -> None:
        'Add a cell to the grid on every hyper plane'
        ranges: list[range] = []
        for width in self.hyper:
            ranges.append(range(width))
        for addend in product(*ranges):
            self._add_cell(coordinates + addend)

    def _add_cell(self, p_or_c: Position|Coordinates) -> None:
        if isinstance(p_or_c, Position):
            position = p_or_c
        else:
            position = IntPosition(p_or_c, gridname=self._gridname)
        self._grid[position] = Cell(position)

    algorithms: dict[str, MazeFunction] = {}

    @classmethod
    def algo(cls, mf: MazeFunction) -> MazeFunction:
        cls.algorithms[mf.__name__] = mf        # type: ignore [attr-defined] # fixed in next mypy version
        return mf

    outputs: dict[str, PrinterFunction] = {}

    @classmethod
    def printer(cls, pf: PrinterFunction) -> PrinterFunction:
        cls.outputs[pf.__name__[:-6]] = pf      # type: ignore [attr-defined] # fixed in next mypy version
        return pf

    def __contains__(self, position: Position) -> bool:
        return position in self._grid

    def __getitem__(self, position: Position) -> Cell:
        return self._grid[position]

    def __len__(self) -> int:
        return len(self._grid)

    def set_options(self,
        hyper: Optional[list[int]] = None,
        weave: Optional[bool] = False,
        pathcolor: Optional[list[float]] = None,
        bg: Optional[bool] = None,
        noflat: Optional[bool] = None,
        linewidth: Optional[float] = None,
        inset: Optional[float] = None,
        pixels: Optional[float] = None,
        room_size: Optional[int] = None,
        grid_position: GridPosition = NullPosition,
    ) -> None:
        self.weave = weave
        self.hyper = hyper or []
        self.pathcolor = pathcolor
        self.bg = bg
        self.noflat = noflat
        self.linewidth = linewidth
        self.inset = inset
        self.pixels = pixels or 20.0
        self.room_size = room_size or 1
        self.grid_position = grid_position

    # quick way to get a position for coordinates in this grid
    def _pos(self, coordinates: Coordinates) -> Position:
        return IntPosition(coordinates, self._gridname)

    def connect(self, first: Position, second: Position) -> None:
        # what if there's a distance between the two cells?
        if IntPosition(second.coordinates, second.gridname) in self.pos_adjacents(first):
            self._grid[first].add_link(second)
            self._grid[second].add_link(first)
            return
        # link square is between both, add link entry
        link_pos = self.find_link_pos(first, second)
        self._add_cell(link_pos)
        self.connect(first, link_pos)
        self.connect(second, link_pos)

    def disconnect(self, first: Position, second: Position) -> None:
        self._grid[first].remove_link(second)
        self._grid[second].remove_link(first)

    def find_link_pos(self, first: Position, second: Position) -> Position:
        # general solution
        first_neighbors = self.pos_adjacents(first)
        second_neighbors = self.pos_adjacents(second)
        intersection_positions = set(first_neighbors) & set(second_neighbors)
        if len(intersection_positions) == 0:
            raise ValueError(f"no common cell between {first} and {second} ({first_neighbors}, {second_neighbors}")
        if len(intersection_positions) > 1:
            intersection_positions = { p for p in intersection_positions if len(self.pos_adjacents(p)) == 4 }
        if len(intersection_positions) > 1:
            raise ValueError(f"too many common cells between {first} and {second} ({first_neighbors}, {second_neighbors}, {intersection_positions}")
        return LinkPosition.from_position(intersection_positions.pop())

    def random_point(self) -> Position:
        return (random.choice(list(self._grid.keys())))

    def pos_neighbors(self, start: Position) -> list[Position]:
        if not self.weave:
            return [p for p in self.pos_adjacents(start) if p in self]
        # for each direction, check for weave-ability
        absolute_neighbors = self.pos_adjacents(start)
        neighbors: list[Position] = []
        for target_pos in absolute_neighbors:
            if target_pos not in self:
                continue
            target_neighbors = self.pos_adjacents(target_pos)
            # not tunnelable if not square
            if len(target_neighbors) != 4:
                neighbors.append(target_pos)
                continue
            target_cell = self[target_pos]
            # is this already connected?
            link_count = len(target_cell.links)
            # only tunnelable if straight across
            if link_count != 2:
                neighbors.append(target_pos)
                continue
            back_index = target_neighbors.index(start)
            other_side = target_neighbors[(back_index + 2) % 4]
            if other_side in self:
                if not ({start.flattened, other_side.flattened} & target_cell.flat_links):
                    # tunnel ok!
                    neighbors.append(other_side)
        return neighbors

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        # must return adjacent cells in order, including those not in grid
        raise NotImplementedError('pos_adjacents')

    def adjust_adjacents(self, start: Position, adjacents: Sequence[Position]) -> Sequence[Position]:
        # this appends hyper directions to subclass results
        # and also adjusts grid-crossing links
        results = [self._edge_map.get(a, a) for a in adjacents]
        hyper_length = len(self.hyper)
        for i in range(hyper_length):
            for updown in (-1, 1):
                direction: Direction = ((0, ) * (2 + i)) + (updown, )
                results.append(add_direction(start, direction))
        return results

    @property
    def edges(self) -> tuple[Edge, ...]:
        raise NotImplementedError("edges")

    @property
    def external_points(self) -> Sequence[tuple[float, ...]]:
        raise NotImplementedError("external_points")

    def points_for_edge(self, edge_num: int) -> Sequence[tuple[float, ...]]:
        points: list[tuple[float, ...]] = []
        external_points = self.external_points
        for i in range(2):
            j = (edge_num + i) % len(external_points)
            points.append(external_points[j])
        return points

    def dijkstra(self, start: Position) -> list[set[Position]]:
        seen: set[Position] = {start}
        far_points: list[set[Position]] = [{start}]
        while True:
            frontier: set[Position] = set()
            for point in far_points[-1]:
                new_points = self[point].links - seen
                frontier |= new_points
                seen |= new_points
            if len(frontier) == 0:
                break
            far_points.append(frontier)

        return far_points

    def longest_path(self) -> list[Position]:
        # start at random point
        start: Position = self.random_point()
        # get farthest point
        first_point = sorted(self.dijkstra(start)[-1])[0]
        # get farthest point from there
        distance_points = self.dijkstra(first_point)
        second_point = sorted(distance_points[-1])[0]
        # get path
        path: list[Position] = [second_point]
        distance = len(distance_points) - 1
        while distance > 0:
            distance -= 1
            possibles = self[path[-1]].links & distance_points[distance]
            path.append(sorted(possibles)[0])
        return path

    def node_analysis(self) -> dict[int, int]:
        # how many positions have 0, 1, 2, ...  connections
        nodes_for_links: dict[int, int] = defaultdict(lambda: 0)
        for cell in self._grid.values():
            nodes_for_links[len(cell.links)] += 1
        return dict(nodes_for_links)

    def dead_ends(self) -> list[Position]:
        ret: list[Position] = []
        for location, cell in self._grid.items():
            if len(cell.links) == 1:
                ret.append(location)
        return ret

    def region_divisions(self, region: set[Position]) -> list[Division]:
        raise NotImplementedError("region_divisions")

    def braid(self, proportion: float) -> None:
        # rule out forced dead-ends, such as the corner of a triangle
        dead_ends = [de for de in self.dead_ends() if len(self.pos_neighbors(de)) > 1]
        target_dead_ends = round(len(dead_ends) * (1 - proportion))
        while len(dead_ends) > target_dead_ends:
            # pick a dead end
            braidable = random.choice(dead_ends)
            # braid to a dead end or a passage
            current_link = self[braidable].links
            all_neighbors = self.pos_neighbors(braidable)
            possible_targets = [p for p in all_neighbors if p not in current_link]
            dead_targets: list[Position] = []
            other_targets: list[Position] = []
            for p in possible_targets:
                if len(self[p].links) == 1:
                    dead_targets.append(p)
                else:
                    other_targets.append(p)
            targets = dead_targets or other_targets
            target = random.choice(targets)
            self.connect(braidable, target)
            dead_ends.remove(braidable)
            try:
                dead_ends.remove(target)
            except ValueError:
                pass

    # function in draw_maze.ps to draw this kind of grid will be "draw" + this
    maze_type = ""

    # key and value for size in draw_maze.ps
    @property
    def size_dict(self) -> dict[str, int | float | bool | list[int]]:
        raise NotImplementedError("size_dict")

    ### Printing support 

    def transform_point(self, point: tuple[float, ...]) -> tuple[float, ...]:
        from math import cos, sin, radians
        grid_pos = self.grid_position
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
        return point

    # corners of bounding box: lower left, top right
    @property
    def bounding_box(self) -> tuple[float, ...]:
        bounding_box: list[float] = [0.0] * 4
        for point in self.external_points:
            for i in range(2):
                bounding_box[i] = min(point[i], bounding_box[i])
                bounding_box[i+2] = max(point[i], bounding_box[i+2])
        return tuple(bounding_box)

    @property
    def hypersteps(self) -> list[tuple[float, ...]]:
        result: list[tuple[float, ...]] = []
        bbox = self.bounding_box
        if len(self.hyper) >= 1:
            result.append((1 + bbox[2] - bbox[0], 0.0))
        if len(self.hyper) >= 2:
            result.append((0.0, 1 + bbox[3] - bbox[1]))
        if len(self.hyper) > 2:
            raise ValueError("can't draw more than 2 hyper dimensions")
        return result

    @property
    def true_bounding_box(self) -> tuple[float, ...]:
        bbox = list(self.bounding_box)
        hypersteps = self.hypersteps
        for i in range(len(self.hyper)):
            for c in range(2):
                bbox[2+c] += hypersteps[i][c] * (self.hyper[i] - 1)
        return tuple(bbox)

    # start of ps code
    @property
    def ps_prologue(self) -> str:
        draw_maze = toppath() + '/includes/draw_maze.ps'
        if self.noflat:
            return f"%!\n({draw_maze}) run\n"
        else:
            with open(draw_maze, 'r') as f:
                include = f.read()
                return include

    # ps command to align ps output
    @property
    def ps_alignment(self) -> str:
        bbox = self.true_bounding_box
        corners = ( (bbox[0], bbox[1]), (bbox[2], bbox[3]) )
        target_sizes = (8, 10.5)
        box_sizes = (corners[1][c] - corners[0][c] for c in range(2))
        scale = min([t / b for t, b in zip(target_sizes, box_sizes)])
        box_centers = ( (corners[0][c] + corners[1][c]) / 2 for c in range(2))
        translate = ' '. join([str(-f) for f in box_centers])
        return " ".join([
            "72 softscale 4.25 5.5 translate", 
            f"{scale} dup scale",
            f"{translate} translate", 
        ])

    # position args for pstopng
    @property
    def png_alignment(self) -> list[str]:
        bbox = self.true_bounding_box
        margin = 0.15
        borders = [
            bbox[0]- margin, bbox[1] - margin,
            bbox[2] + margin, bbox[3] + margin
        ]
        return [str(border) for border in borders]

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        grid_position = self.grid_position
        grid_offset = grid_position.location
        translation = ' '.join([str(f) for f in grid_offset])
        output.append('gsave')
        if grid_position.rotation:
            output.append(f"{grid_position.rotation} rotate")
        output.append(f"{translation} translate")
        if grid_position.scale and grid_position.scale != 1.0:
            output.append(f"{grid_position.scale} softscale")

        output.append("<<")
        # size
        for size_key, size_value in self.size_dict.items():
            if isinstance(size_value, list):
                output.append(f"/{size_key} {ps_list(size_value)}")
            elif isinstance(size_value, bool):
                output.append(f"/{size_key} {str(size_value).lower()}")
            elif isinstance(size_value, Real):
                output.append(f"/{size_key} {size_value}")
            else:
                raise ValueError(f"strange type in size_dict: {size_key} ({type(size_value)}")
        # make field lookup
        field_for_position: dict[Position, int] = {}
        if field:
            for i, frontier in enumerate(field):
                for position in frontier:
                    if position.gridname == self._gridname:
                        field_for_position[position] = i
        if self.hyper:
            output.append("/hyperstep " + ps_list([
                ps_list(step) for step in self.hypersteps
            ]) )
        if self.weave:
            output.append("/weave true")
        if self.pathcolor:
            output.append("/pathcolor " + ps_list(self.pathcolor))
        if self.bg:
            output.append("/bg true")
        if self.linewidth:
            output.append(f"/linewidth {self.linewidth}")
        if self.inset:
            output.append(f"/inset {self.inset}")
        # cells
        output.append("/cells [")
        # draw link cells first
        for k in sorted(self._grid.keys()):
            if k.gridname != self._gridname:
                continue
            v = self._grid[k]
            walls = self.walls_for_cell(v)
            walls_text = ps_list([str(w).lower() for w in walls])
            field_text = str(field_for_position.get(k, 0))
            links_text = ps_list(sorted(v.links))
            output.append(ps_list([ k.ps_rep, walls_text, field_text ]) + f" % {links_text}")
        output.append("]")
        if path:
            output.append("/path ")
            output.append(ps_list([
                position.ps_rep for position in path
            ]))
        if field:
            output.append("/field ")
            output.append(ps_list([
                ps_list([
                    position.ps_rep for position in frontier
                ]) for frontier in field
            ]))
        output.append(f">> draw{self.maze_type}")
        output.append('grestore')
        return "\n".join(output)

    def walls_for_cell(self, cell: Cell) -> list[bool]:
        return [npos.flattened not in cell.flat_links for npos in self.pos_adjacents(cell.position)]

    def structured_data(self,
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str
    ) -> dict[str, Any]:
        output_data: dict[str, Any] = {}
        # size
        output_data.update(self.size_dict)
        if self.weave:
            output_data['weave'] = True
        output_cells: list[dict[str, Position | list[Position]]] = []
        for k, v in self._grid.items():
            cell_info: dict[str, Position| list[Position]] = {
                "position": k.json_rep,
                "links": [p.json_rep for p in sorted(v.links)]
            }
            output_cells.append(cell_info)
        output_data['cells'] = output_cells
        if path:
            output_data['path'] = [p.json_rep for p in path]
        if field:
            output_data['field'] = [
                [p.json_rep for p in frontier]
            for frontier in field]
        output_data['self'] = self.maze_type
        return output_data

    def print(self,
        print_method: str,
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str
) -> None:
        self.outputs[print_method](self, path, field, **kwargs)

    def generate_maze(self, maze_algorithm: str) -> None:
        self.algorithms[maze_algorithm](self)

class SingleSizeGrid(BaseGrid):
    def __init__(self, size: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)

### Maze Generation Algorithms

@BaseGrid.algo
def aldous_broder(maze: BaseGrid) -> None:
    "wander, extending maze when you leave visited area"
    current: Position = maze.random_point()
    visited: set[Position] = {current}
    steps = 0
    while len(visited) < len(maze):
        steps += 1
        next: Position = random.choice(maze.pos_neighbors(current))
        if next not in visited:
            maze.connect(current, next)
            visited.add(next)
        current = next

@BaseGrid.algo
def wilson(maze: BaseGrid) -> None:
    "wander from random points, chopping off loops, until visited is found"
    start: Position = maze.random_point()
    unvisited: set[Position] = set(maze._grid.keys())
    visited: set[Position] = {start}
    unvisited -= visited
    steps: int = 0
    while len(unvisited):
        current: Position = random.choice(sorted(unvisited))
        path: list[Position] = [current]
        steps += 1
        while path[-1] not in visited:
            steps += 1
            next: Position = random.choice(maze.pos_neighbors(current))
            if next in path:
                # chop out loop
                path = path[:(path.index(next))]
            path.append(next)
            current = next
        # connect path
        for i in range(len(path) - 1):
            current = path[i]
            next = path[i + 1]
            maze.connect(current, next)
            visited.add(current)
        unvisited -= visited

@BaseGrid.algo
def hunt_kill(maze: BaseGrid) -> None:
    current: Position = maze.random_point()
    visited: set[Position] = {current}
    # break when we fill the grid
    while True:
        # break when we paint ourselves into a corner
        while True:
            next_options = set(maze.pos_neighbors(current)) - visited
            if not next_options:
                break
            next: Position = random.choice(sorted(next_options))
            maze.connect(current, next)
            visited.add(next)
            current = next
        # choose a new start if possible
        if len(visited) == len(maze):
            return
        for start_option in sorted(maze._grid.keys()):
            if start_option not in visited:
                connection_options = set(maze.pos_neighbors(start_option)) & visited
                if connection_options:
                    connection: Position = random.choice(sorted(connection_options))
                    maze.connect(connection, start_option)
                    current = start_option
                    visited.add(current)
                    break

@BaseGrid.algo
def backtrack(maze: BaseGrid) -> None:
    stack: list[Position] = [maze.random_point()]
    visited: set[Position] = {stack[0]}
    while stack:
        next_options = set(maze.pos_neighbors(stack[-1])) - visited
        if next_options:
            next: Position = random.choice(sorted(next_options))
            maze.connect(stack[-1], next)
            stack.append(next)
            visited.add(next)
        else:
            stack.pop()

@BaseGrid.algo
def kruskal(maze: BaseGrid) -> None:
    # set of possible connections
    connection_pool: set[tuple[Position, Position]] = set()
    for location in maze._grid.keys():
        for neighbor in maze.pos_neighbors(location):
            if neighbor > location:
                connection_pool.add((location, neighbor))
    # sets of connected points
    point_groups: dict[int, set[Position]] = {}
    next_group: int = 0
    # mapping back to groups
    group_for_point: dict[Position, int] = {}

    # connect two points if they're not in the same group,
    # creating or merging groups as necessary
    def k_connect(connection: tuple[Position, Position]) -> None:
        nonlocal next_group
        groups_for_connection: list[Optional[int]] = [
            group_for_point.get(p, None) for p in connection]
        if None in groups_for_connection:
            if groups_for_connection == [None, None]:
                # neither point is in a group, make a new group
                point_groups[next_group] = set(connection)
                maze.connect(*connection)
                for p in connection:
                    group_for_point[p] = next_group
                next_group += 1
            else:
                # one point is in a group, put the other into the same
                target_group = [g for g in groups_for_connection if g is not None][0]
                maze.connect(*connection)
                for p in connection:
                    point_groups[target_group].add(p)
                    group_for_point[p] = target_group
        elif groups_for_connection[0] != groups_for_connection[1]:
            # the points are in different groups, merge them
            target_group, source_group = sorted([g for g in groups_for_connection if g is not None])
            maze.connect(*connection)
            point_groups[target_group] |= point_groups[source_group]
            for p in point_groups[source_group]:
                group_for_point[p] = target_group
            del point_groups[source_group]
        else:
            # the points are in the same group, don't connect them
            pass

    # add some weaves - how many? for now, as many as possible
    if maze.weave:
        weaveable_points: set[Position] = set(maze._grid.keys())
        while weaveable_points:
            weave_pos = random.choice(sorted(weaveable_points))
            weaveable_points.remove(weave_pos)
            if weave_pos in group_for_point:
                continue
            neighbors = maze.pos_adjacents(weave_pos)
            if len(neighbors) != 4:
                continue
            neighborset = set(neighbors)
            if neighborset & set(group_for_point.keys()):
                continue
            if not neighborset <= set(maze._grid.keys()):
                continue
            weaveable_points -= neighborset
            link_pos = LinkPosition.from_position(weave_pos)
            link_cell = Cell(link_pos)
            maze._grid[link_pos] = link_cell
            top_mod = random.randrange(2)

            top_group = next_group
            point_groups[top_group] = { weave_pos }
            group_for_point[weave_pos] = top_group
            next_group += 1

            bottom_group = next_group
            point_groups[bottom_group] = { link_pos }
            group_for_point[link_pos] = bottom_group
            next_group += 1

            for i, neighbor in enumerate(neighbors):
                if i % 2 == top_mod:
                    target_pos = weave_pos
                else:
                    target_pos = link_pos
                k_connect((neighbor, target_pos))
                connection_pool.remove(tuple(sorted((neighbor, weave_pos)))) # type: ignore [arg-type]

    while(connection_pool):
        connection = random.choice(sorted(connection_pool))
        connection_pool.remove(connection)
        k_connect(connection)

@BaseGrid.algo
def simple_prim(maze: BaseGrid) -> None:
    visited: set[Position] = set()
    active: list[Position] = []
    start_point = maze.random_point()
    active.append(start_point)
    visited.add(start_point)
    while active:
        source = random.choice(active)
        neighbors = [n for n in maze.pos_neighbors(source) if n not in visited]
        if neighbors:
            target = random.choice(neighbors)
            maze.connect(source, target)
            active.append(target)
            visited.add(target)
        else:
            active.remove(source)

@BaseGrid.algo
def true_prim(maze: BaseGrid) -> None:
    visited: set[Position] = set()
    active: list[Position] = []
    cost: dict[Position, int] = {k: random.randrange(100) for k in maze._grid.keys()}
    start_point = maze.random_point()
    active.append(start_point)
    visited.add(start_point)
    while active:
        min_source_cost = min([cost[pos] for pos in active])
        source = random.choice([pos for pos in active if cost[pos] == min_source_cost])
        neighbors = [n for n in maze.pos_neighbors(source) if n not in visited]
        if neighbors:
            min_target_cost = min([cost[pos] for pos in neighbors])
            target = random.choice([n for n in neighbors if cost[n] == min_target_cost])
            maze.connect(source, target)
            active.append(target)
            visited.add(target)
        else:
            active.remove(source)

def growing_tree(maze: BaseGrid, choice_method: Callable[[list[Position]], Position]) -> None:
    visited: set[Position] = set()
    active: list[Position] = []
    start_point = maze.random_point()
    active.append(start_point)
    visited.add(start_point)
    while active:
        source = choice_method(active)
        neighbors = [n for n in maze.pos_neighbors(source) if n not in visited]
        if neighbors:
            target = random.choice(neighbors)
            maze.connect(source, target)
            active.append(target)
            visited.add(target)
        else:
            active.remove(source)

@BaseGrid.algo
def random_tree(maze: BaseGrid) -> None:
    growing_tree( maze, lambda active: random.choice(active))

@BaseGrid.algo
def last_tree(maze: BaseGrid) -> None:
    growing_tree(maze, lambda active: active[-1])

@BaseGrid.algo
def half_tree(maze: BaseGrid) -> None:
    growing_tree(maze, lambda active: active[-1] if random.randrange(2) == 0 else random.choice(active))

@BaseGrid.algo
def first_tree(maze: BaseGrid) -> None:
    growing_tree(maze, lambda active: active[0])

@BaseGrid.algo
def median_tree(maze: BaseGrid) -> None:
    growing_tree(maze, lambda active: active[len(active) // 2])

@BaseGrid.algo
def eller(maze: BaseGrid) -> None:
    # group structure from kruskal
    # sets of connected points
    point_groups: dict[int, set[Position]] = {}
    next_group: int = 0
    # mapping back to groups
    group_for_point: dict[Position, int] = {}

    # create a new group
    def start_group(points: tuple[Position, ...]) -> None:
        nonlocal next_group
        point_groups[next_group] = set(points)
        for p in points:
            group_for_point[p] = next_group
        next_group += 1

    # connect two points if they're not in the same group,
    # creating or merging groups as necessary
    def k_connect(connection: tuple[Position, Position]) -> None:
        groups_for_connection: list[Optional[int]] = [
            group_for_point.get(p, None) for p in connection]
        if None in groups_for_connection:
            if groups_for_connection == [None, None]:
                # neither point is in a group, make a new group
                start_group(connection)
                maze.connect(*connection)
            else:
                # one point is in a group, put the other into the same
                target_group = [g for g in groups_for_connection if g is not None][0]
                maze.connect(*connection)
                for p in connection:
                    point_groups[target_group].add(p)
                    group_for_point[p] = target_group
        elif groups_for_connection[0] != groups_for_connection[1]:
            # the points are in different groups, merge them
            target_group, source_group = sorted([g for g in groups_for_connection if g is not None])
            maze.connect(*connection)
            point_groups[target_group] |= point_groups[source_group]
            for p in point_groups[source_group]:
                group_for_point[p] = target_group
            del point_groups[source_group]
        else:
            # the points are in the same group, don't connect them
            pass

    # get all possible xes
    all_xes = sorted(list({ p.coordinates[0] for p in maze._grid.keys() }))
    # go row by row
    last_x = all_xes[-1]
    for x in all_xes:
        row_points = sorted([p for p in maze._grid.keys() if p.coordinates[0] == x])
        for i in range(len(row_points)):
            # check against previous for free loop
            if row_points[i-1] in maze.pos_adjacents(row_points[i]):
                # half chance to connect if meaningful
                if x == last_x or random.randrange(2) == 1:
                    k_connect((row_points[i-1], row_points[i]))
            if row_points[i] not in group_for_point:
                start_group((row_points[i],))
        # carve "east" for each row
        row_points_set = set(row_points)
        for group_points in point_groups.values():
            east_points = [p for p in group_points & row_points_set]
            # get all connections to next row
            next_row_connections = [(p, q) for p in east_points for q in maze.pos_adjacents(p) if q.coordinates[0] > x and q in maze]
            random.shuffle(next_row_connections)
            if next_row_connections:
                # # carve west 1-N times
                # for i in range(random.randint(1,len(next_row_connections))):
                    # k_connect(next_row_connections[i])
                for i, connection in enumerate(next_row_connections):
                    if i == 0 or random.randrange(4) == 0:
                        k_connect(connection)

@BaseGrid.algo
def fractal(maze: BaseGrid) -> None:
    def fractal_step(region: set[Position]) -> None:
        if len(region) <= maze.room_size:
            # make big room
            for p in region:
                for q in maze.pos_adjacents(p):
                    if q in region:
                        maze.connect(p, q)
        elif len(region) > 1:
            division_options = maze.region_divisions(region)
            division = random.choice(division_options)
            border = [ (p, q) for p in division.regions[0]
                              for q in maze.pos_neighbors(p) if q in division.regions[1]]
            # make one border connection
            door = random.choice(border)
            maze.connect(*door)
            for subregion in division.regions:
                fractal_step(subregion)

    # first region is entire grid
    region = set(maze._grid.keys())
    fractal_step(region)


@BaseGrid.printer
def png_print(maze: BaseGrid,
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str
) -> None:
    import subprocess
    import os
    filename = '.temp.ps'
    maze_name = str(kwargs.get('maze_name', 'temp'))
    with open(filename, 'w') as f:
        f.write(maze.ps_prologue)
        f.write("/%s {" % (maze_name, ))
        f.write(maze.ps_instructions(path=path, field=field))
        f.write("\n } def\n")
        f.write("%%EndProlog\n")
    pstopng = toppath() + '/bin/pstopng'
    command = [pstopng] + maze.png_alignment + [str(maze.pixels), filename, maze_name]
    subprocess.run(command, check=True)
    os.unlink(filename)

@BaseGrid.printer
def ps_print(maze: BaseGrid,
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str
) -> None:
    print(maze.ps_prologue)
    print("%%EndProlog\n")
    print(maze.ps_alignment)
    print(maze.ps_instructions(path=path, field=field))
    print("showpage")

@BaseGrid.printer
def json_print(maze: BaseGrid,
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str
) -> None:
    print(json.dumps(maze.structured_data(path, field, **kwargs)))
