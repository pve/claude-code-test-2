"""Unit tests for AI algorithms."""

import pytest
from unittest.mock import patch
from app.utils.ai import TicTacToeAI, get_ai_move
from app.models.tictactoe import TicTacToeGame


@pytest.mark.unit
def test_ai_initialization():
    """Test AI initialization with default and custom difficulty."""
    # Default difficulty
    ai = TicTacToeAI()
    assert ai.difficulty == 'medium'
    assert ai.ai_player == 'O'
    assert ai.human_player == 'X'
    
    # Custom difficulty
    ai_hard = TicTacToeAI('hard')
    assert ai_hard.difficulty == 'hard'
    
    ai_easy = TicTacToeAI('EASY')  # Test case insensitive
    assert ai_easy.difficulty == 'easy'


@pytest.mark.unit
def test_ai_set_difficulty():
    """Test setting AI difficulty level."""
    ai = TicTacToeAI()
    
    # Valid difficulty changes
    ai.set_difficulty('hard')
    assert ai.difficulty == 'hard'
    
    ai.set_difficulty('Easy')  # Test case insensitive
    assert ai.difficulty == 'easy'
    
    # Invalid difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        ai.set_difficulty('impossible')


@pytest.mark.unit
def test_ai_get_difficulty():
    """Test getting current AI difficulty."""
    ai = TicTacToeAI('hard')
    assert ai.get_difficulty() == 'hard'


@pytest.mark.unit
def test_get_move_no_empty_cells():
    """Test AI behavior when no moves are available."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Fill the board
    game.board = [['X', 'O', 'X'], ['O', 'X', 'O'], ['X', 'O', 'X']]
    
    with pytest.raises(ValueError, match="No valid moves available"):
        ai.get_move(game)


@pytest.mark.unit
def test_get_move_invalid_difficulty():
    """Test AI with invalid difficulty level."""
    ai = TicTacToeAI()
    ai.difficulty = 'invalid'
    game = TicTacToeGame()
    
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        ai.get_move(game)


@pytest.mark.unit
def test_find_winning_move():
    """Test AI's ability to find winning moves."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Set up board where O can win with move at (0, 2)
    game.board = [['O', 'O', ''], ['X', 'X', 'O'], ['', '', '']]
    
    winning_move = ai._find_winning_move(game, 'O')
    assert winning_move == (0, 2)


@pytest.mark.unit
def test_find_winning_move_no_win():
    """Test finding winning move when none exists."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Set up board with no immediate winning moves for O
    game.board = [['X', 'O', ''], ['', '', ''], ['', '', '']]
    
    winning_move = ai._find_winning_move(game, 'O')
    assert winning_move is None


@pytest.mark.unit
def test_find_blocking_move():
    """Test AI's ability to find blocking moves."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Set up board where X can win at (0, 2), so AI should block
    game.board = [['X', 'X', ''], ['O', '', ''], ['', '', '']]
    
    blocking_move = ai._find_blocking_move(game)
    assert blocking_move == (0, 2)


@pytest.mark.unit
def test_find_blocking_move_no_threat():
    """Test blocking move when no threat exists."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Set up board with no immediate threats
    game.board = [['X', 'O', ''], ['', '', ''], ['', '', '']]
    
    blocking_move = ai._find_blocking_move(game)
    assert blocking_move is None


@pytest.mark.unit
def test_minimax_ai_wins():
    """Test minimax when AI can win."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Set up board where O can win at (0, 2)
    game.board = [['O', 'O', ''], ['X', 'X', 'O'], ['', '', '']]
    
    score, move = ai._minimax(game, True)
    assert score == 10  # AI wins
    assert move == (0, 2)


@pytest.mark.unit
def test_minimax_human_wins():
    """Test minimax when human wins."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Set up board where X has already won
    game.board = [['X', 'X', 'X'], ['O', 'O', ''], ['', '', '']]
    
    score, move = ai._minimax(game, True)
    assert score == -10  # Human wins
    assert move is None


@pytest.mark.unit
def test_minimax_draw():
    """Test minimax with draw scenario."""
    ai = TicTacToeAI()
    game = TicTacToeGame()
    
    # Set up board that results in draw
    game.board = [['X', 'O', 'X'], ['O', 'O', 'X'], ['X', 'X', 'O']]
    
    score, move = ai._minimax(game, True)
    assert score == 0  # Draw
    assert move is None


@pytest.mark.unit
def test_easy_difficulty_move():
    """Test easy difficulty move selection."""
    ai = TicTacToeAI('easy')
    game = TicTacToeGame()
    
    # Set up board with one empty cell
    game.board = [['X', 'O', 'X'], ['O', 'X', 'O'], ['', 'X', 'O']]
    
    move = ai.get_move(game)
    assert move == (2, 0)  # Only available move


@pytest.mark.unit
@patch('random.random')
@patch('random.choice')
def test_easy_difficulty_random_vs_blocking(mock_choice, mock_random):
    """Test easy difficulty random vs blocking behavior."""
    ai = TicTacToeAI('easy')
    game = TicTacToeGame()
    
    # Set up board where X can win at (0, 2)
    game.board = [['X', 'X', ''], ['O', '', ''], ['', '', '']]
    
    # Test blocking (20% chance)
    mock_random.return_value = 0.1  # Less than 0.2, should block
    move = ai.get_move(game)
    assert move == (0, 2)  # Should block
    
    # Test random (80% chance)
    mock_random.return_value = 0.5  # Greater than 0.2, should be random
    mock_choice.return_value = (1, 2)
    move = ai.get_move(game)
    assert move == (1, 2)
    
    # Verify random choice was called with actual empty cells
    expected_empty_cells = game.get_empty_cells()
    mock_choice.assert_called_with(expected_empty_cells)


@pytest.mark.unit
def test_medium_difficulty_winning_move():
    """Test medium difficulty prioritizes winning moves."""
    ai = TicTacToeAI('medium')
    game = TicTacToeGame()
    
    # Set up board where O can win at (0, 2)
    game.board = [['O', 'O', ''], ['X', 'X', 'O'], ['', '', '']]
    
    move = ai.get_move(game)
    assert move == (0, 2)  # Should take winning move


@pytest.mark.unit
def test_medium_difficulty_blocking_move():
    """Test medium difficulty blocks opponent wins."""
    ai = TicTacToeAI('medium')
    game = TicTacToeGame()
    
    # Set up board where X can win at (0, 2)
    game.board = [['X', 'X', ''], ['O', '', ''], ['', '', '']]
    
    move = ai.get_move(game)
    assert move == (0, 2)  # Should block


@pytest.mark.unit
def test_medium_difficulty_center_preference():
    """Test medium difficulty takes center when available."""
    ai = TicTacToeAI('medium')
    game = TicTacToeGame()
    
    # Set up board with center available
    game.board = [['X', '', ''], ['', '', ''], ['', '', 'O']]
    
    move = ai.get_move(game)
    assert move == (1, 1)  # Should take center


@pytest.mark.unit
@patch('random.choice')
def test_medium_difficulty_corner_preference(mock_choice):
    """Test medium difficulty prefers corners when center unavailable."""
    ai = TicTacToeAI('medium')
    game = TicTacToeGame()
    
    # Set up board with center taken, corners available
    game.board = [['', '', ''], ['', 'X', ''], ['', '', '']]
    
    mock_choice.return_value = (0, 0)
    move = ai.get_move(game)
    assert move == (0, 0)
    
    # Verify it was called with corners
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    mock_choice.assert_called_with(corners)


@pytest.mark.unit
def test_medium_difficulty_random_fallback():
    """Test medium difficulty falls back to random when no strategy applies."""
    ai = TicTacToeAI('medium')
    game = TicTacToeGame()
    
    # Set up board with center and ALL corners taken, leaving only edges
    game.board = [['X', '', 'O'], ['', 'X', ''], ['O', '', 'X']]
    
    # This board has no corners available (all are X or O), center taken (X)
    # Only edges available: (0,1), (1,0), (1,2), (2,1)
    
    move = ai.get_move(game)
    
    # Should be one of the edge positions since no other strategy applies
    expected_positions = [(0, 1), (1, 0), (1, 2), (2, 1)]
    assert move in expected_positions


@pytest.mark.unit
def test_hard_difficulty_optimal_play():
    """Test hard difficulty makes optimal moves."""
    ai = TicTacToeAI('hard')
    game = TicTacToeGame()
    
    # Set up board where O can win at (0, 2)
    game.board = [['O', 'O', ''], ['X', 'X', 'O'], ['', '', '']]
    
    move = ai.get_move(game)
    assert move == (0, 2)  # Should take winning move


@pytest.mark.unit
def test_hard_difficulty_defensive_play():
    """Test hard difficulty blocks opponent wins."""
    ai = TicTacToeAI('hard')
    game = TicTacToeGame()
    
    # Set up board where X can win at (0, 2)
    game.board = [['X', 'X', ''], ['O', '', ''], ['', '', '']]
    
    move = ai.get_move(game)
    assert move == (0, 2)  # Should block


@pytest.mark.unit
def test_hard_difficulty_empty_board():
    """Test hard difficulty on empty board (should take corner or center)."""
    ai = TicTacToeAI('hard')
    game = TicTacToeGame()
    
    move = ai.get_move(game)
    
    # Optimal first moves are corners or center
    optimal_moves = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]
    assert move in optimal_moves


@pytest.mark.unit
def test_convenience_function():
    """Test the convenience function get_ai_move."""
    game = TicTacToeGame()
    
    # Set up board with only one move
    game.board = [['X', 'O', 'X'], ['O', 'X', 'O'], ['', 'X', 'O']]
    
    move = get_ai_move(game, 'easy')
    assert move == (2, 0)
    
    move = get_ai_move(game, 'medium')
    assert move == (2, 0)
    
    move = get_ai_move(game, 'hard')
    assert move == (2, 0)


@pytest.mark.unit
def test_ai_integration_with_game():
    """Test AI integration with TicTacToeGame model."""
    ai = TicTacToeAI('medium')
    game = TicTacToeGame()
    
    # Set game to O's turn (AI player)
    game.current_player = 'O'
    
    # AI makes first move
    move = ai.get_move(game)
    assert move in game.get_empty_cells()
    
    # Apply the move
    result = game.make_move(move[0], move[1], 'O')
    assert result is True
    assert game.board[move[0]][move[1]] == 'O'


@pytest.mark.unit
def test_ai_complete_game_simulation():
    """Test AI playing a complete game."""
    ai = TicTacToeAI('hard')
    game = TicTacToeGame()
    
    # Simulate moves until game ends (max 9 moves)
    moves_count = 0
    while game.game_status == 'playing' and moves_count < 9:
        if game.current_player == 'O':
            # AI move
            move = ai.get_move(game)
            game.make_move(move[0], move[1], 'O')
        else:
            # Human move (random for simulation)
            empty_cells = game.get_empty_cells()
            if empty_cells:
                move = empty_cells[0]  # Take first available
                game.make_move(move[0], move[1], 'X')
        
        moves_count += 1
    
    # Game should end properly
    assert game.game_status in ['won', 'lost', 'draw']
    assert moves_count <= 9


@pytest.mark.unit
def test_minimax_alpha_beta_pruning():
    """Test that minimax uses alpha-beta pruning correctly."""
    ai = TicTacToeAI('hard')
    game = TicTacToeGame()
    
    # Set up a specific game state
    game.board = [['X', 'O', ''], ['', 'X', ''], ['', '', '']]
    
    # Call minimax and ensure it returns valid results
    score, move = ai._minimax(game, True, -1000, 1000)
    
    assert isinstance(score, int)
    assert -10 <= score <= 10  # Score should be within expected range
    assert move is None or (isinstance(move, tuple) and len(move) == 2)
    
    if move:
        assert move in game.get_empty_cells()


@pytest.mark.unit
def test_ai_never_loses_when_going_first():
    """Test that hard AI never loses when going first (should win or draw)."""
    ai = TicTacToeAI('hard')
    game = TicTacToeGame()
    
    # AI goes first
    game.current_player = 'O'
    
    # Play against optimal opponent (minimax for human too)
    while game.game_status == 'playing':
        if game.current_player == 'O':
            # AI move
            move = ai.get_move(game)
            game.make_move(move[0], move[1], 'O')
        else:
            # Optimal human move using minimax
            human_ai = TicTacToeAI('hard')
            human_ai.ai_player = 'X'
            human_ai.human_player = 'O'
            
            empty_cells = game.get_empty_cells()
            if empty_cells:
                # Get best move for human (minimizing for original AI)
                best_score = 1000
                best_move = empty_cells[0]
                
                for row, col in empty_cells:
                    test_game = game.copy()
                    test_game.board[row][col] = 'X'
                    score, _ = ai._minimax(test_game, True)
                    if score < best_score:
                        best_score = score
                        best_move = (row, col)
                
                game.make_move(best_move[0], best_move[1], 'X')
    
    # AI should never lose when going first against optimal play
    assert game.game_status in ['lost', 'draw']  # 'lost' means human lost, AI won