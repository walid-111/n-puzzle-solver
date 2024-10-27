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

def main():
    initial_board = [
        [1, 2, 3],
        [8, 0, 4],
        [7, 6, 5]
    ]
    
    state = PuzzleState(initial_board)
    
    print("Initial puzzle state:")
    print(state)
    print(f"\nEmpty space is at position: {state.empty_pos}")
    print(f"Puzzle size is: {state.size}x{state.size}")
    print(f"Number of moves so far: {state.g_score}")

if __name__ == "__main__":
    main()