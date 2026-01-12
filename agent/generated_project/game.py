"""
Game Controller Module for Tic Tac Toe Game
Implements the main game controller and state machine
"""

from board import Board
from renderer import GameRenderer
from ai import AIPlayer
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, CELL_SIZE,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER,
    PLAYER_X, PLAYER_O, PLAYER_HUMAN, PLAYER_AI
)


class GameController:
    """
    Main game controller that orchestrates all game logic and state management.
    
    The GameController is the central component that coordinates the board, renderer,
    AI player, and game state. It manages:
    - Game state transitions (menu -> playing -> game_over -> menu)
    - Turn management and player switching
    - Move validation and execution
    - AI decision-making
    - Score tracking
    - Game mode selection (human vs AI or human vs human)
    
    This class serves as the core orchestrator called by main.py to run the game loop.
    """
    
    def __init__(self):
        """
        Initialize the game controller with all necessary components.
        
        Sets up:
        - The game board
        - The renderer for displaying the game
        - The AI player
        - Initial game state set to STATE_MENU
        - Score tracking (human, AI, and draws)
        - Current player tracking
        - Game mode (defaults to human vs AI)
        """
        self.board = Board()
        self.renderer = GameRenderer(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, CELL_SIZE)
        self.ai = AIPlayer(player_symbol=PLAYER_O)
        
        # Game state initialization
        self.game_state = STATE_MENU
        self.scores = {
            'human': 0,
            'ai': 0,
            'draws': 0
        }
        self.current_player = PLAYER_X
        
        # Game mode tracking
        self.game_mode = 'human_vs_ai'  # Can be 'human_vs_ai' or 'human_vs_human'
        self.player_types = {
            PLAYER_X: PLAYER_HUMAN,  # Human plays as X
            PLAYER_O: PLAYER_AI      # AI plays as O
        }
    
    def handle_click(self, pos):
        """
        Handle a mouse click event and convert it to a board move.
        
        Converts the pixel coordinates of the click to board coordinates,
        validates the move, and if valid, applies it to the board.
        This method is called when a mouse click occurs during gameplay.
        
        Args:
            pos (tuple): (x, y) pixel coordinates of the mouse click
        
        Returns:
            bool: True if move was successfully applied, False otherwise
        """
        # Convert click position to board coordinates
        board_pos = self.renderer.handle_mouse_click(pos)
        
        # If click is outside board area, return False
        if board_pos is None:
            return False
        
        row, col = board_pos
        
        # Validate the move
        if not self.board.is_valid_move(row, col):
            return False
        
        # Apply move to board
        success = self.board.make_move(row, col, self.current_player)
        return success
    
    def process_turn(self):
        """
        Process the current turn, executing AI move if applicable.
        
        Checks if the current player is the AI. If so, it calls the AI's
        get_best_move() method and executes the move on the board.
        For human players, this method does nothing (human moves via handle_click).
        
        Returns:
            bool: True if AI move was executed, False if it's human player's turn
        """
        # Check if current player is AI
        if self.current_player == PLAYER_O and self.player_types[PLAYER_O] == PLAYER_AI:
            # Get AI's best move
            best_move = self.ai.get_best_move(self.board)
            
            if best_move is not None:
                row, col = best_move
                # Execute the move
                self.board.make_move(row, col, self.current_player)
                return True
        
        return False
    
    def check_game_end(self):
        """
        Check if the game has ended and update state accordingly.
        
        Checks for a winner using board.check_winner() and for a draw using
        board.check_draw(). If the game has ended, updates the scores dictionary
        and transitions the game state to STATE_GAME_OVER.
        
        Returns:
            bool: True if game has ended, False if game is still ongoing
        """
        winner = self.board.check_winner()
        is_draw = self.board.check_draw()
        
        # Check if there's a winner
        if winner is not None:
            # Update scores
            if winner == PLAYER_X:
                self.scores['human'] += 1
            else:  # PLAYER_O
                self.scores['ai'] += 1
            
            # Transition to game over state
            self.game_state = STATE_GAME_OVER
            return True
        
        # Check for draw
        if is_draw:
            # Update draw count
            self.scores['draws'] += 1
            
            # Transition to game over state
            self.game_state = STATE_GAME_OVER
            return True
        
        return False
    
    def reset_game(self):
        """
        Reset the game for a new round while keeping scores.
        
        Clears the board, sets the game state back to STATE_PLAYING,
        and alternates the starting player between games.
        This prepares the game for another round without resetting scores.
        """
        # Reset the board
        self.board.reset()
        
        # Set state to playing
        self.game_state = STATE_PLAYING
        
        # Alternate starting player (switch who goes first)
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
    
    def update_game_state(self):
        """
        Manage the overall game state and turn flow.
        
        This is the main update method that orchestrates the game loop.
        It handles:
        - Processing turns (AI moves or waiting for human)
        - Checking for game end conditions
        - Switching between players
        
        This method should be called once per frame or game tick.
        
        Returns:
            None
        """
        if self.game_state != STATE_PLAYING:
            return
        
        # Process current turn (AI move if applicable)
        ai_moved = self.process_turn()
        
        # If a move was made (human or AI), check for game end
        if ai_moved:
            # Check if game ended after AI move
            if self.check_game_end():
                return
            
            # Switch to human player
            self.current_player = PLAYER_X if self.current_player == PLAYER_O else PLAYER_O
        # If no AI move but it's AI's turn, wait for AI decision
        # If it's human's turn, wait for click via handle_click
    
    def handle_human_move(self, pos):
        """
        Handle a human player's move triggered by a mouse click.
        
        Processes the click, validates and applies the move, then automatically
        switches turns and processes AI moves if applicable.
        
        Args:
            pos (tuple): (x, y) pixel coordinates of the mouse click
        
        Returns:
            bool: True if human move was successfully applied, False otherwise
        """
        if self.game_state != STATE_PLAYING:
            return False
        
        # Only allow human to click if it's their turn
        if self.player_types[self.current_player] != PLAYER_HUMAN:
            return False
        
        # Handle the click and apply move
        if not self.handle_click(pos):
            return False
        
        # Check if game ended after human move
        if self.check_game_end():
            return True
        
        # Switch to other player
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
        
        # If it's now AI's turn and game mode is human vs AI, process AI turn
        if self.game_mode == 'human_vs_ai' and self.current_player == PLAYER_O:
            ai_moved = self.process_turn()
            if ai_moved:
                if self.check_game_end():
                    return True
                # Switch back to human
                self.current_player = PLAYER_X
        
        return True
    
    def toggle_game_mode(self, mode):
        """
        Switch between different game modes.
        
        Allows switching between 'human_vs_ai' and 'human_vs_human' modes.
        Updates the player_types dictionary to reflect who is human and who is AI.
        
        Args:
            mode (str): The game mode to switch to.
                       Options: 'human_vs_ai' or 'human_vs_human'
        
        Returns:
            None
        """
        if mode not in ['human_vs_ai', 'human_vs_human']:
            return
        
        self.game_mode = mode
        
        if mode == 'human_vs_ai':
            # Human plays as X, AI plays as O
            self.player_types[PLAYER_X] = PLAYER_HUMAN
            self.player_types[PLAYER_O] = PLAYER_AI
        elif mode == 'human_vs_human':
            # Both human players
            self.player_types[PLAYER_X] = PLAYER_HUMAN
            self.player_types[PLAYER_O] = PLAYER_HUMAN
    
    def start_game(self, mode='human_vs_ai'):
        """
        Start a new game with the specified mode.
        
        Sets up the game with the selected mode and transitions to STATE_PLAYING.
        Resets the board and sets the starting player to X.
        
        Args:
            mode (str): The game mode ('human_vs_ai' or 'human_vs_human')
        
        Returns:
            None
        """
        self.toggle_game_mode(mode)
        self.board.reset()
        self.current_player = PLAYER_X
        self.game_state = STATE_PLAYING
    
    def return_to_menu(self):
        """
        Return to the main menu.
        
        Transitions the game state back to STATE_MENU without resetting scores.
        This allows players to review their scores and select a new game mode.
        
        Returns:
            None
        """
        self.game_state = STATE_MENU
    
    def render(self):
        """
        Render the current game state to the screen.
        
        Calls the renderer's update_display method with the current game state,
        board state, scores, and current player information.
        
        Returns:
            None
        """
        board_state = self.board.get_board()
        self.renderer.update_display(
            self.game_state,
            board_state,
            self.scores,
            self.current_player
        )
    
    def quit(self):
        """
        Clean up resources and close the game.
        
        Closes the pygame window and terminates the renderer.
        
        Returns:
            None
        """
        self.renderer.quit()
