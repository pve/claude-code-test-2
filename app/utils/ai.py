"""AI algorithms for tic-tac-toe game with difficulty levels."""

import random
from typing import Tuple, Optional
from app.models.tictactoe import TicTacToeGame


class TicTacToeAI:
    """
    AI player for tic-tac-toe game with configurable difficulty levels.
    
    Implements minimax algorithm with alpha-beta pruning for optimal play,
    and various strategies for different difficulty levels.
    """
    
    def __init__(self, difficulty: str = 'medium'):
        """
        Initialize AI with specified difficulty level.
        
        Args:
            difficulty: AI difficulty ('easy', 'medium', 'hard')
        """
        self.difficulty = difficulty.lower()
        self.ai_player = TicTacToeGame.PLAYER_O
        self.human_player = TicTacToeGame.PLAYER_X
    
    def get_move(self, game: TicTacToeGame) -> Tuple[int, int]:
        """
        Get the AI's next move based on difficulty level.
        
        Args:
            game: Current game state
            
        Returns:
            Tuple of (row, col) for AI's move
            
        Raises:
            ValueError: If no valid moves available
        """
        empty_cells = game.get_empty_cells()
        
        if not empty_cells:
            raise ValueError("No valid moves available")
        
        if self.difficulty == 'easy':
            return self._get_easy_move(game, empty_cells)
        elif self.difficulty == 'medium':
            return self._get_medium_move(game, empty_cells)
        elif self.difficulty == 'hard':
            return self._get_hard_move(game)
        else:
            raise ValueError(f"Invalid difficulty level: {self.difficulty}")
    
    def _get_easy_move(self, game: TicTacToeGame, empty_cells: list) -> Tuple[int, int]:
        """
        Easy difficulty: mostly random moves with occasional defensive play.
        
        Args:
            game: Current game state
            empty_cells: List of available positions
            
        Returns:
            Tuple of (row, col) for move
        """
        # 80% random, 20% chance to block winning move
        if random.random() < 0.2:
            # Try to block human win
            blocking_move = self._find_blocking_move(game)
            if blocking_move:
                return blocking_move
        
        # Otherwise, random move
        return random.choice(empty_cells)
    
    def _get_medium_move(self, game: TicTacToeGame, empty_cells: list) -> Tuple[int, int]:
        """
        Medium difficulty: strategic play with some randomness.
        
        Args:
            game: Current game state
            empty_cells: List of available positions
            
        Returns:
            Tuple of (row, col) for move
        """
        # Priority: win > block > center > corner > random
        
        # 1. Try to win
        winning_move = self._find_winning_move(game, self.ai_player)
        if winning_move:
            return winning_move
        
        # 2. Block human win
        blocking_move = self._find_blocking_move(game)
        if blocking_move:
            return blocking_move
        
        # 3. Take center if available
        if (1, 1) in empty_cells:
            return (1, 1)
        
        # 4. Take corners
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        available_corners = [pos for pos in corners if pos in empty_cells]
        if available_corners:
            return random.choice(available_corners)
        
        # 5. Random move
        return random.choice(empty_cells)
    
    def _get_hard_move(self, game: TicTacToeGame) -> Tuple[int, int]:
        """
        Hard difficulty: optimal play using minimax algorithm.
        
        Args:
            game: Current game state
            
        Returns:
            Tuple of (row, col) for optimal move
        """
        _, best_move = self._minimax(game, True)
        return best_move
    
    def _find_winning_move(self, game: TicTacToeGame, player: str) -> Optional[Tuple[int, int]]:
        """
        Find a move that would result in a win for the specified player.
        
        Args:
            game: Current game state
            player: Player to find winning move for
            
        Returns:
            Winning move position or None if no winning move exists
        """
        for row, col in game.get_empty_cells():
            # Create a copy to test the move
            test_game = game.copy()
            test_game.board[row][col] = player
            
            if test_game.check_winner() == player:
                return (row, col)
        
        return None
    
    def _find_blocking_move(self, game: TicTacToeGame) -> Optional[Tuple[int, int]]:
        """
        Find a move that blocks the human player from winning.
        
        Args:
            game: Current game state
            
        Returns:
            Blocking move position or None if no blocking needed
        """
        return self._find_winning_move(game, self.human_player)
    
    def _minimax(self, game: TicTacToeGame, is_maximizing: bool, 
                 alpha: int = -1000, beta: int = 1000) -> Tuple[int, Optional[Tuple[int, int]]]:
        """
        Minimax algorithm with alpha-beta pruning for optimal move selection.
        
        Args:
            game: Current game state
            is_maximizing: True if maximizing player (AI), False if minimizing (human)
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            
        Returns:
            Tuple of (score, best_move)
        """
        # Check terminal states
        winner = game.check_winner()
        if winner == self.ai_player:
            return 10, None
        elif winner == self.human_player:
            return -10, None
        elif game.is_board_full():
            return 0, None
        
        best_move = None
        empty_cells = game.get_empty_cells()
        
        if is_maximizing:
            # AI's turn (maximizing)
            max_eval = -1000
            
            for row, col in empty_cells:
                # Make move
                test_game = game.copy()
                test_game.board[row][col] = self.ai_player
                
                # Recursively evaluate
                eval_score, _ = self._minimax(test_game, False, alpha, beta)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (row, col)
                
                # Alpha-beta pruning
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        
        else:
            # Human's turn (minimizing)
            min_eval = 1000
            
            for row, col in empty_cells:
                # Make move
                test_game = game.copy()
                test_game.board[row][col] = self.human_player
                
                # Recursively evaluate
                eval_score, _ = self._minimax(test_game, True, alpha, beta)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (row, col)
                
                # Alpha-beta pruning
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            return min_eval, best_move
    
    def set_difficulty(self, difficulty: str) -> None:
        """
        Update AI difficulty level.
        
        Args:
            difficulty: New difficulty level ('easy', 'medium', 'hard')
            
        Raises:
            ValueError: If invalid difficulty level provided
        """
        difficulty = difficulty.lower()
        if difficulty not in ['easy', 'medium', 'hard']:
            raise ValueError(f"Invalid difficulty level: {difficulty}")
        
        self.difficulty = difficulty
    
    def get_difficulty(self) -> str:
        """
        Get current difficulty level.
        
        Returns:
            Current difficulty level
        """
        return self.difficulty


def get_ai_move(game: TicTacToeGame, difficulty: str = 'medium') -> Tuple[int, int]:
    """
    Convenience function to get AI move for a game.
    
    Args:
        game: Current game state
        difficulty: AI difficulty level
        
    Returns:
        Tuple of (row, col) for AI's move
    """
    ai = TicTacToeAI(difficulty)
    return ai.get_move(game)