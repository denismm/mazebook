# grids with cells in a square layout

from positions import Position, Direction, cardinal_directions, add_direction
from typing import Optional

from .maze import Cell, BaseGrid, ps_list

TEXT_CELL_WIDTH = 4
TEXT_CELL_HEIGHT = 3

WALL = '#'
SPACE = ' '
PATH = '.'

GridMask = set[Position]

class RectBaseGrid(BaseGrid):
    def __init__(self, height: int, width: int) -> None:
        super().__init__()
        self.width = width
        self.height = height

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        raise ValueError("not overridden")

    def pos_neighbors(self, start: Position) -> list[Position]:
        neighbors = [add_direction(start, dir) for dir in self.neighbor_directions_for_start(start)]
        return [neighbor for neighbor in neighbors if neighbor in self]

    @property
    def png_alignment(self) -> list[str]:
        return ['-0.05', 'd', str(self.width + 0.05), str(self.height + 0.05)]

    @property
    def ps_alignment(self) -> str:
        output = "72 softscale 0.25 0.25 translate "
        if self.width / 8 > self.height / 10.5:
            output += f"8 {self.width} div dup scale"
        else:
            output += f"10.5 {self.height} div dup scale"
        return output

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        output.append("<<")
        # width and height
        output.append(f"/width {self.width}")
        output.append(f"/height {self.height}")
        # cells
        output.append("/cells [")
        for k, v in self._grid.items():
            walls: list[str] = []
            for dir in self.neighbor_directions_for_start(k):
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
        output.append(f">> {self.ps_function}")
        return "\n".join(output)

class RectGrid(RectBaseGrid):
    outputs = {}

    def __init__(self, height: int, width: int, mask: Optional[GridMask]=None) -> None:
        super().__init__(height, width)
        for i in range(width):
            for j in range(height):
                position = (i, j)
                if mask and position not in mask:
                    continue
                self._grid[position] = Cell(position)

    ps_function: str = "drawmaze"

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

    def ascii_print(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        def door_for_positions(a: Position, b: Position) -> str:
            if a in self and b in self and b in self[a].links:
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
        output.append(WALL * ((TEXT_CELL_WIDTH + 1) * self.width + 1))
        for j in range(self.height):
            across_output = WALL
            down_output = WALL
            center_output = across_output
            for i in range(self.width):
                position = (i, j)
                if position not in self:
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

                across_position = (i + 1, j)
                door = door_for_positions(position, across_position)
                across_output += door
                center_output += door

                down_position = (i, j + 1)
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

    outputs['ascii'] = ascii_print
    outputs['ps'] = RectBaseGrid.ps_print
    outputs['png'] = RectBaseGrid.png_print

    def print(self,
            print_method: str,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        self.outputs[print_method](self, path, field, **kwargs)

class ZetaGrid(RectBaseGrid):
    outputs = {}

    def __init__(self, height: int, width: int) -> None:
        super().__init__(height, width)
        for i in range(width):
            for j in range(height):
                position = (i, j)
                self._grid[position] = Cell(position)

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        return ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))

    ps_function: str = "drawzetamaze"

    outputs['ps'] = RectBaseGrid.ps_print
    outputs['png'] = RectBaseGrid.png_print

    def print(self,
            print_method: str,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        self.outputs[print_method](self, path, field, **kwargs)

class UpsilonGrid(RectBaseGrid):
    outputs = {}

    def __init__(self, height: int, width: int) -> None:
        super().__init__(height, width)
        for i in range(width):
            for j in range(height):
                position = (i * 2, j * 2)
                self._grid[position] = Cell(position)
        for i in range(width - 1):
            for j in range(height - 1):
                position = (1 + i * 2, 1 + j * 2)
                self._grid[position] = Cell(position)

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        if start[0] % 2 == 0:
            return ((2, 0), (1, 1), (0, 2), (-1, 1), (-2, 0), (-1, -1), (0, -2), (1, -1))
        else:
            return ((1, 1), (-1, 1), (-1, -1), (1, -1))

    ps_function = "drawupsilonmaze"

    outputs['ps'] = RectBaseGrid.ps_print
    outputs['png'] = RectBaseGrid.png_print

    def print(self,
            print_method: str,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        self.outputs[print_method](self, path, field, **kwargs)
