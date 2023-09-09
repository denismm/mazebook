from positions import Position, Direction, cardinal_directions, add_direction
import random
from collections import defaultdict

class Cell():
    def __init__(self, location: Position) -> None:
        self.position = location
        self.links: set[Position] = set()

    def add_link(self, link: Position) -> None:
        self.links.add(link)

GridMask = set[Position]
class BaseGrid():
    algorithms = {}
    def __init__(self) -> None:
        self._grid: dict[Position, Cell] = {}

    def __contains__(self, position: Position) -> bool:
        return position in self._grid

    def __getitem__(self, position: Position) -> Cell:
        return self._grid[position]

    def __len__(self) -> int:
        return len(self._grid)

    def connect(self, first: Position, second: Position) -> None:
        self._grid[first].add_link(second)
        self._grid[second].add_link(first)

    def random_point(self) -> Position:
        return (random.choice(list(self._grid.keys())))

    def pos_neighbors(self, start: Position) -> list[Position]:
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
