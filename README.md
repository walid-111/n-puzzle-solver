# n-puzzle solver

Solves the n-puzzle (8-puzzle, 15-puzzle, or any size) using A*. The goal isn't the classic 1, 2, 3... order but a snail pattern, with 0 as the empty tile:

```
1 2 3
8 0 4
7 6 5
```

Before solving, it checks whether the puzzle is solvable at all.

## Usage

Only needs Python 3.

```
python3 npuzzle-solver.py puzzles/3-solvable.txt
python3 npuzzle-solver.py --generate 4
```

You can choose the heuristic with `--heuristic` (linear_conflict by default, or manhattan, misplaced, euclidean) and the search with `--search` (astar by default, or greedy, uniform).

A puzzle file starts with the size, followed by the rows. Lines starting with `#` are comments. There are a few examples in `puzzles/`.

```
3
0 2 3
4 5 7
8 6 1
```

The output shows every step, the number of moves, how many nodes were examined, and the max number of nodes in memory.

## How it works

A* picks the state with the lowest moves made + heuristic, so it always finds the shortest solution. Greedy only looks at the heuristic: it's much faster, but the solution is longer. Uniform only looks at the moves made, so it becomes very slow quickly.

Linear conflict is the best heuristic here. It's the Manhattan distance plus 2 for each pair of tiles that are in their goal row or column but in the wrong order, which cuts down a lot of nodes.

3x3 puzzles are instant. 4x4 depends on the puzzle, from instant to a few minutes. For anything bigger, greedy is the way to go.

`npuzzle-gen.py` is a puzzle generator that came with the project, I didn't write it.
