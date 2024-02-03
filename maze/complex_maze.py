from .grid import BaseGrid, SingleSizeGrid
from .multigrid import MultiGrid, GridSpec, EdgeSpec
from .rectgrid import RectBaseGrid, RectGrid, ZetaGrid, UpsilonGrid
from .circlegrid import SemiCircleGrid, PolygonGrid
from .hexgrid import HexGrid, TriGrid
from typing_extensions import Protocol

class ComplexMaze(Protocol):
    def __call__(self,
        size: int,
        **kwargs: str) -> MultiGrid: ...

complex_mazes: dict[str, ComplexMaze] = {}

# dict-adding decorator
def complex(cmf: ComplexMaze) -> ComplexMaze:
    complex_mazes[cmf.__name__] = cmf   # type: ignore [attr-defined] # fixed in next mypy version
    return cmf

def complex_grid(mazetype: str, size: int, **kwargs: str) -> MultiGrid:
    return complex_mazes[mazetype](size, **kwargs)

@complex
def slender_star(size: int, **kwargs: str) -> MultiGrid:
    center_cell: bool = kwargs.pop('center_cell', False)        # type: ignore [assignment]
    polygon_args = (size, 5)
    polygon_kwargs = {"firstring": 10, "center_cell": center_cell}
    point_kwargs = {'slices': 1, "center_cell": center_cell}
    point_size = None

    drop_grid = PolygonGrid(*polygon_args, **polygon_kwargs)    # type: ignore [arg-type]
    triangle_width = drop_grid.widths[-1] // 5
    for i in range(size, size * 3):
        drop_grid = PolygonGrid(i, 10, **point_kwargs)   # type: ignore [arg-type]
        outer_width = drop_grid.widths[-1] // 10
        if outer_width == triangle_width:
            point_size = i
        if outer_width > triangle_width:
            if point_size is None:
                raise ValueError("no matching size")
            break
    assert point_size is not None
    point_args = (point_size, 10)

    subgrids = {
        "C": GridSpec( PolygonGrid, polygon_args,
            (
                EdgeSpec("0", 0, True),
                EdgeSpec("1", 0, True),
                EdgeSpec("2", 0, True),
                EdgeSpec("3", 0, True),
                EdgeSpec("4", 0, True),
            ),
            (0, 0),
            rotation=54,
            kwargs=polygon_kwargs
        ),
        "0": GridSpec( PolygonGrid, point_args,
            (EdgeSpec("C", 0, True, align=True),),
            kwargs=point_kwargs,
        ),
        "1": GridSpec( PolygonGrid, point_args,
            (EdgeSpec("C", 1, True, align=True),),
            kwargs=point_kwargs,
        ),
        "2": GridSpec( PolygonGrid, point_args,
            (EdgeSpec("C", 2, True, align=True),),
            kwargs=point_kwargs,
        ),
        "3": GridSpec( PolygonGrid, point_args,
            (EdgeSpec("C", 3, True, align=True),),
            kwargs=point_kwargs,
        ),
        "4": GridSpec( PolygonGrid, point_args,
            (EdgeSpec("C", 4, True, align=True),),
            kwargs=point_kwargs,
        ),
    }
    return MultiGrid(subgrids, **kwargs)

@complex
def fat_star(size: int, **kwargs: str) -> MultiGrid:
    point_kwargs = {'slices': 1}
    subgrids = {
        "C": GridSpec(
            PolygonGrid,
            (size, 5),
            (
                EdgeSpec("0", 0, True),
                EdgeSpec("1", 0, True),
                EdgeSpec("2", 0, True),
                EdgeSpec("3", 0, True),
                EdgeSpec("4", 0, True),
            ),
            (0, 0),
            rotation=54,
        ),
        "0": GridSpec(
            PolygonGrid,
            (size, 5),
            (EdgeSpec("C", 0, True, align=True),),
            kwargs = point_kwargs,
        ),
        "1": GridSpec(
            PolygonGrid,
            (size, 5),
            (EdgeSpec("C", 1, True, align=True),),
            kwargs = point_kwargs,
        ),
        "2": GridSpec(
            PolygonGrid,
            (size, 5),
            (EdgeSpec("C", 2, True, align=True),),
            kwargs = point_kwargs,
        ),
        "3": GridSpec(
            PolygonGrid,
            (size, 5),
            (EdgeSpec("C", 3, True, align=True),),
            kwargs = point_kwargs,
        ),
        "4": GridSpec(
            PolygonGrid,
            (size, 5),
            (EdgeSpec("C", 4, True, align=True),),
            kwargs = point_kwargs,
        ),
    }

    return MultiGrid(subgrids, **kwargs)

@complex
def cube(size: int, **kwargs: str) -> MultiGrid:
    subgrids = {
        "F": GridSpec(
            RectGrid,
            (size, size),
            (
                EdgeSpec("R", 2, True),
                EdgeSpec("U", 3, True),
                EdgeSpec("L", 0, True),
                EdgeSpec("D", 1, True),
            ),
        ),
        "B": GridSpec(
            RectGrid,
            (size, size),
            (
                EdgeSpec("R", 0, True),
                EdgeSpec("D", 3, True, align=True),
                EdgeSpec("L", 2, True),
                EdgeSpec("U", 1, True),
            ),
        ),
        "L": GridSpec(
            RectGrid,
            (size, size),
            (
                EdgeSpec("F", 2, True, align=True),
                EdgeSpec("U", 2, True),
                EdgeSpec("B", 2, True),
                EdgeSpec("D", 2, True),
            ),
        ),
        "R": GridSpec(
            RectGrid,
            (size, size),
            (
                EdgeSpec("B", 0, True),
                EdgeSpec("U", 0, True),
                EdgeSpec("F", 0, True, align=True),
                EdgeSpec("D", 0, True),
            ),
        ),
        "U": GridSpec(
            RectGrid,
            (size, size),
            (
                EdgeSpec("R", 1, True),
                EdgeSpec("B", 3, True),
                EdgeSpec("L", 1, True),
                EdgeSpec("F", 1, True, align=True),
            ),
        ),
        "D": GridSpec(
            RectGrid,
            (size, size),
            (
                EdgeSpec("R", 3, True),
                EdgeSpec("F", 3, True, align=True),
                EdgeSpec("L", 3, True),
                EdgeSpec("B", 1, True),
            ),
        ),
    }

    return MultiGrid(subgrids, **kwargs)

@complex
def heart(size: int, **kwargs: str) -> MultiGrid:
    subgrids = {
        "C": GridSpec(
            RectGrid,
            (size, size),
            (
                EdgeSpec("L", 0, True),
                EdgeSpec("R", 0, True),
                None,
                None,
            ),
            rotation=45,
        ),
        "L": GridSpec(
            SemiCircleGrid,
            (size,),
            (
                EdgeSpec("C", 0, True, align=True),
            ),
        ),
        "R": GridSpec(
            SemiCircleGrid,
            (size,),
            (
                EdgeSpec("C", 1, True, align=True),
            ),
        ),
    }
    return MultiGrid(subgrids, **kwargs)
