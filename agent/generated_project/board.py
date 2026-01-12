"""
Board Module for Tic Tac Toe Game
Manages the game board state and provides methods for game logic
"""

from constants import GRID_SIZE, PLAYER_X, PLAYER_O


class Board:
    """
    Represents the Tic Tac Toe game board.
    
    The board is a 3x3 grid where each cell can contain 'X', 'O', or None (empty).
    This class manages the board state and provides methods for move validation,
    checking for winners, and board status.
    """
    
    def __init__(self):
        """
        Initialize the board with a 3x3 grid of None values.
        Each cell is empty at the start of the game.
        """
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def make_move(self, row, col, player):
        """
        Place a player's mark (X or O) on the board at the specified position.
        
        Args:
            row (int): Row index (0-2)
            col (int): Column index (0-2)
            player (str): Player mark ('X' or 'O')
        
        Returns:
            bool: True if move was successful, False if cell is already occupied
        """
        if not self.is_valid_move(row, col):
            return False
        
        self.grid[row][col] = player
        return True
    
    def is_valid_move(self, row, col):
        """
        Check if a move is legal (cell is within bounds and empty).
        
        Args:
            row (int): Row index (0-2)
            col (int): Column index (0-2)
        
        Returns:
            bool: True if move is valid, False otherwise
        """
        # Check if indices are within grid bounds
        if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
            return False
        
        # Check if cell is empty
        if self.grid[row][col] is not None:
            return False
        
        return True
    
    def get_board(self):
        """
        Get the current board state.
        
        Returns:
            list: 3x3 grid representing the board state
        """
        return self.grid
    
    def get_available_moves(self):
        """
        Get a list of all available moves (empty cells).
        
        Returns:
            list: List of (row, col) tuples for empty cells
        """
        available_moves = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    available_moves.append((row, col))
        
        return available_moves
    
    def check_winner(self):
        """
        Check if there is a winner on the board.
        
        Checks all rows, columns, and diagonals for three matching marks.
        
        Returns:
            str: 'X' if X wins, 'O' if O wins, None if no winner
        """
        # Check rows
        for row in range(GRID_SIZE):
            if self.grid[row][0] is not None and \
               self.grid[row][0] == self.grid[row][1] == self.grid[row][2]:
                return self.grid[row][0]
        
        # Check columns
        for col in range(GRID_SIZE):
            if self.grid[0][col] is not None and \
               self.grid[0][col] == self.grid[1][col] == self.grid[2][col]:
                return self.grid[0][col]
        
        # Check diagonals
        # Top-left to bottom-right
        if self.grid[0][0] is not None and \
           self.grid[0][0] == self.grid[1][1] == self.grid[2][2]:
            return self.grid[0][0]
        
        # Top-right to bottom-left
        if self.grid[0][2] is not None and \
           self.grid[0][2] == self.grid[1][1] == self.grid[2][0]:
            return self.grid[0][2]
        
        return None
    
    def check_draw(self):
        """
        Check if the board is full with no winner (draw/tie game).
        
        Returns:
            bool: True if board is full and no winner exists, False otherwise
        """
        # Check if there are any available moves
        if len(self.get_available_moves()) > 0:
            return False
        
        # Check if there's a winner
        if self.check_winner() is not None:
            return False
        
        # Board is full and no winner
        return True
    
    def reset(self):
        """
        Clear the board and reset it to initial state (all None values).
        Used to start a new game.
        """
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def __repr__(self):
        """
        String representation of the board for debugging.
        
        Returns:
            str: Visual representation of the board
        """
        board_str = "\n"
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.grid[row][col] if self.grid[row][col] else " "
                board_str += f" {cell} "
                if col < GRID_SIZE - 1:
                    board_str += "|"
            board_str += "\n"
            if row < GRID_SIZE - 1:
                board_str += "-----------\n"
        return board_str
