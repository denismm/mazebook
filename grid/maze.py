from positions import Position, Direction, cardinal_directions, add_direction
import random
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Optional
import json

class Cell():
    def __init__(self, location: Position) -> None:
        self.position = location
        self.links: set[Position] = set()

    def add_link(self, link: Position) -> None:
        self.links.add(link)

    @property
    def flat_links(self) -> set[Position]:
        # for weaving it can be useful to ignore the 3rd coord of a link
        return set([p[:2] for p in self.links])

# convenience for ps printing
def ps_list(iterable: Iterable[Any]) -> str:
    return '[' + ' '.join([str(x) for x in iterable]) + ']'

GridMask = set[Position]
class BaseGrid():
    def __init__(self, **kwargs: Any) -> None:
        self._grid: dict[Position, Cell] = {}
        self.set_options(**kwargs)

    algorithms = {}
    outputs = {}

    def __contains__(self, position: Position) -> bool:
        return position in self._grid

    def __getitem__(self, position: Position) -> Cell:
        return self._grid[position]

    def __len__(self) -> int:
        return len(self._grid)

    def set_options(self,
        weave: Optional[bool] = False,
        pathcolor: Optional[list[float]] = None,
        bg: Optional[bool] = None,
        linewidth: Optional[float] = None,
        inset: Optional[float] = None,
        pixels: Optional[float] = None,
    ) -> None:
        if pixels is None:
            pixels = 20.0
        self.weave = weave
        self.pathcolor = pathcolor
        self.bg = bg
        self.linewidth = linewidth
        self.inset = inset
        self.pixels = pixels

    def connect(self, first: Position, second: Position) -> None:
        # what if there's a distance between the two cells?
        if second[:2] in self.pos_adjacents(first):
            self._grid[first].add_link(second)
            self._grid[second].add_link(first)
            return
        # link square is between both, add third dimension
        link_pos = self.find_link_pos(first, second) + (1, )
        link_cell = Cell(link_pos)
        self._grid[link_pos] = link_cell
        self.connect(first, link_pos)
        self.connect(second, link_pos)

    def find_link_pos(self, first: Position, second: Position) -> Position:
        # general solution
        first_neighbors = self.pos_adjacents(first)
        second_neighbors = self.pos_adjacents(second)
        intersection_positions = set(first_neighbors) & set(second_neighbors)
        if len(intersection_positions) == 0:
            raise ValueError(f"no common cell between {first} and {second}")
        if len(intersection_positions) > 1:
            raise ValueError(f"too many common cells between {first} and {second} ({first_neighbors}, {second_neighbors}, {intersection_positions}")
        return intersection_positions.pop()

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
                if not ({start, other_side} & target_cell.flat_links):
                    # tunnel ok!
                    neighbors.append(other_side)
        return neighbors

    def pos_adjacents(self, start: Position) -> list[Position]:
        # must return adjacent cells in order, including those not in grid
        raise ValueError("abstract method not overridden")

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
        first_point = self.dijkstra(start)[-1].pop()
        # get farthest point from there
        distance_points = self.dijkstra(first_point)
        second_point = distance_points[-1].pop()
        # get path
        path: list[Position] = [second_point]
        distance = len(distance_points) - 1
        while distance > 0:
            distance -= 1
            possibles = self[path[-1]].links & distance_points[distance]
            path.append(possibles.pop())
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
    def size_dict(self) -> dict[str, int | bool | list[int]]:
        raise ValueError("not overridden")

    # ps command to align ps output
    @property
    def ps_alignment(self) -> str:
        raise ValueError("not overridden")

    # command subset for pstopng
    @property
    def png_alignment(self) -> list[str]:
        raise ValueError("not overridden")

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        output.append("<<")
        # size
        for size_key, size_value in self.size_dict.items():
            if isinstance(size_value, list):
                output.append(f"/{size_key} {ps_list(size_value)}")
            elif isinstance(size_value, bool):
                output.append(f"/{size_key} {str(size_value).lower()}")
            elif isinstance(size_value, int):
                output.append(f"/{size_key} {size_value}")
        # make field lookup
        field_for_position: dict[Position, int] = {}
        if field:
            for i, frontier in enumerate(field):
                for position in frontier:
                    field_for_position[position] = i
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
        for k in sorted(self._grid.keys(), key=lambda p: -(len(p))):
            v = self._grid[k]
            walls = self.walls_for_cell(v)
            walls_text = ps_list([str(w).lower() for w in walls])
            field_text = str(field_for_position.get(k, 0))
            links_text = ps_list(v.links)
            output.append(ps_list([ ps_list(k), walls_text, field_text ]) + f" % {links_text}")
        output.append("]")
        if path:
            output.append("/path ")
            output.append(ps_list([
                ps_list(position) for position in path
            ]))
        if field:
            output.append("/field ")
            output.append(ps_list([
                ps_list([
                    ps_list(position) for position in frontier
                ]) for frontier in field
            ]))
        output.append(f">> draw{self.maze_type}")
        return "\n".join(output)

    def walls_for_cell(self, cell: Cell) -> list[bool]:
        return [npos not in cell.flat_links for npos in self.pos_adjacents(cell.position)]

    def png_print(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        import subprocess
        import os
        filename = '.temp.ps'
        maze_name = str(kwargs.get('maze_name', 'temp'))
        with open(filename, 'w') as f:
            f.write("%!\n(draw_maze.ps) run\n")
            f.write("/%s {" % (maze_name, ))
            f.write(self.ps_instructions(path=path, field=field))
            f.write("\n } def\n")
            f.write("%%EndProlog\n")
        command = ['pstopng'] + self.png_alignment + [str(self.pixels), filename, maze_name]
        subprocess.run(command, check=True)
        os.unlink(filename)

    def ps_print(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        print("%!\n(draw_maze.ps) run")
        print("%%EndProlog\n")
        print(self.ps_alignment)
        print(self.ps_instructions(path=path, field=field))
        print("showpage")

    def json_print(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        output_data: dict[str, Any] = {}
        # size
        output_data.update(self.size_dict)
        if self.weave:
            output_data['weave'] = True
        output_cells: list[dict[str, Position | list[Position]]] = []
        for k, v in self._grid.items():
            cell_info: dict[str, Position| list[Position]] = {"position": k, "links": list(v.links)}
            output_cells.append(cell_info)
        output_data['cells'] = output_cells
        if path:
            output_data['path'] = path
        if field:
            output_data['field'] = [list(x) for x in field]
        output_data['maze_type'] = self.maze_type
        print(json.dumps(output_data))

    outputs['ps'] = ps_print
    outputs['png'] = png_print
    outputs['json'] = json_print

    def print(self,
        print_method: str,
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str
) -> None:
        self.outputs[print_method](self, path, field, **kwargs)

    def aldous_broder(self) -> None:
        current: Position = self.random_point()
        visited: set[Position] = {current}
        steps = 0
        while len(visited) < len(self):
            steps += 1
            next: Position = random.choice(self.pos_neighbors(current))
            if next not in visited:
                self.connect(current, next)
                visited.add(next)
            current = next

    def wilson(self) -> None:
        start: Position = self.random_point()
        unvisited: set[Position] = set(self._grid.keys())
        visited: set[Position] = {start}
        unvisited -= visited
        steps: int = 0
        while len(unvisited):
            current: Position = random.choice(list(unvisited))
            path: list[Position] = [current]
            steps += 1
            while path[-1] not in visited:
                steps += 1
                next: Position = random.choice(self.pos_neighbors(current))
                if next in path:
                    # chop out loop
                    path = path[:(path.index(next))]
                path.append(next)
                current = next
            # connect path
            for i in range(len(path) - 1):
                current = path[i]
                next = path[i + 1]
                self.connect(current, next)
                visited.add(current)
            unvisited -= visited

    def hunt_kill(self) -> None:
        current: Position = self.random_point()
        visited: set[Position] = {current}
        # break when we fill the grid
        while True:
            # break when we paint ourselves into a corner
            while True:
                next_options = set(self.pos_neighbors(current)) - visited
                if not next_options:
                    break
                next: Position = random.choice(list(next_options))
                self.connect(current, next)
                visited.add(next)
                current = next
            # choose a new start if possible
            if len(visited) == len(self):
                return
            for start_option in sorted(self._grid.keys()):
                if start_option not in visited:
                    connection_options = set(self.pos_neighbors(start_option)) & visited
                    if connection_options:
                        connection: Position = random.choice(list(connection_options))
                        self.connect(connection, start_option)
                        current = start_option
                        visited.add(current)
                        break

    def backtrack(self) -> None:
        stack: list[Position] = [self.random_point()]
        visited: set[Position] = {stack[0]}
        while stack:
            next_options = set(self.pos_neighbors(stack[-1])) - visited
            if next_options:
                next: Position = random.choice(list(next_options))
                self.connect(stack[-1], next)
                stack.append(next)
                visited.add(next)
            else:
                stack.pop()

    def kruskal(self) -> None:
        # set of possible connections
        connection_pool: set[tuple[Position, Position]] = set()
        for location in self._grid.keys():
            for neighbor in self.pos_neighbors(location):
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
                    self.connect(*connection)
                    for p in connection:
                        group_for_point[p] = next_group
                    next_group += 1
                else:
                    # one point is in a group, put the other into the same
                    target_group = [g for g in groups_for_connection if g is not None][0]
                    self.connect(*connection)
                    for p in connection:
                        point_groups[target_group].add(p)
                        group_for_point[p] = target_group
            elif groups_for_connection[0] != groups_for_connection[1]:
                # the points are in different groups, merge them
                target_group, source_group = sorted([g for g in groups_for_connection if g is not None])
                self.connect(*connection)
                point_groups[target_group] |= point_groups[source_group]
                for p in point_groups[source_group]:
                    group_for_point[p] = target_group
                del point_groups[source_group]
            else:
                # the points are in the same group, don't connect them
                pass

        # add some weaves - how many? for now, as many as possible
        if self.weave:
            weaveable_points: set[Position] = set(self._grid.keys())
            while weaveable_points:
                weave_pos = random.choice(list(weaveable_points))
                weaveable_points.remove(weave_pos)
                if weave_pos in group_for_point:
                    continue
                neighbors = self.pos_adjacents(weave_pos)
                if len(neighbors) != 4:
                    continue
                neighborset = set(neighbors)
                if neighborset & set(group_for_point.keys()):
                    continue
                if not neighborset <= set(self._grid.keys()):
                    continue
                weaveable_points -= neighborset
                link_pos: Position = weave_pos + (1,)
                link_cell = Cell(link_pos)
                self._grid[link_pos] = link_cell
                top_mod = random.randint(0, 1)

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
            connection = random.choice(list(connection_pool))
            connection_pool.remove(connection)
            k_connect(connection)

    algorithms['aldous_broder'] = aldous_broder
    algorithms['wilson'] = wilson
    algorithms['hunt_kill'] = hunt_kill
    algorithms['backtrack'] = backtrack
    algorithms['kruskal'] = kruskal

    def generate_maze(self, maze_algorithm: str) -> None:
        self.algorithms[maze_algorithm](self)

class SingleSizeGrid(BaseGrid):
    def __init__(self, size: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)

