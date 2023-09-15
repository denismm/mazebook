from positions import Position, cardinal_directions, add_direction
from typing import Optional
from math import pi
from functools import cache

from maze import Cell, BaseGrid, ps_list

class CircleGrid(BaseGrid):
    outputs = {}

    def __init__(self, height: int) -> None:
        super().__init__()
        self.height = height
        self.widths: list[int] = [1]
        self.ratios: list[int] = [0]
        # positions in CircleGrid are (r, theta)
        self._grid[(0,0)] = Cell((0,0))
        for r in range(1,height + 1):
            # for now, use algorithm from book
            circumference = r * pi * 2
            last_width = self.widths[r - 1]
            estimated_cell_width = circumference / last_width
            ratio = round(estimated_cell_width)
            width = last_width * ratio
            self.widths.append(width)
            self.ratios.append(ratio)
            for theta in range(width):
                position = (r, theta)
                self._grid[position] = Cell(position)

    @cache
    def pos_neighbors(self, start: Position) -> list[Position]:
        # cw and ccw around ring
        r, theta = start
        neighbors: list[Position] = []
        if r > 0:
            # left, right, down
            neighbors.append((r, (theta - 1) % self.widths[r]))
            neighbors.append((r - 1, theta // self.ratios[r]))
            neighbors.append((r, (theta + 1) % self.widths[r]))
        if r < self.height:
            next_ratio = self.ratios[r + 1]
            neighbors += [(r + 1, theta * next_ratio + x) for x in range(next_ratio)]

        neighbors = [neighbor for neighbor in neighbors if neighbor in self]
        return neighbors

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        output.append("<<")
        # width and height
        output.append(f"/height {self.height}")
        output.append(f"/widths {ps_list(self.widths)}")
        # cells
        output.append("/cells [")
        for k, v in self._grid.items():
            walls: list[str] = []
            for npos in self.pos_neighbors(v.position):
                walls.append(str(npos not in v.links).lower())
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
        output.append(">> drawcirclemaze")
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
            str(-1 * (self.height + 0.65)), 'd', 'd', 'd',
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
        print(f"4 {self.height + 0.5} div dup scale")
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
