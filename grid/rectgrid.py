# grids with cells in a square layout

from positions import Position, IntPosition, Direction, cardinal_directions, add_direction, manhattan, Coordinates
from typing import Optional, Any, Callable, Sequence
import random

from .maze import BaseGrid, ps_list, Division

TEXT_CELL_WIDTH = 4
TEXT_CELL_HEIGHT = 3

WALL = '#'
SPACE = ' '
PATH = '.'

GridMask = set[Coordinates]

class RectBaseGrid(BaseGrid):
    def __init__(self, height: int, width: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        raise ValueError("not overridden")

    def pos_adjacents(self, start: Position) -> Sequence[Position]:
        neighbors: list[Position] = [
            add_direction(start, dir)
            for dir in self.neighbor_directions_for_start(start)
        ]
        neighbors.extend(super().pos_adjacents(start))
        return neighbors

    @property
    def bounding_box(self) -> tuple[float, ...]:
        return (0, 0, self.width, self.height)

    @property
    def size_dict(self) -> dict[str, int | list[int]]:
        return {"width": self.width, "height": self.height}

class RectGrid(RectBaseGrid):
    outputs = dict(BaseGrid.outputs)

    def __init__(self, height: int, width: int, mask: Optional[GridMask]=None, **kwargs: Any) -> None:
        super().__init__(height, width, **kwargs)
        for i in range(width):
            for j in range(height):
                if mask and (i, j) not in mask:
                    continue
                self._add_column((i, j))

    algorithms = dict(BaseGrid.algorithms)

    maze_type = "rectmaze"

    @classmethod
    def from_mask_txt(cls, filename: str) -> 'RectGrid':
        space_characters = {' ', '.'}
        grid_mask: GridMask= set()
        width = 0
        height = 0
        with open(filename, 'r') as f:
            lines: list[str] = [line.rstrip('\n') for line in f]
        lines.reverse()
        height = len(lines)
        for row, line in enumerate(lines):
            for column, cell in enumerate(line):
                if cell in space_characters:
                    grid_mask.add((column, row))
            width = max(width, len(line))
        return cls(height, width, mask=grid_mask)

    @classmethod
    def from_mask_png(cls, filename: str) -> 'RectGrid':
        import png
        grid_mask: GridMask= set()
        mask_image = png.Reader(filename=filename)
        (width, height, rows, info) = mask_image.asRGBA8()
        for row, line in enumerate(rows):
            for column, cell in enumerate(zip(*[iter(line)]*4)):
                (r, g, b, a) = cell
                if a == 0 or (r == 255 and g == 255 and b == 255):
                    grid_mask.add((column, height - row - 1))
        return cls(height, width, mask=grid_mask)

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        return cardinal_directions

    def region_divisions(self, region: set[Position]) -> list[Division]:
        result: list[Division] = []
        # we assert that any region is rectangular
        for coordinate in range(2):
            xs = { p.coordinates[coordinate] for p in region }
            for x in range(min(xs), max(xs)):
                left = { p for p in region if p.coordinates[coordinate] <= x }
                right = region - left
                result.append(Division(f"cut {coordinate} on {x}", (left, right)))
        return result


@RectGrid.printer       # type: ignore [arg-type]
def ascii_print(maze: RectGrid,
        path: list[Position] = [],
        field: list[set[Position]] = [],
        **kwargs: str
) -> None:
    def door_for_positions(a: Position, b: Position) -> str:
        if a in maze and b in maze and b in maze[a].links:
            if a in path and b in path:
                return PATH
            return SPACE
        else:
            return WALL
    field_for_position: dict[Position, int] = {}
    for distance, positions in enumerate(field):
        for position in positions:
            field_for_position[position] = distance
    output: list[str] = []
    output.append(WALL * ((TEXT_CELL_WIDTH + 1) * maze.width + 1))
    for j in range(maze.height):
        across_output = WALL
        down_output = WALL
        center_output = across_output
        for i in range(maze.width):
            position = IntPosition((i, j))
            if position not in maze:
                interior = WALL
            elif position in path:
                interior = PATH
            else:
                interior = SPACE
            if position in field_for_position:
                field_str = str(field_for_position[position])
                extra_space = TEXT_CELL_WIDTH - len(field_str)
                interior_output = interior * (extra_space // 2)
                interior_output += field_str
                interior_output += interior * (TEXT_CELL_WIDTH - len(interior_output))
                center_output += interior_output
            else:
                center_output += interior * TEXT_CELL_WIDTH
            across_output += interior * TEXT_CELL_WIDTH

            across_position = IntPosition((i + 1, j))
            door = door_for_positions(position, across_position)
            across_output += door
            center_output += door

            down_position = IntPosition((i, j + 1))
            door = door_for_positions(position, down_position)
            down_output += door * TEXT_CELL_WIDTH
            down_output += WALL

        for i in range(TEXT_CELL_HEIGHT):
            if i == TEXT_CELL_HEIGHT // 2:
                output.append(center_output)
            else:
                output.append(across_output)
        output.append(down_output)

    output.reverse()
    for line in output:
        print(line)


@RectGrid.algo  # type: ignore [arg-type]
def binary(maze: RectGrid) -> None:
    ne = cardinal_directions[:2]
    # nw = cardinal_directions[1:3]
    for j in range(maze.height):
        for i in range(maze.width):
            position = IntPosition((i, j))
            possible_next: list[Position] = []
            # possible_dirs = ne if j % 2 == 0 else nw
            possible_dirs = ne
            next_position: Position
            for direction in possible_dirs:
                next_position = add_direction(position, direction)
                if next_position in maze:
                    possible_next.append(next_position)
            if possible_next:
                next_position = random.choice(possible_next)
                maze.connect(position, next_position)
            
@RectGrid.algo  # type: ignore [arg-type]
def sidewinder(maze: RectGrid) -> None:
    ne = cardinal_directions[:2]
    for j in range(maze.height):
        run: list[Position] = []
        for i in range(maze.width):
            position = IntPosition((i, j))
            run.append(position)
            options: list[Direction] = []
            for direction in ne:
                next_position = add_direction(position, direction)
                if next_position in maze:
                    options.append(direction)
            if options: 
                next_direction = random.choice(options)
                if next_direction == (0, 1):
                    # close run and break north
                    break_room = random.choice(run)
                    next_position = add_direction(break_room, next_direction)
                    maze.connect(break_room, next_position)
                    run = []
                else:
                    # add next room to run
                    next_position = add_direction(position, next_direction)
                    maze.connect(position, next_position)


class ZetaGrid(RectBaseGrid):
    def __init__(self, height: int, width: int, **kwargs: Any) -> None:
        super().__init__(height, width, **kwargs)
        for i in range(width):
            for j in range(height):
                self._add_column((i, j))

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        return ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))

    maze_type = "zetamaze"

class UpsilonGrid(RectBaseGrid):
    def __init__(self, height: int, width: int, **kwargs: Any) -> None:
        super().__init__(height, width, **kwargs)
        for i in range(width):
            for j in range(height):
                self._add_column((i * 2, j * 2))
        for i in range(width - 1):
            for j in range(height - 1):
                self._add_column((1 + i * 2, 1 + j * 2))

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        if start.coordinates[0] % 2 == 0:
            return ((2, 0), (1, 1), (0, 2), (-1, 1), (-2, 0), (-1, -1), (0, -2), (1, -1))
        else:
            return ((1, 1), (-1, 1), (-1, -1), (1, -1))

    maze_type = "upsilonmaze"

    def find_link_pos(self, first: Position, second: Position) -> Position:
        # diagonal octagons have 3 common neighbors, use simpler solution
        return IntPosition(tuple([ (a + b) // 2 for a, b in zip(first.coordinates, second.coordinates)]))
