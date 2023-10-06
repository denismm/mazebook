Position = tuple[int, ...]
Direction = Position

cardinal_directions: tuple[Direction, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))
direction_symbols = ">v<^"

def add_direction(position: Position, dir: Direction) -> Position:
    return tuple([p + d for p, d in zip(position, dir)])

def manhattan(start: Position, end: Position) -> int:
    return sum([abs(a - b) for a, b in zip(start, end)])
