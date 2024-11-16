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
"""

from typing import List, Tuple
import heapq

class PuzzleState:
    def __init__(self, board: List[List[int]], parent=None, move=""):
        self.board = board
        self.size = len(board)
        self.parent = parent
        self.move = move
        self.g_score = 0 if parent is None else parent.g_score + 1
        self.empty_pos = self._find_number_in_board(0, board)
        self.goal_board = self._generate_snail_goal()
    
    def _find_number_in_board(self, number: int, board: List[List[int]]) -> Tuple[int, int]:
        """Find position of a number in a given board"""
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == number:
                    return (i, j)
        raise ValueError(f"Number {number} not found in board")

    def _generate_snail_goal(self) -> List[List[int]]:
        """Generates the goal board in snail pattern."""
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

    def _generate_linear_goal(self) -> List[List[int]]:
        """Create linear pattern goal state"""
        numbers = list(range(1, self.size * self.size))
        numbers.append(0)
        goal = []
        for i in range(0, len(numbers), self.size):
            goal.append(numbers[i:i + self.size])
        return goal

    def is_goal_state(self) -> bool:
        """Check if current state matches goal state (snail pattern)"""
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != self.goal_board[i][j]:
                    return False
        return True

    def _transform_to_linear(self, board: List[List[int]]) -> List[List[int]]:
        """Transform a board to equivalent linear pattern positions"""
        snail_to_linear = {}
        linear_goal = self._generate_linear_goal()
        linear_flat = []
        for row in linear_goal:
            linear_flat.extend(row)
        
        for i in range(len(self.goal_board)):
            for j in range(len(self.goal_board[i])):
                snail_num = self.goal_board[i][j]
                linear_num = linear_flat[i * self.size + j]
                snail_to_linear[snail_num] = linear_num
    
        transformed = []
        for row in board:
            new_row = [snail_to_linear[num] for num in row]
            transformed.append(new_row)
        
        return transformed

    def is_solvable(self) -> bool:
        """
        Check if puzzle is solvable by:
        1. Transform initial state to linear pattern equivalent
        2. Check solvability using standard linear pattern rules
        https://www.geeksforgeeks.org/check-instance-8-puzzle-solvable/
        https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/
        """
        transformed_board = self._transform_to_linear(self.board)
    
        print("\nGoal board (linear pattern):")
        for row in self._generate_linear_goal():
            print(row)
        print("\nTransformed board (linear pattern):")
        for row in transformed_board:
            print(row)
        
        # Count inversions relative to linear pattern
        # Get positions in linear pattern (1 should be in position 0, 2 in position 1, etc.)
        flat_board = [num for row in transformed_board for num in row if num != 0]
        print("\n1D Transformed board without 0:")
        print(flat_board)

        # Count inversions
        inversions = 0
        for i in range(len(flat_board)):
            for j in range(i + 1, len(flat_board)):
                if flat_board[i] > flat_board[j]:
                    inversions += 1
        
        blank_position = self._find_number_in_board(0, transformed_board)
        blank_row_from_bottom = self.size - blank_position[0] - 1
        
        print(f"Inversions: {inversions}")
        print(f"blank row from bottom: {blank_row_from_bottom}")
        
        # Apply standard linear pattern solvability rules
        if self.size % 2 == 1:
            solvable = inversions % 2 == 0
        else:
            if blank_row_from_bottom % 2 == 0:
                solvable = inversions % 2 == 1
            else:
                solvable = inversions % 2 == 0
        return solvable

    def get_neighbors_states(self) -> List['PuzzleState']:
        """
        Generate all possible next states
        1 2 3     1 0 3     1 2 3     1 2 3     1 2 3
        8 0 4  →  8 2 4  +  8 6 4  +  0 8 4  +  8 4 0 
        7 6 5     7 6 5     7 0 5     7 6 5     7 6 5
        """
        neighbors = []
        
        # Possible moves: (row_change, column_change, move_name)
        possible_moves = [
            (-1, 0, "UP"),
            (1, 0, "DOWN"),
            (0, -1, "LEFT"),
            (0, 1, "RIGHT")
        ]
        
        empty_row, empty_col = self.empty_pos
        
        for row_change, col_change, move_name in possible_moves:
            # Calculate new position for empty tile
            new_row = empty_row + row_change
            new_col = empty_col + col_change
            
            # Check if new position is within board boundaries
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                # Create a copy of current board
                new_board = []
                for row in self.board:
                    new_board.append(row[:]) # Append copy not reference with [:]
                
                # Swap empty tile with neighbor
                new_board[empty_row][empty_col] = new_board[new_row][new_col]
                new_board[new_row][new_col] = 0
                
                neighbors.append(PuzzleState(new_board, self, move_name))
        
        return neighbors

    def manhattan_distance(self) -> int:
        """Total Manhattan distance for current state"""
        distance = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0:
                    goal_pos = self._find_number_in_board(number, self.goal_board)
                    distance += abs(i - goal_pos[0]) + abs(j - goal_pos[1])
        return distance

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
        manhattan = self.manhattan_distance()
        misplaced = self.misplaced_tiles()
        euclidean = self.euclidean_distance()

        # Weights = 1, 0.5, 0.1 respectively, manhattan is the most important
        return manhattan + 0.5 * misplaced + 0.1 * euclidean

class NPuzzleSolver:
    def __init__(self, initial_state: PuzzleState):
        self.initial_state = initial_state
        self.nodes_selected = 0 # Number of states we looked at
        self.max_nodes_stored = 0 # Maximum number of states stored in memory

    def solve(self):
        open_set = []
        closed_set = set()
        
        initial_f = self.initial_state.g_score + self.initial_state.get_heuristic_score()
        heapq.heappush(open_set, (initial_f, id(self.initial_state), self.initial_state))
        
        print("\nStarting A* search:")
        print(f"Initial f_score: {initial_f}")
        print(f"Initial manhattan: {self.initial_state.manhattan_distance()}")
        print(f"Initial misplaced: {self.initial_state.misplaced_tiles()}")
        print(f"Initial euclidean: {self.initial_state.euclidean_distance()}")
        
        while open_set:
            current_f, _, current_state = heapq.heappop(open_set)
            
            # Debug every 10k nodes
            if self.nodes_selected % 10000 == 0:
                print(f"Nodes selected: {self.nodes_selected}, f_score: {current_f}, g_score: {current_state.g_score}, h_score: {current_state.get_heuristic_score()}")

            board_tuple = tuple(map(tuple, current_state.board))
            if board_tuple in closed_set:
                continue
            
            if current_state.is_goal_state():
                return current_state
                
            closed_set.add(board_tuple)
            
            for neighbor in current_state.get_neighbors_states():
                neighbor_tuple = tuple(map(tuple, neighbor.board))
                if neighbor_tuple in closed_set:
                    continue
                    
                f_score = neighbor.g_score + neighbor.get_heuristic_score()
                heapq.heappush(open_set, (f_score, id(neighbor), neighbor))
            
            self.nodes_selected += 1
            self.max_nodes_stored = max(self.max_nodes_stored, 
                                    len(open_set) + len(closed_set))
        
        return None

    def reconstruct_path(self, final_state: PuzzleState) -> List[str]:
        """Backtrack from final state to initial state using parent references to get the sequence of moves."""
        path = []
        current = final_state
        
        # Follow parent references until we reach initial state (which has no parent)
        while current.parent is not None:
            path.append(current.move)
            current = current.parent
        
        # Reverse path because we collected moves backwards
        return list(reversed(path))

    def print_solution(self, final_state: PuzzleState):
        """Shows each state in the solution path"""
        # Collect all states from goal back to start
        states = []
        current = final_state
        while current is not None:
            states.append(current)
            current = current.parent
        
        # Print from start to goal
        states.reverse()
        for i, state in enumerate(states):
            print(f"\nStep {i}:")
            for row in state.board:
                print(row)
            if i < len(states) - 1:
                print(f"Move: {states[i + 1].move}")

def main(): 
    try:
        board = parse_puzzle_file("../snail.txt")
        initial_state = PuzzleState(board)
        
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
            moves = solver.reconstruct_path(solution)
            print("\nSolution path:")
            solver.print_solution(solution)
            print(f"\nSolution found in {len(moves)} moves!")
            print(f"Moves: {moves}")
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
            # Read all lines and remove comments and empty lines
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
            
            # Parse board
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