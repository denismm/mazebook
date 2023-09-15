from positions import Position, Direction, add_direction
from typing import Optional

from .maze import Cell, BaseGrid, ps_list

hex_directions: tuple[Direction, ...] = ( 
    (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, 0)
)

class HexBaseGrid(BaseGrid):
    outputs = {}

    def pos_neighbors(self, start: Position) -> list[Position]:
        neighbors = [add_direction(start, dir) for dir in hex_directions]
        return [neighbor for neighbor in neighbors if neighbor in self]

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        output.append("<<")
        # radius
        output.append(f"/radius {self.radius}")
        # cells
        output.append("/cells [")
        for k, v in self._grid.items():
            walls: list[str] = []
            for dir in hex_directions:
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

    @property
    def ps_function(self) -> str:
        raise ValueError("ps_function not overridden")

    @property
    def png_alignment(self) -> list[str]:
        raise ValueError("png_alignment not overridden")

    @property
    def ps_alignment(self) -> str:
        raise ValueError("ps_alignment not overridden")

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

    outputs['ps'] = ps_print
    outputs['png'] = png_print

    def print(self,
            print_method: str,
            path: list[Position] = [],
            field: list[set[Position]] = [],
            **kwargs: str
    ) -> None:
        self.outputs[print_method](self, path, field, **kwargs)

class HexGrid(HexBaseGrid):
    def __init__(self, radius: int) -> None:
        super().__init__()
        self.radius = radius
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if abs(i - j) <= radius:
                    position = (i, j)
                    self._grid[position] = Cell(position)

    @property
    def ps_function(self) -> str:
        return "drawhexmaze"

    @property
    def png_alignment(self) -> list[str]:
        return [str(-1 * (self.radius + 0.65)), 'd', 'd', 'd']

    @property
    def ps_alignment(self) -> str:
        return f"72 softscale 4.25 5.5 translate 4 {self.radius + 0.5} div dup scale"

class TriGrid(HexGrid):
    def __init__(self, width: int) -> None:
        super().__init__()
        self.width = width
        max_sum = 3 * (width - 1)
        for i in range(2 * width - 1): # last i is 2(w - 1)
            for j in range( i // 2, max_sum - i + 1):
                if (i + j) % 3 != 1:
                    position = (i, j)
                    self._grid[position] = Cell(position)

    @property
    def ps_function(self) -> str:
        return "drawtrimaze"

    @property
    def png_alignment(self) -> list[str]:
        return [str(-0.65), 'd', str(self.width + 0.65), 'd']

    @property
    def ps_alignment(self) -> str:
        return f"72 softscale 0.25 dup translate 8 {self.width + 1} div dup scale"
