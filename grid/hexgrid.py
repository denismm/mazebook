# grids that use hexagonal geometry

from positions import Position, Direction, add_direction
from typing import Optional

from .maze import Cell, SingleSizeGrid, ps_list

hex_directions: tuple[Direction, ...] = ( 
    (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, 0)
)

class HexBaseGrid(SingleSizeGrid):
    outputs = {}

    @property
    def neighbor_directions(self) -> tuple[tuple[Direction, ...], ...]:
        raise ValueError("neighbor_directions not overridden")

    def neighbor_directions_for_start(self, start:Position) -> tuple[Direction, ...]:
        all_nd = self.neighbor_directions
        directions_index = sum(start) % len(all_nd)
        return all_nd[directions_index]

    def pos_neighbors(self, start: Position) -> list[Position]:
        neighbor_directions = self.neighbor_directions_for_start(start)
        neighbors = [add_direction(start, dir) for dir in neighbor_directions]
        return [neighbor for neighbor in neighbors if neighbor in self]

    @property
    def ps_function(self) -> str:
        raise ValueError("ps_function not overridden")

    @property
    def ps_size(self) -> str:
        raise ValueError("ps_size not overridden")

    @property
    def png_alignment(self) -> list[str]:
        raise ValueError("png_alignment not overridden")

    @property
    def ps_alignment(self) -> str:
        raise ValueError("ps_alignment not overridden")

    def ps_instructions(self,
            path: list[Position] = [],
            field: list[set[Position]] = [],
    ) -> str:
        output: list[str] = []
        output.append("<<")
        # size
        output.append(self.ps_size)
        # cells
        output.append("/cells [")
        for k, v in self._grid.items():
            walls: list[str] = []
            neighbor_directions = self.neighbor_directions_for_start(k)
            for dir in neighbor_directions:
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
        super().__init__(radius)
        self.radius = radius
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if abs(i - j) <= radius:
                    position = (i, j)
                    self._grid[position] = Cell(position)

    @property
    def neighbor_directions(self) -> tuple[tuple[Direction, ...], ...]:
        return (hex_directions,)

    @property
    def ps_size(self) -> str:
        return f"/radius {self.radius}"

    @property
    def ps_function(self) -> str:
        return "drawhexmaze"

    @property
    def png_alignment(self) -> list[str]:
        return [str(-1 * (self.radius + 0.65)), 'd', 'd', 'd']

    @property
    def ps_alignment(self) -> str:
        return f"72 softscale 4.25 5.5 translate 4 {self.radius + 0.5} div dup scale"

class TriGrid(HexBaseGrid):
    def __init__(self, width: int) -> None:
        super().__init__(width)
        self.width = width
        max_sum = 3 * (width - 1)
        for sum in range( max_sum + 1):
            if sum % 3 != 1:
                start_i = (sum + 1) // 3
                for i in range(start_i, sum - start_i + 1):
                    j = sum - i
                    position = (i, j)
                    self._grid[position] = Cell(position)

    @property
    def neighbor_directions(self) -> tuple[tuple[Direction, ...], ...]:
        return (
            ((1, 1), (-1, 0), (0, -1),),
            (),
            ((0, 1), (-1, -1), (1, 0),)
        )

    @property
    def ps_size(self) -> str:
        return f"/width {self.width}"

    @property
    def ps_function(self) -> str:
        return "drawtrimaze"

    @property
    def png_alignment(self) -> list[str]:
        from math import sqrt
        return [str(-1.3), 'd', str((self.width - 1) * sqrt(3) + 1.3), str(self.width * 1.5 + 0.5)]

    @property
    def ps_alignment(self) -> str:
        return f"72 softscale 0.25 dup translate 8 {self.width} 3 sqrt mul div dup scale 3 sqrt half dup translate"
