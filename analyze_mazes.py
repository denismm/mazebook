#!/usr/bin/env python3
import maze
import time

SIZE = 50
SAMPLES = 50

analysis_per_algorithm: dict[str, dict[int, float]] = {}

print("\t".join([str(x) for x in range(1, 5)] + ['ms', 'algorithm']))
for algorithm in maze.Grid.algorithms.keys():
    start = time.time()
    all_data: dict[int, int] = {k: 0 for k in range(5)}
    for _ in range(SAMPLES):
        g = maze.Grid(SIZE, SIZE)
        g.generate_maze(algorithm)
        analysis = g.node_analysis()
        for k, v in analysis.items():
            all_data[k] += v
    span = (time.time() - start) * 1000 / SAMPLES
    analysis_per_algorithm[algorithm] = {
        k: 100 * v / (SAMPLES * SIZE * SIZE) for k, v in all_data.items()
    }
    output = [
        str(analysis_per_algorithm[algorithm][k]) for k in range(1, 5)
    ]
    output.append(str(int(span)))
    output.append(algorithm)
    print("\t".join(output))

# print(analysis_per_algorithm)
