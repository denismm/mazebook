from collections.abc import Hashable
from functools import total_ordering
from itertools import zip_longest
from typing import Any, Optional

Coordinates = tuple[int, ...]

position_type_order_keys = {
    "link": -1,
    "int": 0,
}


@total_ordering
class Position(Hashable):
    __position_type: str
    __coordinates: Coordinates
    __gridname: Optional[str]

    def __init__(self, position_type: str, coordinates: Coordinates, gridname: Optional[str] = None) -> None:
        self.__position_type = position_type
        self.__coordinates = coordinates
        self.__gridname = gridname

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return (
            self.position_type == other.position_type
            and self.coordinates == other.coordinates
        )

    def __lt__(self, other: "Position") -> bool:
        return (
            self.gridname,
            position_type_order_keys[self.position_type],
            self.coordinates,
        ) < (
            self.gridname,
            position_type_order_keys[other.position_type],
            other.coordinates,
        )

    def __hash__(self) -> int:
        return hash(self.position_type) ^ hash(self.coordinates) ^ hash(self.gridname)

    def __repr__(self) -> str:
        class_name = type(self).__name__
        if self.__gridname:
            return f"<{class_name} {self.position_type} {self.coordinates} ({self.__gridname})>"
        else:
            return f"<{class_name} {self.position_type} {self.coordinates}>"

    @property
    def ps_rep(self) -> str:
        raise ValueError("not implemented")

    @property
    def json_rep(self) -> Any:
        raise ValueError("not implemented")

    @property
    def coordinates(self) -> Coordinates:
        return self.__coordinates

    @property
    def position_type(self) -> str:
        return self.__position_type

    @property
    def gridname(self) -> Optional[str]:
        return self.__gridname

    @property
    def flattened(self) -> tuple[Optional[str], Coordinates]:
        return (self.__gridname, self.__coordinates)

class IntPosition(Position):
    def __init__(self, coordinates: Coordinates, gridname: Optional[str] = None) -> None:
        super().__init__("int", coordinates, gridname)

    @property
    def ps_rep(self) -> str:
        return "[" + " ".join([str(x) for x in self.coordinates]) + "]"

    @property
    def json_rep(self) -> Any:
        return list(self.coordinates)


class LinkPosition(Position):
    def __init__(self, coordinates: Coordinates, gridname: Optional[str] = None) -> None:
        super().__init__("link", coordinates, gridname)

    @property
    def ps_rep(self) -> str:
        return "[" + " ".join([str(x) for x in self.coordinates]) + " /link]"

    @property
    def json_rep(self) -> Any:
        return {"type": "link", "coordinates": list(self.coordinates)}

    @classmethod
    def from_position(cls, p: Position) -> 'LinkPosition':
        return LinkPosition(p.coordinates, gridname=p.gridname)


Direction = Coordinates

cardinal_directions: tuple[Direction, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))


def add_direction(position: Position, dir: Direction) -> IntPosition:
    return IntPosition(
        tuple([p + d for p, d in zip_longest(position.coordinates, dir, fillvalue=0)]),
        gridname=position.gridname
    )


def manhattan(start: Position, end: Position) -> int:
    return sum([abs(a - b) for a, b in zip(start.coordinates, end.coordinates)])
