"""
Renderer Module for Tic Tac Toe Game
Handles all visual rendering using Pygame
"""

import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, GRID_SIZE, CELL_SIZE, BOARD_PADDING,
    COLOR_WHITE, COLOR_BLACK, COLOR_GRAY, COLOR_BLUE, COLOR_RED, COLOR_GREEN,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER, PLAYER_X, PLAYER_O
)


class GameRenderer:
    """
    Renders the Tic Tac Toe game using Pygame.
    
    Manages the pygame display window and handles all drawing operations including:
    - Game board with grid lines
    - Player moves (X and O symbols)
    - Menu with game mode options
    - Game over screen with winner information
    - Turn indicator
    - Mouse click to board position conversion
    """
    
    def __init__(self, width, height, grid_size, cell_size):
        """
        Initialize the pygame display and renderer.
        
        Args:
            width (int): Window width in pixels
            height (int): Window height in pixels
            grid_size (int): Size of the tic tac toe grid (typically 3)
            cell_size (int): Size of each cell in pixels
        """
        # Initialize pygame
        pygame.init()
        
        # Store dimensions
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cell_size = cell_size
        
        # Create display window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tic Tac Toe")
        
        # Create clock for FPS management
        self.clock = pygame.time.Clock()
        self.fps = FPS
        
        # Set up fonts
        self.font_large = pygame.font.Font(None, 72)  # For X and O symbols
        self.font_medium = pygame.font.Font(None, 48)  # For menu/game over text
        self.font_small = pygame.font.Font(None, 32)   # For regular text
        
        # Calculate board position (centered on screen with padding)
        self.board_start_x = BOARD_PADDING
        self.board_start_y = BOARD_PADDING
        self.board_end_x = self.board_start_x + (self.grid_size * self.cell_size)
        self.board_end_y = self.board_start_y + (self.grid_size * self.cell_size)
    
    def draw_board(self, board_state):
        """
        Draw the 3x3 grid lines on the board.
        
        Args:
            board_state (list): The current board state (not directly used for grid drawing)
        """
        # Draw vertical lines
        for i in range(1, self.grid_size):
            x = self.board_start_x + (i * self.cell_size)
            pygame.draw.line(
                self.screen,
                COLOR_GRAY,
                (x, self.board_start_y),
                (x, self.board_end_y),
                2
            )
        
        # Draw horizontal lines
        for i in range(1, self.grid_size):
            y = self.board_start_y + (i * self.cell_size)
            pygame.draw.line(
                self.screen,
                COLOR_GRAY,
                (self.board_start_x, y),
                (self.board_end_x, y),
                2
            )
    
    def draw_moves(self, board_state):
        """
        Draw X and O symbols on the board cells.
        
        Uses COLOR_BLUE for X symbols and COLOR_RED for O symbols.
        
        Args:
            board_state (list): 3x3 grid representing the board state
        """
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_value = board_state[row][col]
                
                if cell_value is not None:
                    # Calculate cell center position
                    cell_x = self.board_start_x + (col * self.cell_size) + (self.cell_size // 2)
                    cell_y = self.board_start_y + (row * self.cell_size) + (self.cell_size // 2)
                    
                    # Render text
                    if cell_value == PLAYER_X:
                        text_surface = self.font_large.render(PLAYER_X, True, COLOR_BLUE)
                    else:  # PLAYER_O
                        text_surface = self.font_large.render(PLAYER_O, True, COLOR_RED)
                    
                    # Get text rect and center it in the cell
                    text_rect = text_surface.get_rect(center=(cell_x, cell_y))
                    self.screen.blit(text_surface, text_rect)
    
    def draw_menu(self, scores):
        """
        Display the main menu with game mode options and score information.
        
        Args:
            scores (dict): Dictionary containing score information with keys like
                          'human' and 'ai' for tracking wins
        """
        # Clear screen
        self.screen.fill(COLOR_WHITE)
        
        # Draw title
        title_surface = self.font_medium.render("Tic Tac Toe", True, COLOR_BLACK)
        title_rect = title_surface.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Draw scores
        human_score_text = f"Player Wins: {scores.get('human', 0)}"
        ai_score_text = f"AI Wins: {scores.get('ai', 0)}"
        
        human_score_surface = self.font_small.render(human_score_text, True, COLOR_BLACK)
        ai_score_surface = self.font_small.render(ai_score_text, True, COLOR_BLACK)
        
        human_score_rect = human_score_surface.get_rect(center=(self.width // 2, 160))
        ai_score_rect = ai_score_surface.get_rect(center=(self.width // 2, 200))
        
        self.screen.blit(human_score_surface, human_score_rect)
        self.screen.blit(ai_score_surface, ai_score_rect)
        
        # Draw game mode options
        menu_text = "Choose Game Mode:"
        menu_surface = self.font_small.render(menu_text, True, COLOR_BLACK)
        menu_rect = menu_surface.get_rect(center=(self.width // 2, 280))
        self.screen.blit(menu_surface, menu_rect)
        
        # Draw option 1: Play against AI
        option1_surface = self.font_small.render("1. Play vs AI (Press 1)", True, COLOR_BLUE)
        option1_rect = option1_surface.get_rect(center=(self.width // 2, 350))
        self.screen.blit(option1_surface, option1_rect)
        
        # Draw option 2: Two player
        option2_surface = self.font_small.render("2. Two Player (Press 2)", True, COLOR_GREEN)
        option2_rect = option2_surface.get_rect(center=(self.width // 2, 400))
        self.screen.blit(option2_surface, option2_rect)
        
        # Draw instruction
        instruction_surface = self.font_small.render("Click on a cell to make your move", True, COLOR_BLACK)
        instruction_rect = instruction_surface.get_rect(center=(self.width // 2, 500))
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_game_over(self, winner, scores):
        """
        Display the game over screen with winner message and reset option.
        
        Args:
            winner (str): The winner ('X', 'O') or 'Draw' for a tie
            scores (dict): Dictionary containing score information
        """
        # Clear screen with semi-transparent overlay effect (simulated with rectangle)
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(COLOR_WHITE)
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over message
        if winner == 'Draw':
            message = "It's a Draw!"
            color = COLOR_GRAY
        else:
            message = f"Player {winner} Wins!"
            color = COLOR_BLUE if winner == PLAYER_X else COLOR_RED
        
        message_surface = self.font_medium.render(message, True, color)
        message_rect = message_surface.get_rect(center=(self.width // 2, 200))
        self.screen.blit(message_surface, message_rect)
        
        # Draw current scores
        human_score_text = f"Player Wins: {scores.get('human', 0)}"
        ai_score_text = f"AI Wins: {scores.get('ai', 0)}"
        
        human_score_surface = self.font_small.render(human_score_text, True, COLOR_BLACK)
        ai_score_surface = self.font_small.render(ai_score_text, True, COLOR_BLACK)
        
        human_score_rect = human_score_surface.get_rect(center=(self.width // 2, 300))
        ai_score_rect = ai_score_surface.get_rect(center=(self.width // 2, 340))
        
        self.screen.blit(human_score_surface, human_score_rect)
        self.screen.blit(ai_score_surface, ai_score_rect)
        
        # Draw reset instruction
        reset_surface = self.font_small.render("Press SPACE to return to menu", True, COLOR_BLACK)
        reset_rect = reset_surface.get_rect(center=(self.width // 2, 450))
        self.screen.blit(reset_surface, reset_rect)
    
    def draw_turn_indicator(self, current_player):
        """
        Display whose turn it is at the top of the screen.
        
        Args:
            current_player (str): The current player ('X' or 'O')
        """
        if current_player == PLAYER_X:
            text = "Your Turn (X)"
            color = COLOR_BLUE
        else:
            text = "AI Turn (O)"
            color = COLOR_RED
        
        turn_surface = self.font_small.render(text, True, color)
        turn_rect = turn_surface.get_rect(center=(self.width // 2, 20))
        self.screen.blit(turn_surface, turn_rect)
    
    def update_display(self, game_state, board_state, scores, current_player):
        """
        Orchestrate all drawing operations based on current game state.
        
        This method handles the overall rendering pipeline, determining what to draw
        based on the current state of the game.
        
        Args:
            game_state (str): Current state ('menu', 'playing', 'game_over')
            board_state (list): 3x3 grid representing the board state
            scores (dict): Dictionary containing score information
            current_player (str): The current player ('X' or 'O')
        """
        if game_state == STATE_MENU:
            # Draw menu screen
            self.draw_menu(scores)
        
        elif game_state == STATE_PLAYING:
            # Clear screen with white background
            self.screen.fill(COLOR_WHITE)
            
            # Draw turn indicator
            self.draw_turn_indicator(current_player)
            
            # Draw board grid
            self.draw_board(board_state)
            
            # Draw moves (X and O symbols)
            self.draw_moves(board_state)
        
        elif game_state == STATE_GAME_OVER:
            # First draw the game board
            self.screen.fill(COLOR_WHITE)
            self.draw_board(board_state)
            self.draw_moves(board_state)
            
            # Determine winner from board state
            # This will be called with winner info, but we check the board
            winner = self._check_winner_from_board(board_state)
            
            # Draw game over screen on top
            self.draw_game_over(winner, scores)
        
        # Update display
        pygame.display.flip()
        
        # Cap framerate
        self.clock.tick(self.fps)
    
    def _check_winner_from_board(self, board_state):
        """
        Check for a winner in the given board state.
        
        Helper method to determine winner from board state.
        
        Args:
            board_state (list): 3x3 grid representing the board state
        
        Returns:
            str: 'X' if X wins, 'O' if O wins, 'Draw' for tie, None if game ongoing
        """
        # Check rows
        for row in range(self.grid_size):
            if board_state[row][0] is not None and \
               board_state[row][0] == board_state[row][1] == board_state[row][2]:
                return board_state[row][0]
        
        # Check columns
        for col in range(self.grid_size):
            if board_state[0][col] is not None and \
               board_state[0][col] == board_state[1][col] == board_state[2][col]:
                return board_state[0][col]
        
        # Check diagonals
        if board_state[0][0] is not None and \
           board_state[0][0] == board_state[1][1] == board_state[2][2]:
            return board_state[0][0]
        
        if board_state[0][2] is not None and \
           board_state[0][2] == board_state[1][1] == board_state[2][0]:
            return board_state[0][2]
        
        # Check for draw (no moves available and no winner)
        has_empty = any(board_state[i][j] is None for i in range(3) for j in range(3))
        if not has_empty:
            return 'Draw'
        
        return None
    
    def handle_mouse_click(self, pos):
        """
        Convert pixel coordinates to board position (row, col).
        
        Converts mouse click position to grid coordinates on the tic tac toe board.
        Returns None if click is outside the board area.
        
        Args:
            pos (tuple): (x, y) pixel coordinates from mouse click
        
        Returns:
            tuple: (row, col) coordinates on the board (0-2, 0-2) if valid click
                   None if click is outside the board area
        """
        x, y = pos
        
        # Check if click is within board bounds
        if x < self.board_start_x or x > self.board_end_x or \
           y < self.board_start_y or y > self.board_end_y:
            return None
        
        # Calculate which cell was clicked
        col = (x - self.board_start_x) // self.cell_size
        row = (y - self.board_start_y) // self.cell_size
        
        # Ensure indices are within valid range
        if row >= self.grid_size or col >= self.grid_size:
            return None
        
        return (row, col)
    
    def quit(self):
        """
        Close the pygame window and clean up resources.
        
        Terminates the pygame module and closes the display window.
        """
        pygame.quit()
