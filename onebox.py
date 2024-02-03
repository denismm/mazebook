#!/usr/bin/env python3
import random
from maze.rectgrid import RectGrid
from maze.multigrid import MultiGrid, GridSpec, EdgeSpec
from positions import IntPosition

def draw_square(name: str, edges: tuple[EdgeSpec, ...]) -> None:
    random.seed(97)
    maze_size = 8
    subgrids = {
        "A": GridSpec(
            RectGrid,
            (maze_size, maze_size),
            edges,
            (0, 0),
        ),
    }

    multigrid = MultiGrid(subgrids, weave=True)

    multigrid.generate_maze("backtrack")

    field = multigrid.dijkstra(IntPosition((0, 0), "A"))

    # multigrid.print("ps", field=field)
    multigrid.print("png", field=field, maze_name=name)

draw_square('torus', (
        EdgeSpec("A", 2, True),
        EdgeSpec("A", 3, True),
        EdgeSpec("A", 0, True),
        EdgeSpec("A", 1, True),
    ))

draw_square('klein', (
        EdgeSpec("A", 2, True),
        EdgeSpec("A", 3, False),
        EdgeSpec("A", 0, True),
        EdgeSpec("A", 1, False),
    ))

draw_square('projective_plane', (
        EdgeSpec("A", 2, False),
        EdgeSpec("A", 3, False),
        EdgeSpec("A", 0, False),
        EdgeSpec("A", 1, False),
    ))

draw_square('cylinder', (
        None,
        EdgeSpec("A", 3, True),
        None,
        EdgeSpec("A", 1, True),
    ))

draw_square('moebius', (
        None,
        EdgeSpec("A", 3, False),
        None,
        EdgeSpec("A", 1, False),
    ))
