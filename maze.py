from positions import Position, Direction, cardinal_directions, add_direction
from typing import Any
import random
from collections import defaultdict

CELL_WIDTH = 4
CELL_HEIGHT = 3

WALL = '#'
SPACE = ' '
PATH = '.'

class Cell():
    def __init__(self, location: Position) -> None:
        self.position = location
        self.links: set[Position] = set()

    def add_link(self, link: Position) -> None:
        self.links.add(link)

class Grid():
    algorithms = {}
    outputs = {}

    def __init__(self, height: int, width: int) -> None:
        self._grid: dict[Position, Cell] = {}
        self.width = width
        self.height = height
        for i in range(width):
            for j in range(height):
                position = (i, j)
                self._grid[position] = Cell(position)

    def __contains__(self, position: Position) -> bool:
        return position in self._grid

    def __getitem__(self, position: Position) -> Cell:
        return self._grid[position]

    def __len__(self) -> int:
        return self.height * self.width

    def connect(self, first: Position, second: Position) -> None:
        self._grid[first].add_link(second)
        self._grid[second].add_link(first)

    def random_point(self) -> Position:
        return (random.randrange(self.width), random.randrange(self.height))

    def pos_neighbors(self, start: Position) -> list[Position]:
        neighbors = [add_direction(start, dir) for dir in cardinal_directions]
        return [neighbor for neighbor in neighbors if neighbor in self]

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
        # start at 0, 0
        start: Position = (0, 0)
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
        # how many positions have 0, 1, 2, 3, 4 connections
        nodes_for_links: dict[int, int] = defaultdict(lambda: 0)
        for cell in self._grid.values():
            nodes_for_links[len(cell.links)] += 1
        return dict(nodes_for_links)

    # I'm not modifying path or field so it's safe to use degenerate
    # cases as defaults
    def ascii_print(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        field_for_position: dict[Position, int] = {}
        for i, positions in enumerate(field):
            for position in positions:
                field_for_position[position] = i
        output: list[str] = []
        output.append(WALL * ((CELL_WIDTH + 1) * self.width + 1))
        for j in range(self.height):
            across_output = WALL
            down_output = WALL
            center_output = across_output
            for i in range(self.width):
                position = (i, j)
                across_position = (i + 1, j)
                down_position = (i, j + 1)
                if position in path:
                    interior = PATH
                else:
                    interior = SPACE
                if position in field_for_position:
                    field_str = str(field_for_position[position])
                    extra_space = CELL_WIDTH - len(field_str)
                    interior_output = interior * (extra_space // 2)
                    interior_output += field_str
                    interior_output += interior * (CELL_WIDTH - len(interior_output))
                    center_output += interior_output
                else:
                    center_output += interior * CELL_WIDTH
                across_output += interior * CELL_WIDTH
                if across_position in self[position].links:
                    if position in path and across_position in path:
                        door = PATH
                    else:
                        door = SPACE
                else:
                    door = WALL
                across_output += door
                center_output += door
                if down_position in self[position].links:
                    if position in path and down_position in path:
                        door = PATH
                    else:
                        door = SPACE
                else:
                    door = WALL
                down_output += door * CELL_WIDTH
                down_output += WALL
            for i in range(CELL_HEIGHT):
                if i == CELL_HEIGHT // 2:
                    output.append(center_output)
                else:
                    output.append(across_output)
            output.append(down_output)

        output.reverse()
        for line in output:
            print(line)

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        from collections.abc import Iterable

        def ps_list(iterable: Iterable[Any]) -> str:
            return '[' + ' '.join([str(x) for x in iterable]) + ']'

        output: list[str] = []
        output.append("<<")
        # width and height
        output.append(f"/width {self.width}")
        output.append(f"/height {self.height}")
        # cells
        output.append("/cells [")
        for k, v in self._grid.items():
            walls: list[str] = []
            for dir in cardinal_directions:
                walls.append(str(add_direction(k, dir) not in v.links).lower())
            output.append(f"[ {ps_list(k)} {ps_list(walls)} ]")
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
        output.append(">> drawmaze")
        return "\n".join(output)

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
        command = ['pstopng',
            '-0.05', 'd', str(self.width + 0.05), str(self.height + 0.05),
            '20', filename, maze_name]
        subprocess.run(command, check=True)
        os.unlink(filename)

    def ps_print(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        print("%!\n(draw_maze.ps) run")
        print("%%EndProlog\n")
        print("72 softscale 0.25 0.25 translate")
        if self.width / 8 > self.height / 10.5:
            print(f"8 {self.width} div dup scale")
        else:
            print(f"10.5 {self.height} div dup scale")
        print(self.ps_instructions(path=path, field=field))
        print("showpage")

    def binary(self) -> None:
        ne = cardinal_directions[:2]
        # nw = cardinal_directions[1:3]
        for j in range(self.height):
            for i in range(self.width):
                position = (i, j)
                possible_next: list[Position] = []
                # possible_dirs = ne if j % 2 == 0 else nw
                possible_dirs = ne
                for direction in possible_dirs:
                    next_position = add_direction(position, direction)
                    if next_position in self:
                        possible_next.append(next_position)
                if possible_next:
                    next_position = random.choice(possible_next)
                    self.connect(position, next_position)

    def sidewinder(self) -> None:
        ne = cardinal_directions[:2]
        for j in range(self.height):
            run: list[Position] = []
            for i in range(self.width):
                position = (i, j)
                run.append(position)
                options: list[Direction] = []
                for direction in ne:
                    next_position = add_direction(position, direction)
                    if next_position in self:
                        options.append(direction)
                if options:
                    next_direction = random.choice(options)
                    if next_direction == (0, 1):
                        # close run and break north
                        break_room = random.choice(run)
                        next_position = add_direction(break_room, next_direction)
                        self.connect(break_room, next_position)
                        run = []
                    else:
                        # add next room to run
                        next_position = add_direction(position, next_direction)
                        self.connect(position, next_position)

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

    algorithms['binary'] = binary
    algorithms['sidewinder'] = sidewinder
    algorithms['aldous_broder'] = aldous_broder
    algorithms['wilson'] = wilson
    algorithms['hunt_kill'] = hunt_kill
    algorithms['backtrack'] = backtrack

    def generate_maze(self, maze_algorithm: str) -> None:
        self.algorithms[maze_algorithm](self)

    outputs['ascii'] = ascii_print
    outputs['ps'] = ps_print
    outputs['png'] = png_print

    def print(self,
            print_method: str,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        self.outputs[print_method](self, path, field, **kwargs)

def make_binary(maze_height: int, maze_width: int) -> Grid:
    grid = Grid(maze_height, maze_width)
    grid.binary()
    return grid

def make_sidewinder(maze_height: int, maze_width: int) -> Grid:
    grid = Grid(maze_height, maze_width)
    grid.sidewinder()
    return grid

def make_aldous_broder(maze_height: int, maze_width: int) -> Grid:
    grid = Grid(maze_height, maze_width)
    grid.aldous_broder()
    # print(f"A-B done in {steps} steps")
    return grid

def make_wilson(maze_height: int, maze_width: int) -> Grid:
    grid = Grid(maze_height, maze_width)
    grid.generate_maze('wilson')
    #  print(f"Wilson done in {steps} steps")
    return grid
