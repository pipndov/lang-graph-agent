"""
AI Module for Tic Tac Toe Game
Implements an AI opponent using the minimax algorithm with alpha-beta pruning
"""

from board import Board


class AIPlayer:
    """
    Represents an AI player that uses the minimax algorithm to determine optimal moves.
    
    The AI evaluates all possible game states and selects the move that maximizes
    its chances of winning while minimizing the opponent's chances. Alpha-beta pruning
    is used to optimize the search by eliminating branches that cannot affect the final result.
    """
    
    def __init__(self, player_symbol='O'):
        """
        Initialize the AI player.
        
        Args:
            player_symbol (str): The symbol representing the AI player ('O' or 'X').
                                Defaults to 'O'.
        """
        self.player_symbol = player_symbol
        # Determine opponent symbol
        self.opponent_symbol = 'X' if player_symbol == 'O' else 'O'
    
    def minimax(self, board, depth, is_maximizing, alpha=float('-inf'), 
                beta=float('inf'), player_x_symbol='X', player_o_symbol='O'):
        """
        Recursively evaluate board positions using the minimax algorithm with alpha-beta pruning.
        
        This algorithm explores all possible game states to a given depth and assigns scores
        based on the outcomes. Alpha-beta pruning eliminates branches that cannot affect
        the final decision, significantly improving performance.
        
        Args:
            board (Board): The current game board state
            depth (int): The current depth in the game tree (0 at leaf nodes)
            is_maximizing (bool): True if maximizing player's turn, False for minimizing
            alpha (float): Alpha value for alpha-beta pruning (best value for maximizer)
            beta (float): Beta value for alpha-beta pruning (best value for minimizer)
            player_x_symbol (str): The symbol used by player X. Defaults to 'X'.
            player_o_symbol (str): The symbol used by player O. Defaults to 'O'.
        
        Returns:
            int: The minimax score for the given board state:
                 +10 if AI (maximizing player) wins
                 -10 if human (minimizing player) wins
                 0 for draw/tie
                 Adjusted by depth to prefer faster wins/losses
        """
        # Check terminal states (game over)
        winner = board.check_winner()
        
        # AI win: return positive score adjusted by depth (prefer faster wins)
        if winner == self.player_symbol:
            return 10 - depth
        
        # Human win: return negative score adjusted by depth (prefer slower losses)
        if winner == self.opponent_symbol:
            return depth - 10
        
        # Draw: return 0
        if board.check_draw():
            return 0
        
        # Get available moves for recursion
        available_moves = board.get_available_moves()
        
        if is_maximizing:
            # Maximizing player (AI) tries to maximize score
            max_eval = float('-inf')
            for row, col in available_moves:
                # Make the move temporarily
                board.make_move(row, col, self.player_symbol)
                
                # Recursively evaluate with minimizing player's turn
                eval_score = self.minimax(board, depth + 1, False, alpha, beta,
                                        player_x_symbol, player_o_symbol)
                
                # Undo the move
                board.grid[row][col] = None
                
                # Update max evaluation
                max_eval = max(max_eval, eval_score)
                
                # Alpha-beta pruning: update alpha
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            # Minimizing player (opponent) tries to minimize score
            min_eval = float('inf')
            for row, col in available_moves:
                # Make the move temporarily
                board.make_move(row, col, self.opponent_symbol)
                
                # Recursively evaluate with maximizing player's turn
                eval_score = self.minimax(board, depth + 1, True, alpha, beta,
                                        player_x_symbol, player_o_symbol)
                
                # Undo the move
                board.grid[row][col] = None
                
                # Update min evaluation
                min_eval = min(min_eval, eval_score)
                
                # Alpha-beta pruning: update beta
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval
    
    def get_best_move(self, board):
        """
        Determine the best move for the AI player using minimax algorithm.
        
        Evaluates all available moves and returns the one with the highest minimax score.
        This represents the optimal move for the AI player given the current board state.
        
        Args:
            board (Board): The current game board state
        
        Returns:
            tuple: A (row, col) tuple representing the best move for the AI.
                   If no moves are available, returns None.
        
        Raises:
            ValueError: If the board has no available moves
        """
        available_moves = board.get_available_moves()
        
        if not available_moves:
            return None
        
        best_score = float('-inf')
        best_move = None
        
        # Evaluate each available move
        for row, col in available_moves:
            # Make the move temporarily
            board.make_move(row, col, self.player_symbol)
            
            # Evaluate this move using minimax (opponent's turn - minimizing)
            move_score = self.minimax(board, 0, False)
            
            # Undo the move
            board.grid[row][col] = None
            
            # Update best move if this one is better
            if move_score > best_score:
                best_score = move_score
                best_move = (row, col)
        
        return best_move
