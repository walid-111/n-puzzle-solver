"""
Search Algorithms:

Breadth-First Search (BFS):
- Explores ALL possible moves, level by level, even bad paths

Dijkstra:
- Like BFS but considers COST of moves, explore cheapeast paths first (still explores all)

A* = Dijkstra + heuristic (to guess which moves are promising):
- Combines:
  * Cost so far (g_score: number of moves made)
  * Estimated cost to goal (h_score: manhattan+misplaced+euclidean in our case)
- Always explores the move with lowest f_score = g_score + h_score

Heuristics for n-puzzle: https://cse.iitk.ac.in/users/cs365/2009/ppt/13jan_Aman.pdf

Exponential complexity growth:
3x3: 9! = 362,880 possible states
4x4: 16! = 20,922,789,888,000 possible states (/2 because half are unsolvable)
A* performance drops significantly with larger puzzles because more possible moves at each state and longer solution paths +
heuristic becomes less accurate at predicting optimal moves
"""

from typing import List, Tuple
import heapq
import argparse
import random

class PuzzleState:
    _goal_board_cache = {}
    _goal_positions_cache = {}

    def __init__(self, board: List[List[int]], parent=None, move="", heuristic="linear_conflict"):
        self.board = board
        self.size = len(board)
        self.parent = parent
        self.move = move
        self.g_score = 0 if parent is None else parent.g_score + 1
        self.empty_pos = self._find_number_in_board(0, board)

        if self.size not in PuzzleState._goal_board_cache:
            PuzzleState._goal_board_cache[self.size] = self._generate_snail_goal()
            goal_board = PuzzleState._goal_board_cache[self.size]
            PuzzleState._goal_positions_cache[self.size] = {
                goal_board[i][j]: (i, j)
                for i in range(self.size)
                for j in range(self.size)
            }

        self.goal_board = PuzzleState._goal_board_cache[self.size]
        self.goal_positions = PuzzleState._goal_positions_cache[self.size]
        self.heuristic = heuristic
        self.h_score = self.get_heuristic_score()

    def _find_number_in_board(self, number: int, board: List[List[int]]) -> Tuple[int, int]:
        """Find position of a number in a given board"""
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == number:
                    return (i, j)
        raise ValueError(f"Number {number} not found in board")

    def _generate_snail_goal(self) -> List[List[int]]:
        """Generates the goal board in snail pattern, logic = fill + shrink"""
        goal_board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        number = 1
        top, bottom = 0, self.size - 1
        left, right = 0, self.size - 1

        if self.size % 2 == 1:
            zero_row = self.size // 2
            zero_col = self.size // 2
        else:
            zero_row = self.size // 2
            zero_col = (self.size // 2) - 1

        while number < self.size * self.size:
            for i in range(left, right + 1):
                if top == zero_row and i == zero_col:
                    continue
                goal_board[top][i] = number
                number += 1
            top += 1

            for i in range(top, bottom + 1):
                if i == zero_row and right == zero_col:
                    continue
                goal_board[i][right] = number
                number += 1
            right -= 1

            for i in range(right, left - 1, -1):
                if bottom == zero_row and i == zero_col:
                    continue
                goal_board[bottom][i] = number
                number += 1
            bottom -= 1

            for i in range(bottom, top - 1, -1):
                if i == zero_row and left == zero_col:
                    continue
                goal_board[i][left] = number
                number += 1
            left += 1

        goal_board[zero_row][zero_col] = 0
        return goal_board

    def is_goal_state(self) -> bool:
        """Check if current state matches goal state (snail pattern)"""
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != self.goal_board[i][j]:
                    return False
        return True

    def is_solvable(self) -> bool:
        """
        Solvability Rules for N×N puzzle with snail pattern goal:
        1. N odd:
            - even number of inversions to be solvable
        2. N even:
            B = blank tile's row counting from bottom
            I = inversions

            2a. N % 4 == 0:
                - B even: I must be odd
                - B odd:  I must be even
            2b. N % 4 == 2:
                - B even: I must be even
                - B odd:  I must be odd
        """
        goal_pos = {}
        for i in range(self.size):
            for j in range(self.size):
                goal_pos[self.goal_board[i][j]] = i * self.size + j

        board_flat = [num for row in self.board for num in row if num != 0]

        inversions = 0
        for i in range(len(board_flat)):
            for j in range(i + 1, len(board_flat)):
                if goal_pos[board_flat[i]] > goal_pos[board_flat[j]]:
                    inversions += 1

        if self.size % 2 == 1:
            return inversions % 2 == 0
        else:
            blank_row_from_bottom = self.size - self.empty_pos[0] - 1
            if self.size >= 6 and self.size % 4 == 2:
                if blank_row_from_bottom % 2 == 0:
                    return inversions % 2 == 0
                else:
                    return inversions % 2 == 1
            else:
                if blank_row_from_bottom % 2 == 0:
                    return inversions % 2 == 1
                else:
                    return inversions % 2 == 0

    def manhattan_distance(self) -> int:
        """Total Manhattan distance for current state"""
        distance = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0:
                    goal_row, goal_col = self.goal_positions[number]
                    distance += abs(i - goal_row) + abs(j - goal_col)
        return distance

    def misplaced_tiles(self) -> int:
        """Total number of misplaced tiles"""
        count = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0 and number != self.goal_board[i][j]:
                    count += 1
        return count

    def euclidean_distance(self) -> float:
        """Total Euclidean distance for current state"""
        distance = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0:
                    goal_row, goal_col = self.goal_positions[number]
                    distance += ((i - goal_row) ** 2 + (j - goal_col) ** 2) ** 0.5
        return distance

    def linear_conflict(self) -> int:
        """
        Manhattan distance + 2 for each pair of tiles in linear conflict.
        Two tiles are in conflict if they are in the same row/col, both need
        to stay in that row/col to reach their goal, but are in the wrong order.
        Admissible because each conflict requires at least 2 extra moves.
        """
        conflict = 0

        # Check rows
        for i in range(self.size):
            for j in range(self.size):
                tile_j = self.board[i][j]
                if tile_j == 0:
                    continue
                goal_row_j, _ = self.goal_positions[tile_j]
                if goal_row_j != i:
                    continue
                for k in range(j + 1, self.size):
                    tile_k = self.board[i][k]
                    if tile_k == 0:
                        continue
                    goal_row_k, _ = self.goal_positions[tile_k]
                    if goal_row_k != i:
                        continue
                    if self.goal_positions[tile_j][1] > self.goal_positions[tile_k][1]:
                        conflict += 2

        # Check columns
        for j in range(self.size):
            for i in range(self.size):
                tile_i = self.board[i][j]
                if tile_i == 0:
                    continue
                _, goal_col_i = self.goal_positions[tile_i]
                if goal_col_i != j:
                    continue
                for k in range(i + 1, self.size):
                    tile_k = self.board[k][j]
                    if tile_k == 0:
                        continue
                    _, goal_col_k = self.goal_positions[tile_k]
                    if goal_col_k != j:
                        continue
                    if self.goal_positions[tile_i][0] > self.goal_positions[tile_k][0]:
                        conflict += 2

        return self.manhattan_distance() + conflict

    def get_heuristic_score(self):
        """Returns the heuristic score for the current state"""
        if self.heuristic == "manhattan":
            return self.manhattan_distance()
        elif self.heuristic == "misplaced":
            return self.misplaced_tiles()
        elif self.heuristic == "euclidean":
            return self.euclidean_distance()
        elif self.heuristic == "linear_conflict":
            return self.linear_conflict()


class NPuzzleSolver:
    def __init__(self, initial_state: PuzzleState):
        self.initial_state = initial_state
        self.nodes_selected = 0
        self.max_nodes_stored = 0

    def solve(self, search="astar"):
        open_set = []
        closed_set = set()
        initial_h = self.initial_state.h_score
        
        if search == "astar":
            initial_f = self.initial_state.g_score + initial_h
        elif search == "greedy":
            initial_f = initial_h
        elif search == "uniform":
            initial_f = self.initial_state.g_score

        heapq.heappush(open_set, (initial_f, initial_h, -self.initial_state.g_score, id(self.initial_state), self.initial_state))

        while open_set:
            current_f, current_h, neg_g, _, current_state = heapq.heappop(open_set)
            self.max_nodes_stored = max(self.max_nodes_stored, len(open_set) + len(closed_set))
            if self.nodes_selected % 10000 == 0:
                print(f"Nodes selected: {self.nodes_selected}, f_score: {current_f}, g_score: {current_state.g_score}, h_score: {current_state.h_score}")
            board_tuple = tuple(map(tuple, current_state.board))
            if board_tuple in closed_set:
                continue
            if current_state.is_goal_state():
                return current_state
            closed_set.add(board_tuple)
            for move in [("UP", -1, 0), ("LEFT", 0, -1), ("RIGHT", 0, 1), ("DOWN", 1, 0)]:
                move_name, row_change, col_change = move
                new_row = current_state.empty_pos[0] + row_change
                new_col = current_state.empty_pos[1] + col_change
                if 0 <= new_row < current_state.size and 0 <= new_col < current_state.size:
                    new_board = [row[:] for row in current_state.board]
                    new_board[current_state.empty_pos[0]][current_state.empty_pos[1]] = new_board[new_row][new_col]
                    new_board[new_row][new_col] = 0
                    neighbor_tuple = tuple(map(tuple, new_board))
                    if neighbor_tuple not in closed_set:
                        neighbor = PuzzleState(new_board, current_state, move_name, current_state.heuristic)
                        h_score = neighbor.h_score
                        
                        if search == "astar":
                            f_score = neighbor.g_score + h_score
                        elif search == "greedy":
                            f_score = h_score
                        elif search == "uniform":
                            f_score = neighbor.g_score
                        
                        heapq.heappush(open_set, (f_score, h_score, -neighbor.g_score, id(neighbor), neighbor))
            self.nodes_selected += 1
        return None

    def print_solution(self, final_state: PuzzleState):
        """Shows solution path and each state in it"""
        states = []
        path = []
        current = final_state
        while current is not None:
            states.append(current)
            path.append(current.move)
            current = current.parent

        states.reverse()
        for i, state in enumerate(states):
            print(f"\nStep {i}:")
            for row in state.board:
                print(row)
            if i < len(states) - 1:
                print(f"Move: {states[i + 1].move}")

        return list(reversed(path))[1:]  # first state has no move


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("puzzle", nargs="?", help="Path to puzzle file")
        parser.add_argument("--generate", type=int, help="Generate random puzzle of given size")
        parser.add_argument("--heuristic", choices=["manhattan", "misplaced", "euclidean", "linear_conflict"],default="linear_conflict", help="Heuristic function to use")
        parser.add_argument("--search", choices=["astar", "greedy", "uniform"], default="astar", help="Search algorithm to use")
        args = parser.parse_args()

        if args.generate:
            if args.generate < 3:
                raise ValueError("Size must be >= 3")
            board = make_puzzle(args.generate, solvable=True, iterations=10000)
        elif args.puzzle:
            board = parse_puzzle_file(args.puzzle)
        else:
            raise ValueError("Usage: python3 npuzzle-solver.py puzzle.txt OR --generate N")

        initial_state = PuzzleState(board, heuristic=args.heuristic)

        print("Initial board:")
        for row in initial_state.board:
            print(row)

        print("\nGoal board (snail pattern):")
        for row in initial_state.goal_board:
            print(row)

        if not initial_state.is_solvable():
            print("\nThis puzzle is NOT SOLVABLE!")
            return
        print("\nPuzzle is solvable, attempting to solve...")

        solver = NPuzzleSolver(initial_state)
        solution = solver.solve(args.search)

        if solution:
            print(f"\nSolution found in {len(solver.print_solution(solution))} moves")
            print(f"Nodes examined: {solver.nodes_selected}")
            print(f"Max nodes in memory: {solver.max_nodes_stored}")
        else:
            print("\nNo solution found")
            print(f"Nodes examined: {solver.nodes_selected}")

    except ValueError as e:
        print(f"Error: {e}")


def parse_puzzle_file(filename: str) -> List[List[int]]:
    try:
        with open(filename, 'r') as file:
            lines = []
            for line in file:
                parts = line.split('#')
                line_without_comment = parts[0]
                line = line_without_comment.strip()
                if line:
                    lines.append(line)

            if not lines:
                raise ValueError("Empty file")

            size = int(lines[0])
            if size < 2:
                raise ValueError(f"Invalid puzzle size: {size}")

            board = []
            for line in lines[1:]:
                row = [int(num) for num in line.split()]
                if len(row) != size:
                    raise ValueError(f"Invalid row length: {len(row)}, expected {size}")
                board.append(row)

            if len(board) != size:
                raise ValueError(f"Invalid number of rows: {len(board)}, expected {size}")

            found_numbers = []
            for row in board:
                for number in row:
                    found_numbers.append(number)
                    if number < 0 or number >= (size * size):
                        raise ValueError(f"Invalid number found: {number}. Numbers should be between 0 and {size * size - 1}")

            found_numbers.sort()
            required_numbers = list(range(size * size))
            if found_numbers != required_numbers:
                raise ValueError(f"Wrong numbers in puzzle! Should have numbers: {required_numbers}, Found numbers: {found_numbers}")
            return board

    except FileNotFoundError:
        raise ValueError(f"File not found: {filename}")
    except ValueError as e:
        raise ValueError(f"Invalid puzzle file: {str(e)}")


# --- Generator (given by subject) ---

def make_goal(s):
    ts = s * s
    puzzle = [-1 for i in range(ts)]
    cur = 1
    x = 0; ix = 1
    y = 0; iy = 0
    while True:
        puzzle[x + y * s] = cur
        if cur == 0:
            break
        cur += 1
        if x + ix == s or x + ix < 0 or (ix != 0 and puzzle[x + ix + y * s] != -1):
            iy = ix; ix = 0
        elif y + iy == s or y + iy < 0 or (iy != 0 and puzzle[x + (y + iy) * s] != -1):
            ix = -iy; iy = 0
        x += ix; y += iy
        if cur == s * s:
            cur = 0
    return puzzle

def make_puzzle(s, solvable, iterations):
    def swap_empty(p):
        idx = p.index(0)
        poss = []
        if idx % s > 0: poss.append(idx - 1)
        if idx % s < s - 1: poss.append(idx + 1)
        if idx // s > 0: poss.append(idx - s)
        if idx // s < s - 1: poss.append(idx + s)
        swi = random.choice(poss)
        p[idx] = p[swi]; p[swi] = 0

    p = make_goal(s)
    for i in range(iterations):
        swap_empty(p)
    if not solvable:
        if p[0] == 0 or p[1] == 0:
            p[-1], p[-2] = p[-2], p[-1]
        else:
            p[0], p[1] = p[1], p[0]
    return [[p[y * s + x] for x in range(s)] for y in range(s)]


if __name__ == "__main__":
    main()