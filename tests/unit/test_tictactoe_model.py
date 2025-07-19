"""Unit tests for TicTacToeGame model."""

import pytest
from app.models.tictactoe import TicTacToeGame


@pytest.mark.unit
def test_game_initialization():
    """Test TicTacToeGame initialization with default values."""
    game = TicTacToeGame()
    
    assert game.board == [['', '', ''], ['', '', ''], ['', '', '']]
    assert game.current_player == TicTacToeGame.PLAYER_X
    assert game.game_status == 'playing'
    assert game.difficulty == 'medium'
    assert game.winner is None
    assert game.winning_line is None


@pytest.mark.unit
def test_game_initialization_with_difficulty():
    """Test TicTacToeGame initialization with custom difficulty."""
    game = TicTacToeGame('hard')
    
    assert game.difficulty == 'hard'
    assert game.game_status == 'playing'


@pytest.mark.unit
def test_to_dict_conversion():
    """Test game state serialization to dictionary."""
    game = TicTacToeGame('easy')
    game.board[0][0] = 'X'
    game.current_player = 'O'
    
    game_dict = game.to_dict()
    
    expected = {
        'board': [['X', '', ''], ['', '', ''], ['', '', '']],
        'current_player': 'O',
        'game_status': 'playing',
        'difficulty': 'easy',
        'winner': None,
        'winning_line': None
    }
    
    assert game_dict == expected


@pytest.mark.unit
def test_from_dict_creation():
    """Test game state deserialization from dictionary."""
    game_data = {
        'board': [['X', 'O', ''], ['', 'X', ''], ['', '', 'O']],
        'current_player': 'X',
        'game_status': 'playing',
        'difficulty': 'hard',
        'winner': None,
        'winning_line': None
    }
    
    game = TicTacToeGame.from_dict(game_data)
    
    assert game.board == [['X', 'O', ''], ['', 'X', ''], ['', '', 'O']]
    assert game.current_player == 'X'
    assert game.game_status == 'playing'
    assert game.difficulty == 'hard'
    assert game.winner is None


@pytest.mark.unit
def test_from_dict_with_missing_fields():
    """Test game creation from incomplete dictionary data."""
    game_data = {'difficulty': 'easy'}
    
    game = TicTacToeGame.from_dict(game_data)
    
    assert game.board == [['', '', ''], ['', '', ''], ['', '', '']]
    assert game.current_player == TicTacToeGame.PLAYER_X
    assert game.game_status == 'playing'
    assert game.difficulty == 'easy'


@pytest.mark.unit
def test_is_valid_move_success():
    """Test valid move validation."""
    game = TicTacToeGame()
    
    assert game.is_valid_move(0, 0) is True
    assert game.is_valid_move(1, 1) is True
    assert game.is_valid_move(2, 2) is True


@pytest.mark.unit
def test_is_valid_move_out_of_bounds():
    """Test move validation for out-of-bounds coordinates."""
    game = TicTacToeGame()
    
    assert game.is_valid_move(-1, 0) is False
    assert game.is_valid_move(0, -1) is False
    assert game.is_valid_move(3, 0) is False
    assert game.is_valid_move(0, 3) is False
    assert game.is_valid_move(5, 5) is False


@pytest.mark.unit
def test_is_valid_move_occupied_cell():
    """Test move validation for occupied cells."""
    game = TicTacToeGame()
    game.board[1][1] = 'X'
    
    assert game.is_valid_move(1, 1) is False
    assert game.is_valid_move(0, 0) is True


@pytest.mark.unit
def test_is_valid_move_game_finished():
    """Test move validation when game is finished."""
    game = TicTacToeGame()
    game.game_status = 'won'
    
    assert game.is_valid_move(0, 0) is False


@pytest.mark.unit
def test_make_move_success():
    """Test successful move execution."""
    game = TicTacToeGame()
    
    result = game.make_move(1, 1, 'X')
    
    assert result is True
    assert game.board[1][1] == 'X'
    assert game.current_player == 'O'


@pytest.mark.unit
def test_make_move_invalid_position():
    """Test move execution with invalid position."""
    game = TicTacToeGame()
    
    result = game.make_move(3, 3, 'X')
    
    assert result is False
    assert game.board == [['', '', ''], ['', '', ''], ['', '', '']]
    assert game.current_player == 'X'


@pytest.mark.unit
def test_make_move_wrong_player():
    """Test move execution with wrong player."""
    game = TicTacToeGame()
    
    result = game.make_move(0, 0, 'O')  # Should be X's turn
    
    assert result is False
    assert game.board[0][0] == ''
    assert game.current_player == 'X'


@pytest.mark.unit
def test_make_move_occupied_cell():
    """Test move execution on occupied cell."""
    game = TicTacToeGame()
    game.board[1][1] = 'X'
    
    result = game.make_move(1, 1, 'O')
    
    assert result is False
    assert game.board[1][1] == 'X'


@pytest.mark.unit
def test_check_winner_row():
    """Test win detection for rows."""
    game = TicTacToeGame()
    
    # Test first row win
    game.board = [['X', 'X', 'X'], ['', '', ''], ['', '', '']]
    winner = game.check_winner()
    
    assert winner == 'X'
    assert game.winning_line == [(0, 0), (0, 1), (0, 2)]


@pytest.mark.unit
def test_check_winner_column():
    """Test win detection for columns."""
    game = TicTacToeGame()
    
    # Test first column win
    game.board = [['O', '', ''], ['O', '', ''], ['O', '', '']]
    winner = game.check_winner()
    
    assert winner == 'O'
    assert game.winning_line == [(0, 0), (1, 0), (2, 0)]


@pytest.mark.unit
def test_check_winner_diagonal_main():
    """Test win detection for main diagonal."""
    game = TicTacToeGame()
    
    # Test main diagonal win
    game.board = [['X', '', ''], ['', 'X', ''], ['', '', 'X']]
    winner = game.check_winner()
    
    assert winner == 'X'
    assert game.winning_line == [(0, 0), (1, 1), (2, 2)]


@pytest.mark.unit
def test_check_winner_diagonal_anti():
    """Test win detection for anti-diagonal."""
    game = TicTacToeGame()
    
    # Test anti-diagonal win
    game.board = [['', '', 'O'], ['', 'O', ''], ['O', '', '']]
    winner = game.check_winner()
    
    assert winner == 'O'
    assert game.winning_line == [(0, 2), (1, 1), (2, 0)]


@pytest.mark.unit
def test_check_winner_no_winner():
    """Test win detection when there's no winner."""
    game = TicTacToeGame()
    
    # Board with no winner
    game.board = [['X', 'O', 'X'], ['O', 'X', 'O'], ['', '', '']]
    winner = game.check_winner()
    
    assert winner is None
    assert game.winning_line is None


@pytest.mark.unit
def test_is_board_full_empty():
    """Test board full detection on empty board."""
    game = TicTacToeGame()
    
    assert game.is_board_full() is False


@pytest.mark.unit
def test_is_board_full_partial():
    """Test board full detection on partially filled board."""
    game = TicTacToeGame()
    game.board = [['X', 'O', ''], ['', 'X', ''], ['', '', '']]
    
    assert game.is_board_full() is False


@pytest.mark.unit
def test_is_board_full_complete():
    """Test board full detection on completely filled board."""
    game = TicTacToeGame()
    game.board = [['X', 'O', 'X'], ['O', 'X', 'O'], ['O', 'X', 'O']]
    
    assert game.is_board_full() is True


@pytest.mark.unit
def test_get_empty_cells():
    """Test getting list of empty cell coordinates."""
    game = TicTacToeGame()
    game.board = [['X', '', 'O'], ['', 'X', ''], ['', '', '']]
    
    empty_cells = game.get_empty_cells()
    expected = [(0, 1), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
    
    assert empty_cells == expected


@pytest.mark.unit
def test_get_empty_cells_full_board():
    """Test getting empty cells on full board."""
    game = TicTacToeGame()
    game.board = [['X', 'O', 'X'], ['O', 'X', 'O'], ['O', 'X', 'O']]
    
    empty_cells = game.get_empty_cells()
    
    assert empty_cells == []


@pytest.mark.unit
def test_reset_game():
    """Test game reset functionality."""
    game = TicTacToeGame()
    
    # Set up modified game state
    game.board = [['X', 'O', ''], ['', 'X', ''], ['', '', '']]
    game.current_player = 'O'
    game.game_status = 'won'
    game.winner = 'X'
    game.winning_line = [(0, 0), (1, 1), (2, 2)]
    
    game.reset_game()
    
    assert game.board == [['', '', ''], ['', '', ''], ['', '', '']]
    assert game.current_player == 'X'
    assert game.game_status == 'playing'
    assert game.winner is None
    assert game.winning_line is None


@pytest.mark.unit
def test_reset_game_with_new_difficulty():
    """Test game reset with difficulty change."""
    game = TicTacToeGame('easy')
    game.board[0][0] = 'X'
    
    game.reset_game('hard')
    
    assert game.board == [['', '', ''], ['', '', ''], ['', '', '']]
    assert game.difficulty == 'hard'


@pytest.mark.unit
def test_get_game_state_message_playing_x():
    """Test game state message for X's turn."""
    game = TicTacToeGame()
    
    message = game.get_game_state_message()
    
    assert message == "Your turn - click a square to play"


@pytest.mark.unit
def test_get_game_state_message_playing_o():
    """Test game state message for O's turn."""
    game = TicTacToeGame()
    game.current_player = 'O'
    
    message = game.get_game_state_message()
    
    assert message == "Computer's turn..."


@pytest.mark.unit
def test_get_game_state_message_won():
    """Test game state message for player win."""
    game = TicTacToeGame()
    game.game_status = 'won'
    
    message = game.get_game_state_message()
    
    assert message == "You won! Congratulations!"


@pytest.mark.unit
def test_get_game_state_message_lost():
    """Test game state message for player loss."""
    game = TicTacToeGame()
    game.game_status = 'lost'
    
    message = game.get_game_state_message()
    
    assert message == "Computer won! Try again!"


@pytest.mark.unit
def test_get_game_state_message_draw():
    """Test game state message for draw."""
    game = TicTacToeGame()
    game.game_status = 'draw'
    
    message = game.get_game_state_message()
    
    assert message == "It's a draw! Good game!"


@pytest.mark.unit
def test_copy_game():
    """Test game state deep copy functionality."""
    game = TicTacToeGame('hard')
    game.board = [['X', 'O', ''], ['', 'X', ''], ['', '', '']]
    game.current_player = 'O'
    game.winning_line = [(0, 0), (1, 1)]
    
    copied_game = game.copy()
    
    # Verify copy has same state
    assert copied_game.board == game.board
    assert copied_game.current_player == game.current_player
    assert copied_game.difficulty == game.difficulty
    assert copied_game.winning_line == game.winning_line
    
    # Verify it's a deep copy (modifying copy doesn't affect original)
    copied_game.board[0][0] = 'O'
    copied_game.winning_line.append((2, 2))
    
    assert game.board[0][0] == 'X'
    assert len(game.winning_line) == 2


@pytest.mark.unit
def test_complete_game_flow_x_wins():
    """Test complete game flow with X winning."""
    game = TicTacToeGame()
    
    # X wins with top row
    moves = [
        (0, 0, 'X'), (1, 0, 'O'),  # X: (0,0), O: (1,0)
        (0, 1, 'X'), (1, 1, 'O'),  # X: (0,1), O: (1,1)
        (0, 2, 'X')                # X: (0,2) - wins!
    ]
    
    for i, (row, col, player) in enumerate(moves):
        result = game.make_move(row, col, player)
        assert result is True
        
        if i == len(moves) - 1:  # Last move should trigger win
            assert game.game_status == 'won'
            assert game.winner == 'X'
            assert game.winning_line == [(0, 0), (0, 1), (0, 2)]


@pytest.mark.unit
def test_complete_game_flow_draw():
    """Test complete game flow resulting in draw."""
    game = TicTacToeGame()
    
    # Moves that result in a draw - carefully arranged to avoid wins
    # Final board: X O X
    #              O O X  
    #              X X O
    moves = [
        (0, 0), (0, 1), (0, 2),  # X O X
        (1, 0), (2, 0), (1, 1),  # O X O
        (2, 1), (2, 2), (1, 2)   # X O X
    ]
    
    for i, (row, col) in enumerate(moves):
        # Make the move with current player
        current_player = game.current_player
        result = game.make_move(row, col, current_player)
        assert result is True
        
        if i == len(moves) - 1:  # Last move should trigger draw
            assert game.game_status == 'draw'
            assert game.winner is None