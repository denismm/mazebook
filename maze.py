from positions import Position

CELL_WIDTH = 3
CELL_HEIGHT = 2

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

    def ascii_print(self) -> None:
        output: list[str] = []
        output.append("#" * ((CELL_WIDTH + 1) * self.width + 1))
        for j in range(self.height):
            across_output = "#"
            down_output = "#"
            for i in range(self.width):
                position = (i, j)
                across_position = (i + 1, j)
                down_position = (i, j + 1)
                across_output += " " * CELL_WIDTH
                if across_position in self[position].neighbors:
                    across_output += " "
                else:
                    across_output += "#"
                if down_position in self[position].neighbors:
                    down_output += " " * CELL_WIDTH
                else:
                    down_output += "#" * CELL_WIDTH
                down_output += "#"
            for _ in range(CELL_HEIGHT):
                output.append(across_output)
            output.append(down_output)

        output.reverse()
        for line in output:
            print(line)
