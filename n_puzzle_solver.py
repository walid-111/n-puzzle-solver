"""
------
Search Algorithms:
------
Breadth-First Search (BFS):
- Explores ALL possible moves level by level
- Problem: Explores EVERYTHING, even bad paths

Dijkstra:
- Like BFS but considers COST of moves, explore cheapeast paths first
- Problem: Still explores in ALL directions

A* = Dijkstra + heuristic (to guess which moves are promising):
- Combines:
  * Cost so far (g_score: number of moves made)
  * Estimated cost to goal (h_score: manhattan+misplaced+euclidean in our case)
  * Total estimate (f_score = g_score + h_score)
- Always explores the move with lowest f_score

Heuristics for n-puzzle: https://cse.iitk.ac.in/users/cs365/2009/ppt/13jan_Aman.pdf
"""

from typing import List, Tuple
import heapq

class PuzzleState:
    """
    This class represents a "snapshot" of how the puzzle looks at any moment.
    """
    def __init__(self, board: List[List[int]], parent=None, move=""):
        """
        board: 2D list representing the puzzle grid
                0 represents the empty space
                Example for 3x3: [[1,2,3], [8,0,4], [7,6,5]]
        parent: The previous state that led to this one (None for initial state)
        move: The move that was made to reach this state ("UP", "DOWN", etc.)
        """

        self.board = board
        self.size = len(board)
        self.parent = parent
        self.move = move
        
        # Calculate how many moves it took to get here
        self.g_score = 0 if parent is None else parent.g_score + 1

        self.empty_pos = self._find_empty()
        self.goal_positions = self._generate_goal_positions()
    
    def _find_empty(self) -> Tuple[int, int]:
        """
        For board: [[1,2,3],
                    [8,0,4],
                    [7,6,5]]
        Returns: (1, 1)
        """
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return (i, j)
        
        raise ValueError("Invalid puzzle: No empty space found")

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

    def _generate_goal_positions(self) -> dict:
        """
        Example for 3x3:
        {
            1: (0,0), 2: (0,1), 3: (0,2),
            8: (1,0), 0: (1,1), 4: (1,2),
            7: (2,0), 6: (2,1), 5: (2,2)
        }
        """
        positions = {}
        number = 1
        top, bottom = 0, self.size-1
        left, right = 0, self.size-1
        
        while number < self.size * self.size:
            # Top row
            for i in range(left, right + 1):
                positions[number] = (top, i)
                number += 1
            top += 1
            
            # Right column
            for i in range(top, bottom + 1):
                positions[number] = (i, right)
                number += 1
            right -= 1
            
            # Bottom row
            for i in range(right, left - 1, -1):
                positions[number] = (bottom, i)
                number += 1
            bottom -= 1
            
            # Left column
            for i in range(bottom, top - 1, -1):
                positions[number] = (i, left)
                number += 1
            left += 1
        
        # Add empty space (0) in center
        positions[0] = (self.size // 2, self.size // 2)
        return positions

    def manhattan_distance(self) -> int:
        """
        Total Manhattan distance for current state (ADMISSIBLE HEURISTIC)   
        Example for number 7 in 3x3:
        Current:   Goal:
        1 2 3     1 2 3
        8 7 4  vs 8 0 4   -> 7 is at (1,1), should be at (2,0)
        6 0 5     7 6 5      Distance = |1-2| + |1-0| = 2
        """
        distance = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0:  # Skip empty tile
                    goal_row, goal_col = self.goal_positions[number]
                    distance += abs(i - goal_row) + abs(j - goal_col)
        return distance
    
    def misplaced_tiles(self) -> int:
        """
        Total number of misplaced tiles. (ADMISSIBLE HEURISTIC)
        """
        count = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0 and self.goal_positions[number] != (i, j):
                    count += 1
        return count
    
    def euclidean_distance(self) -> float:
        """
        Total Euclidean distance for current state. (ADMISSIBLE HEURISTIC)
        """
        distance = 0
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0:
                    goal_row, goal_col = self.goal_positions[number]
                    distance += ((i - goal_row) ** 2 + (j - goal_col) ** 2) ** 0.5
        return distance

    def get_heuristic_score(self) -> int:
        """
        Returns the heuristic score for the current state.
        """
        manhattan = self.manhattan_distance()
        misplaced = self.misplaced_tiles()
        euclidean = self.euclidean_distance()

        # Weights = 1, 0.5, 0.1 respectively, manhattan is the most important
        return manhattan + 0.5 * misplaced + 0.1 * euclidean

    def is_goal_state(self) -> bool:
        """
        Check if current state matches goal state configuration
        """
        for i in range(self.size):
            for j in range(self.size):
                number = self.board[i][j]
                if number != 0:
                    goal_pos = self.goal_positions[number]
                    if (i, j) != goal_pos:
                        return False
        return True

    # When we try to print any object using print(), Python automatically looks for its __str__ method
    def __str__(self) -> str:
        """
        string representation of the board.
        Example:
        1 2 3
        8 0 4
        7 6 5
        """
        result = ""
        
        for row in self.board:
            row_string = ""
            for number in row:
                row_string += str(number) + " "
            result += row_string.strip() + "\n"
        
        return result.strip()

class NPuzzleSolver:
    def __init__(self, initial_state: PuzzleState):
        self.initial_state = initial_state
        self.nodes_selected = 0 # Number of states we looked at
        self.max_nodes_stored = 0 # Maximum number of states stored in memory

    def solve(self):
        open_set = []
        closed_set = set()
        
        # Add initial state
        initial_f = self.initial_state.g_score + self.initial_state.get_heuristic_score()
        heapq.heappush(open_set, (initial_f, id(self.initial_state), self.initial_state))
        
        while open_set:  # Add a limit to prevent infinite loops
            current_f, _, current_state = heapq.heappop(open_set)
            
            # Convert board to tuple for set operations
            board_tuple = tuple(map(tuple, current_state.board))
            
            if board_tuple in closed_set:
                continue
            
            # Check if this is goal state
            if current_state.is_goal_state():
                return current_state
                
            closed_set.add(board_tuple)
            
            # Try all possible moves
            for neighbor in current_state.get_neighbors_states():
                neighbor_tuple = tuple(map(tuple, neighbor.board))
                if neighbor_tuple in closed_set:
                    continue
                    
                f_score = neighbor.g_score + neighbor.get_heuristic_score()
                heapq.heappush(open_set, (f_score, id(neighbor), neighbor))
            
            self.nodes_selected += 1
            self.max_nodes_stored = max(self.max_nodes_stored, 
                                    len(open_set) + len(closed_set))
        
        return None  # No solution found

    def reconstruct_path(self, final_state: PuzzleState) -> List[str]:
        """
        Backtrack from final state to initial state  using parent references to get the sequence of moves.
        """
        path = []
        current = final_state
        
        # Follow parent references until we reach initial state (which has no parent)
        while current.parent is not None:
            path.append(current.move)
            current = current.parent
        
        # Reverse path because we collected moves backwards
        return list(reversed(path))

    def print_solution(self, final_state: PuzzleState):
        """
        Shows each state in the solution path
        """
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
            print(state)
            if i < len(states) - 1:
                print(f"Move: {states[i + 1].move}")

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

def main():
    test_file_content = """3
3 1 2
8 0 4
7 6 5"""
    
    with open("test_puzzle.txt", "w") as f:
        f.write(test_file_content)
    
    try:
        board = parse_puzzle_file("test_puzzle.txt")
        initial_state = PuzzleState(board)
        
        print("Initial state:")
        print(initial_state)
        print("\nGoal positions:")
        for num in range(initial_state.size * initial_state.size):
            print(f"Number {num} should be at {initial_state.goal_positions[num]}")
        
        solver = NPuzzleSolver(initial_state)
        solution = solver.solve()
        
        if solution:
            moves = solver.reconstruct_path(solution)
            print(f"\nSolution found in {len(moves)} moves!")
            print(f"Moves: {moves}")
            print(f"Nodes examined: {solver.nodes_selected}")
            print(f"Max nodes in memory: {solver.max_nodes_stored}")
            
            print("\nSolution path:")
            solver.print_solution(solution)
        else:
            print("\nNo solution found")
            print(f"Nodes examined: {solver.nodes_selected}")
            
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()