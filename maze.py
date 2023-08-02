from positions import Position

CELL_WIDTH = 4
CELL_HEIGHT = 3

WALL = '#'
SPACE = ' '
PATH = '.'

class Cell():
    def __init__(self, location: Position) -> None:
        self.neighbors: set[Position] = set()

    def add_neighbor(self, neighbor: Position) -> None:
        self.neighbors.add(neighbor)

class Grid():
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

    def connect(self, first: Position, second: Position) -> None:
        self._grid[first].add_neighbor(second)
        self._grid[second].add_neighbor(first)

    def dijkstra(self, start: Position) -> list[set[Position]]:
        seen: set[Position] = {start}
        far_points: list[set[Position]] = [{start}]
        while True:
            frontier: set[Position] = set()
            for point in far_points[-1]:
                new_points = self[point].neighbors - seen
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
            possibles = self[path[-1]].neighbors & distance_points[distance]
            path.append(possibles.pop())
        return path

    # I'm not modifying path or field so it's safe to use degenerate
    # cases as defaults
    def ascii_print(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
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
                if across_position in self[position].neighbors:
                    if position in path and across_position in path:
                        door = PATH
                    else:
                        door = SPACE
                else:
                    door = WALL
                across_output += door
                center_output += door
                if down_position in self[position].neighbors:
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
