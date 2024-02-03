#!/usr/bin/env python3
import maze.grid
import maze.rectgrid
import time

SIZE = 50
SAMPLES = 50

analysis_per_algorithm: dict[str, dict[int, float]] = {}

def line_print(data: list[str]) -> None:
    print("".join(f"{x: >8}" for x in data))

line_print([str(x) for x in range(1, 5)] + ['ms', ' algorithm'])
for algorithm in grid.rectgrid.RectGrid.algorithms.keys():
    start = time.time()
    all_data: dict[int, int] = {k: 0 for k in range(5)}
    for _ in range(SAMPLES):
        g = grid.rectgrid.RectGrid(SIZE, SIZE)
        g.generate_maze(algorithm)
        analysis = g.node_analysis()
        for k, v in analysis.items():
            all_data[k] += v
    span = (time.time() - start) * 1000 / SAMPLES
    analysis_per_algorithm[algorithm] = {
        k: 100 * v / (SAMPLES * SIZE * SIZE) for k, v in all_data.items()
    }
    output = [
        f"{analysis_per_algorithm[algorithm][k]:0.2f}" for k in range(1, 5)
    ]
    output.append(str(int(span)))
    output.append(" " + algorithm)
    line_print(output)

# print(analysis_per_algorithm)
