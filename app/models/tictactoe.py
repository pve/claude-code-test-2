"""Tic-tac-toe game model with core game logic."""

from typing import List, Optional, Tuple, Dict, Any


class TicTacToeGame:
    """
    A tic-tac-toe game model that manages game state and logic.
    
    This class handles the core game mechanics including move validation,
    win detection, and board state management. It follows the session-based
    architecture pattern to avoid global state.
    """
    
    EMPTY = ''
    PLAYER_X = 'X'
    PLAYER_O = 'O'
    
    def __init__(self, difficulty: str = 'medium'):
        """
        Initialize a new tic-tac-toe game.
        
        Args:
            difficulty: AI difficulty level ('easy', 'medium', 'hard')
        """
        self.board: List[List[str]] = [['', '', ''], ['', '', ''], ['', '', '']]
        self.current_player: str = self.PLAYER_X  # Human player starts
        self.game_status: str = 'playing'  # 'playing', 'won', 'lost', 'draw'
        self.difficulty: str = difficulty
        self.winner: Optional[str] = None
        self.winning_line: Optional[List[Tuple[int, int]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert game state to dictionary for session storage.
        
        Returns:
            Dictionary representation of game state
        """
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_status': self.game_status,
            'difficulty': self.difficulty,
            'winner': self.winner,
            'winning_line': self.winning_line
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TicTacToeGame':
        """
        Create game instance from dictionary data.
        
        Args:
            data: Dictionary containing game state
            
        Returns:
            TicTacToeGame instance
        """
        game = cls(data.get('difficulty', 'medium'))
        game.board = data.get('board', [['', '', ''], ['', '', ''], ['', '', '']])
        game.current_player = data.get('current_player', cls.PLAYER_X)
        game.game_status = data.get('game_status', 'playing')
        game.winner = data.get('winner')
        game.winning_line = data.get('winning_line')
        return game
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """
        Check if a move is valid.
        
        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            
        Returns:
            True if move is valid, False otherwise
        """
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return False
        
        if self.board[row][col] != self.EMPTY:
            return False
        
        if self.game_status != 'playing':
            return False
        
        return True
    
    def make_move(self, row: int, col: int, player: str) -> bool:
        """
        Execute a move on the board.
        
        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            player: Player making the move ('X' or 'O')
            
        Returns:
            True if move was successful, False otherwise
        """
        if not self.is_valid_move(row, col):
            return False
        
        if player != self.current_player:
            return False
        
        self.board[row][col] = player
        
        # Check for win/draw after move
        winner = self.check_winner()
        if winner:
            self.game_status = 'won' if winner == self.PLAYER_X else 'lost'
            self.winner = winner
        elif self.is_board_full():
            self.game_status = 'draw'
        else:
            # Switch to next player
            self.current_player = self.PLAYER_O if player == self.PLAYER_X else self.PLAYER_X
        
        return True
    
    def check_winner(self) -> Optional[str]:
        """
        Check if there's a winner on the current board.
        
        Returns:
            Winner player ('X' or 'O') or None if no winner
        """
        # Check rows
        for i in range(3):
            if (self.board[i][0] == self.board[i][1] == self.board[i][2] != self.EMPTY):
                self.winning_line = [(i, 0), (i, 1), (i, 2)]
                return self.board[i][0]
        
        # Check columns
        for j in range(3):
            if (self.board[0][j] == self.board[1][j] == self.board[2][j] != self.EMPTY):
                self.winning_line = [(0, j), (1, j), (2, j)]
                return self.board[0][j]
        
        # Check diagonals
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] != self.EMPTY):
            self.winning_line = [(0, 0), (1, 1), (2, 2)]
            return self.board[0][0]
        
        if (self.board[0][2] == self.board[1][1] == self.board[2][0] != self.EMPTY):
            self.winning_line = [(0, 2), (1, 1), (2, 0)]
            return self.board[0][2]
        
        return None
    
    def is_board_full(self) -> bool:
        """
        Check if the board is completely filled.
        
        Returns:
            True if board is full, False otherwise
        """
        for row in self.board:
            for cell in row:
                if cell == self.EMPTY:
                    return False
        return True
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """
        Get list of empty cell coordinates.
        
        Returns:
            List of (row, col) tuples for empty cells
        """
        empty_cells = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == self.EMPTY:
                    empty_cells.append((i, j))
        return empty_cells
    
    def reset_game(self, difficulty: Optional[str] = None) -> None:
        """
        Reset the game to initial state.
        
        Args:
            difficulty: Optional new difficulty level
        """
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.current_player = self.PLAYER_X
        self.game_status = 'playing'
        self.winner = None
        self.winning_line = None
        
        if difficulty:
            self.difficulty = difficulty
    
    def get_game_state_message(self) -> str:
        """
        Get human-readable game state message.
        
        Returns:
            String describing current game state
        """
        if self.game_status == 'won':
            return "You won! Congratulations!"
        elif self.game_status == 'lost':
            return "Computer won! Try again!"
        elif self.game_status == 'draw':
            return "It's a draw! Good game!"
        elif self.current_player == self.PLAYER_X:
            return "Your turn - click a square to play"
        else:
            return "Computer's turn..."
    
    def copy(self) -> 'TicTacToeGame':
        """
        Create a deep copy of the current game state.
        
        Returns:
            New TicTacToeGame instance with identical state
        """
        new_game = TicTacToeGame(self.difficulty)
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        new_game.game_status = self.game_status
        new_game.winner = self.winner
        new_game.winning_line = self.winning_line[:] if self.winning_line else None
        return new_game