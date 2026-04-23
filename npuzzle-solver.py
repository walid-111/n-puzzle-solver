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
import sys
import argparse

class PuzzleState:
    def __init__(self, board: List[List[int]], parent=None, move="", heuristic="manhattan"):
        self.board = board
        self.size = len(board)
        self.parent = parent
        self.move = move
        self.g_score = 0 if parent is None else parent.g_score + 1 # Depth
        self.empty_pos = self._find_number_in_board(0, board)
        self.goal_board = self._generate_snail_goal()
        self.heuristic = heuristic
    
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
        top, bottom = 0, self.size-1
        left, right = 0, self.size-1

        if self.size % 2 == 1:
            zero_row = self.size // 2
            zero_col = self.size // 2
        else:
            zero_row = self.size // 2
            zero_col = (self.size // 2) - 1
        
        while number < self.size * self.size:
            # Top row
            for i in range(left, right + 1):
                if top == zero_row and i == zero_col:
                    continue
                goal_board[top][i] = number
                number += 1
            top += 1
            
            # Right column
            for i in range(top, bottom + 1):
                if i == zero_row and right == zero_col:
                    continue
                goal_board[i][right] = number
                number += 1
            right -= 1
            
            # Bottom row
            for i in range(right, left - 1, -1):
                if bottom == zero_row and i == zero_col:
                    continue
                goal_board[bottom][i] = number
                number += 1
            bottom -= 1
            
            # Left column
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
        # Create mapping from numbers to their goal positions
        goal_pos = {}
        for i in range(self.size):
            for j in range(self.size):
                goal_pos[self.goal_board[i][j]] = i * self.size + j
        print(f"Goal pos: {goal_pos}")
        board_flat = [num for row in self.board for num in row if num != 0]
        print(f"Board flat: {board_flat}")
        inversions = 0
        for i in range(len(board_flat)):
            for j in range(i + 1, len(board_flat)):
                # print(f"Goal pos: {goal_pos[board_flat[i]]} and {goal_pos[board_flat[j]]}")
                if goal_pos[board_flat[i]] > goal_pos[board_flat[j]]:
                    # print("Inversion found")
                    inversions += 1
        
        if self.size % 2 == 1:
            return inversions % 2 == 0
        else:
            print("Even sized puzzle")
            blank_row_from_bottom = self.size - self.empty_pos[0] - 1
            print(f"Blank row from bottom: {blank_row_from_bottom}")
            
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
                    goal_pos = self._find_number_in_board(number, self.goal_board)
                    distance += abs(i - goal_pos[0]) + abs(j - goal_pos[1])
        return distance * self.size

    def misplaced_tiles(self) -> int:
        """Total number of misplaced tiles."""
        count = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0 and number != self.goal_board[i][j]:
                    count += 1
        return count

    def euclidean_distance(self) -> float:
        """Total Euclidean distance for current state."""
        distance = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0:
                    goal_pos = self._find_number_in_board(number, self.goal_board)
                    distance += ((i - goal_pos[0]) ** 2 + (j - goal_pos[1]) ** 2) ** 0.5
        return distance
    
    def get_heuristic_score(self) -> int:
        """Returns the heuristic score for the current state."""
        if self.heuristic == "manhattan":
            return self.manhattan_distance()
        elif self.heuristic == "misplaced":
            return self.misplaced_tiles()
        elif self.heuristic == "euclidean":
            return self.euclidean_distance()

class NPuzzleSolver:
    def __init__(self, initial_state: PuzzleState):
        self.initial_state = initial_state
        self.nodes_selected = 0 # Number of states we looked at
        self.max_nodes_stored = 0 # Maximum number of states stored in memory

    def solve(self):
        open_set = []
        closed_set = set()
        initial_h = self.initial_state.get_heuristic_score()
        initial_f = self.initial_state.g_score + initial_h
        
        """
        (initial_f,        # Primary sort key (f_score = g + h)
        initial_h,         # Secondary sort - prefer lower heuristic when f_scores equal
        -g_score,         # Tertiary sort - negative so higher g_scores (deeper paths) are preferred
        id(state),        # Unique identifier to break remaining ties
        state)            # The actual state object
        """

        heapq.heappush(open_set, (initial_f, initial_h, -self.initial_state.g_score, id(self.initial_state), self.initial_state))
        
        while open_set:
            current_f, current_h, neg_g, _, current_state = heapq.heappop(open_set)
            
            self.max_nodes_stored = max(self.max_nodes_stored, len(open_set) + len(closed_set))

            if self.nodes_selected % 10000 == 0:
                print(f"Nodes selected: {self.nodes_selected}, f_score: {current_f}, g_score: {current_state.g_score}, h_score: {current_state.get_heuristic_score()}")

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
                    new_board = [row[:] for row in current_state.board] # [row[:] for row in current_state.board] is a deep copy of the board so we don't modify the original
                    new_board[current_state.empty_pos[0]][current_state.empty_pos[1]] = new_board[new_row][new_col]
                    new_board[new_row][new_col] = 0
                    
                    neighbor_tuple = tuple(map(tuple, new_board))
                    if neighbor_tuple not in closed_set:
                        neighbor = PuzzleState(new_board, current_state, move_name, current_state.heuristic)
                        h_score = neighbor.get_heuristic_score()
                        f_score = neighbor.g_score + h_score
                        heapq.heappush(open_set, (f_score, h_score, -neighbor.g_score, id(neighbor), neighbor))
            
            self.nodes_selected += 1
        
        return None

    def print_solution(self, final_state: PuzzleState):
        """Shows solution path, and each state in it"""

        # Backtrack from final state to initial state to collect the states and moves
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
        
        return list(reversed(path))

def main(): 
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("puzzle", help="Path to puzzle file")
        parser.add_argument("--heuristic", choices=["manhattan", "misplaced", "euclidean"], 
                          default="manhattan", help="Heuristic function to use")
        args = parser.parse_args()

        board = parse_puzzle_file(args.puzzle)
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
        solution = solver.solve()
        
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
            # Remove comments and empty lines
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
                # Handle both aligned and non-aligned formats
                row = [int(num) for num in line.split()]
                if len(row) != size:
                    raise ValueError(f"Invalid row length: {len(row)}, expected {size}")
                board.append(row)
            
            if len(board) != size:
                raise ValueError(f"Invalid number of rows: {len(board)}, expected {size}")
            
            # Validate numbers (should be 0 to size²-1)
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

if __name__ == "__main__":
    main()