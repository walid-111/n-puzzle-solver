from typing import List, Tuple
from copy import deepcopy

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

        # Store the current board configuration
        self.board = board

        self.size = len(board)
        self.parent = parent
        self.move = move
        
        # Calculate how many moves it took to get here
        self.g_score = 0 if parent is None else parent.g_score + 1
        
        # Find where the empty space (0) is on the board
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

    def get_neighbors(self) -> List['PuzzleState']:
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
        Calculates total Manhattan distance for current state.
        Manhattan distance is sum of horizontal and vertical distances
        each tile is from its goal position.
        
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

def parse_puzzle_file(filename: str) -> List[List[int]]:
    """
    Format example:
    3
    3 2 6
    1 4 0
    8 7 5
    """
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
    test_file_content = """# this is a comment
3
3 2 6 # another comment
1 4 0
8 7 5"""
    
    with open("test_puzzle.txt", "w") as f:
        f.write(test_file_content)
    
    try:
        board = parse_puzzle_file("test_puzzle.txt")
    
        state = PuzzleState(board)
        
        print("Current state:")
        print(state)
        print("\nGoal positions for each number:")
        for num in range(1, state.size * state.size):
            print(f"Number {num} should be at {state.goal_positions[num]}")
        
        print(f"\nTotal Manhattan distance: {state.manhattan_distance()}")
        
        print("\nPossible moves and their Manhattan distances:")
        for neighbor in state.get_neighbors():
            print(f"\nAfter move {neighbor.move}:")
            print(neighbor)
            print(f"Manhattan distance: {neighbor.manhattan_distance()}")
        
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()