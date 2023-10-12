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
    def __init__(self,
        weave: Optional[bool] = False,
        pathcolor: Optional[list[float]] = None,
        bg: Optional[bool] = None,
        linewidth: Optional[float] = None,
        inset: Optional[float] = None,
    ) -> None:
        self._grid: dict[Position, Cell] = {}
        self.set_options(weave, pathcolor, bg, linewidth, inset)

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
    ) -> None:
        self.weave = weave
        self.pathcolor = pathcolor
        self.bg = bg
        self.linewidth = linewidth
        self.inset = inset

    def connect(self, first: Position, second: Position) -> None:
        self._grid[first].add_link(second)
        self._grid[second].add_link(first)

    def random_point(self) -> Position:
        return (random.choice(list(self._grid.keys())))

    def pos_neighbors(self, start: Position) -> list[Position]:
        raise ValueError("abstract method not overridden")

    def pos_neighbors_for_walls(self, start: Position) -> list[Position]:
        return self.pos_neighbors(start)

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
    def size_dict(self) -> dict[str, int | list[int]]:
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
        raise ValueError("not overridden")

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
        command = ['pstopng'] + self.png_alignment + ['20', filename, maze_name]
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

    algorithms['aldous_broder'] = aldous_broder
    algorithms['wilson'] = wilson
    algorithms['hunt_kill'] = hunt_kill
    algorithms['backtrack'] = backtrack

    def generate_maze(self, maze_algorithm: str) -> None:
        self.algorithms[maze_algorithm](self)

class SingleSizeGrid(BaseGrid):
    def __init__(self, size: int) -> None:
        super().__init__()

