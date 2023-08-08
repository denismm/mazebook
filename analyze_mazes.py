#!/usr/bin/env python3
import maze

SIZE = 50
SAMPLES = 50

analysis_per_algorithm: dict[str, dict[int, float]] = {}

for algorithm in maze.Grid.algorithms.keys():
    all_data: dict[int, int] = {k: 0 for k in range(5)}
    for _ in range(SAMPLES):
        g = maze.Grid(SIZE, SIZE)
        g.generate_maze(algorithm)
        analysis = g.node_analysis()
        for k, v in analysis.items():
            all_data[k] += v
    analysis_per_algorithm[algorithm] = {k: v / SAMPLES for k, v in all_data.items()}
    print("\t".join([ str(analysis_per_algorithm[algorithm][k]) for k in range(5)]), algorithm)

# print(analysis_per_algorithm)
