from positions import Position, Direction, add_direction
from typing import Any, Optional

from maze import Cell, BaseGrid

hex_directions: tuple[Direction, ...] = ( 
    (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, 0)
)

class HexGrid(BaseGrid):
    outputs = {}

    def __init__(self, radius: int) -> None:
        super().__init__()
        self.radius = radius
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if abs(i - j) <= radius:
                    position = (i, j)
                    self._grid[position] = Cell(position)

    def pos_neighbors(self, start: Position) -> list[Position]:
        neighbors = [add_direction(start, dir) for dir in hex_directions]
        return [neighbor for neighbor in neighbors if neighbor in self]

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        from collections.abc import Iterable

        def ps_list(iterable: Iterable[Any]) -> str:
            return '[' + ' '.join([str(x) for x in iterable]) + ']'

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
        output.append(">> drawhexmaze")
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
            str(-1 * (self.radius + 0.65)), 'd', 'd', 'd',
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
        print("72 softscale 4.25 5.5 translate")
        print(f"4 {self.radius + 0.5} div dup scale")
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
