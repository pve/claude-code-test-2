"""Game routes blueprint for tic-tac-toe functionality."""

from flask import Blueprint, request, jsonify, session
from app.models.tictactoe import TicTacToeGame
from app.utils.ai import get_ai_move
from app.utils.validation import validate_json_input
import logging

logger = logging.getLogger(__name__)

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


def _check_json_depth(data, max_depth=10, current_depth=0):
    """
    Check JSON nesting depth to prevent JSON bombs.
    
    Args:
        data: JSON data to check
        max_depth: Maximum allowed depth
        current_depth: Current nesting level
        
    Returns:
        int: Maximum depth found
    """
    if current_depth > max_depth:
        return current_depth
    
    if isinstance(data, dict):
        if not data:  # Empty dict
            return current_depth
        return max(_check_json_depth(value, max_depth, current_depth + 1) 
                  for value in data.values())
    elif isinstance(data, list):
        if not data:  # Empty list
            return current_depth
        return max(_check_json_depth(item, max_depth, current_depth + 1) 
                  for item in data)
    else:
        return current_depth


def _validate_coordinates(row, col):
    """
    Validate and sanitize game coordinates with overflow protection.
    
    Args:
        row: Row coordinate
        col: Column coordinate
        
    Returns:
        tuple: (row, col) as integers
        
    Raises:
        ValueError: If coordinates are invalid
    """
    try:
        # Handle potential overflow/infinity values
        if isinstance(row, float):
            if not (-2**31 <= row <= 2**31-1):
                raise ValueError("Row coordinate out of valid range")
        if isinstance(col, float):
            if not (-2**31 <= col <= 2**31-1):
                raise ValueError("Column coordinate out of valid range")
            
        row = int(row)
        col = int(col)
        
        # Validate range (0-2 for tic-tac-toe)
        if not (0 <= row <= 2) or not (0 <= col <= 2):
            raise ValueError("Coordinates must be between 0 and 2")
            
    except (ValueError, TypeError, OverflowError) as e:
        raise ValueError(f"Invalid coordinates: {str(e)}")
    
    return row, col


def _validate_session_game_data(game_data):
    """
    Validate session game data for integrity.
    
    Args:
        game_data: Game data from session
        
    Returns:
        bool: True if data is valid
    """
    if not isinstance(game_data, dict):
        return False
    
    # Check required fields
    required_fields = ['board', 'current_player', 'game_status', 'difficulty']
    if not all(field in game_data for field in required_fields):
        return False
    
    # Validate current_player
    if game_data['current_player'] not in ['X', 'O']:
        return False
    
    # Validate game_status
    valid_statuses = ['playing', 'won', 'draw', 'quit']
    if game_data['game_status'] not in valid_statuses:
        return False
    
    # Validate difficulty
    if game_data['difficulty'] not in ['easy', 'medium', 'hard']:
        return False
    
    # Validate board structure
    board = game_data['board']
    if not isinstance(board, list) or len(board) != 3:
        return False
    
    for row in board:
        if not isinstance(row, list) or len(row) != 3:
            return False
        for cell in row:
            if cell not in ['', 'X', 'O']:
                return False
    
    return True


@game_bp.route('/new', methods=['POST'])
def new_game():
    """
    Start a new tic-tac-toe game.
    
    Expected JSON body:
    {
        "difficulty": "easy|medium|hard"  # optional, defaults to "medium"
    }
    
    Returns:
        JSON response with game state
    """
    try:
        # Get and validate JSON input with size limits
        try:
            # Check request size first
            if request.content_length and request.content_length > 1024:  # 1KB limit
                return jsonify({
                    'error': 'Request too large',
                    'message': 'Request body exceeds maximum size of 1KB'
                }), 413
            
            raw_data = request.get_json()
            
            # Protect against JSON bombs (deep nesting)
            if raw_data and _check_json_depth(raw_data) > 10:
                return jsonify({
                    'error': 'Invalid JSON structure',
                    'message': 'JSON nesting too deep (max 10 levels)'
                }), 400
                
        except Exception as e:
            return jsonify({
                'error': 'Invalid JSON',
                'message': 'Request body must be valid JSON'
            }), 400
            
        data = validate_json_input(raw_data or {})
        difficulty = data.get('difficulty', 'medium').lower()
        
        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({
                'error': 'Invalid difficulty level',
                'message': 'Difficulty must be one of: easy, medium, hard'
            }), 400
        
        # Create new game
        game = TicTacToeGame(difficulty)
        
        # Store in session
        session['game'] = game.to_dict()
        session.permanent = True
        
        logger.info(f"New game started with difficulty: {difficulty}")
        
        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'message': game.get_game_state_message()
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting new game: {str(e)}")
        return jsonify({
            'error': 'Failed to start new game',
            'message': 'An unexpected error occurred'
        }), 500


@game_bp.route('/state', methods=['GET'])
def get_game_state():
    """
    Get current game state.
    
    Returns:
        JSON response with current game state
    """
    try:
        game_data = session.get('game')
        
        if not game_data:
            return jsonify({
                'error': 'No active game',
                'message': 'Please start a new game first'
            }), 404
        
        # Validate session data integrity
        if not _validate_session_game_data(game_data):
            # Clear corrupted session data
            session.pop('game', None)
            return jsonify({
                'error': 'Invalid game data',
                'message': 'Game session corrupted. Please start a new game.'
            }), 400
        
        game = TicTacToeGame.from_dict(game_data)
        
        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'message': game.get_game_state_message()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting game state: {str(e)}")
        return jsonify({
            'error': 'Failed to get game state',
            'message': 'An unexpected error occurred'
        }), 500


@game_bp.route('/move', methods=['POST'])
def make_move():
    """
    Make a move in the current game.
    
    Expected JSON body:
    {
        "row": 0-2,
        "col": 0-2
    }
    
    Returns:
        JSON response with updated game state
    """
    try:
        # Get and validate JSON input
        try:
            raw_data = request.get_json()
        except Exception as e:
            return jsonify({
                'error': 'Invalid JSON',
                'message': 'Request body must be valid JSON'
            }), 400
            
        if raw_data is None:
            return jsonify({
                'error': 'Missing JSON body',
                'message': 'Request must include JSON body'
            }), 400
            
        data = validate_json_input(raw_data)
        
        if 'row' not in data or 'col' not in data:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Both row and col are required'
            }), 400
        
        # Validate coordinates with overflow protection
        try:
            row, col = _validate_coordinates(data['row'], data['col'])
        except ValueError as e:
            return jsonify({
                'error': 'Invalid move coordinates',
                'message': str(e)
            }), 400
        
        # Get current game with validation
        game_data = session.get('game')
        if not game_data:
            return jsonify({
                'error': 'No active game',
                'message': 'Please start a new game first'
            }), 404
        
        # Validate session data integrity
        if not _validate_session_game_data(game_data):
            # Clear corrupted session data
            session.pop('game', None)
            return jsonify({
                'error': 'Invalid game data',
                'message': 'Game session corrupted. Please start a new game.'
            }), 400
        
        game = TicTacToeGame.from_dict(game_data)
        
        # Check if it's human player's turn
        if game.current_player != TicTacToeGame.PLAYER_X:
            return jsonify({
                'error': 'Not your turn',
                'message': 'Wait for your turn to make a move'
            }), 400
        
        if game.game_status != 'playing':
            return jsonify({
                'error': 'Game not active',
                'message': f'Game is {game.game_status}. Start a new game to continue.'
            }), 400
        
        # Make human move
        success = game.make_move(row, col, TicTacToeGame.PLAYER_X)
        if not success:
            return jsonify({
                'error': 'Invalid move',
                'message': 'That position is already taken or move is not valid'
            }), 400
        
        logger.info(f"Human move: ({row}, {col})")
        
        # Check if game ended after human move
        if game.game_status != 'playing':
            session['game'] = game.to_dict()
            return jsonify({
                'success': True,
                'game': game.to_dict(),
                'message': game.get_game_state_message(),
                'game_over': True
            }), 200
        
        # Make AI move
        try:
            ai_move = get_ai_move(game, game.difficulty)
            ai_success = game.make_move(ai_move[0], ai_move[1], TicTacToeGame.PLAYER_O)
            
            if ai_success:
                logger.info(f"AI move: {ai_move}")
            else:
                logger.error(f"AI move failed: {ai_move}")
                
        except Exception as e:
            logger.error(f"AI move error: {str(e)}")
            # Continue without AI move if it fails
        
        # Update session
        session['game'] = game.to_dict()
        
        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'message': game.get_game_state_message(),
            'game_over': game.game_status != 'playing',
            'ai_move': ai_move if 'ai_move' in locals() else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error making move: {str(e)}")
        return jsonify({
            'error': 'Failed to make move',
            'message': 'An unexpected error occurred'
        }), 500


@game_bp.route('/reset', methods=['POST'])
def reset_game():
    """
    Reset the current game to initial state.
    
    Optional JSON body:
    {
        "difficulty": "easy|medium|hard"  # optional, keeps current if not provided
    }
    
    Returns:
        JSON response with reset game state
    """
    try:
        # Get current game or create new one with validation
        game_data = session.get('game')
        if game_data:
            # Validate session data integrity
            if not _validate_session_game_data(game_data):
                # Clear corrupted session data and use default
                session.pop('game', None)
                current_difficulty = 'medium'
            else:
                game = TicTacToeGame.from_dict(game_data)
                current_difficulty = game.difficulty
        else:
            current_difficulty = 'medium'
        
        # Check for new difficulty with JSON bomb protection
        try:
            # Check request size first
            if request.content_length and request.content_length > 1024:  # 1KB limit
                return jsonify({
                    'error': 'Request too large',
                    'message': 'Request body exceeds maximum size of 1KB'
                }), 413
            
            raw_data = request.get_json()
            
            # Protect against JSON bombs (deep nesting)
            if raw_data and _check_json_depth(raw_data) > 10:
                return jsonify({
                    'error': 'Invalid JSON structure',
                    'message': 'JSON nesting too deep (max 10 levels)'
                }), 400
                
        except Exception as e:
            return jsonify({
                'error': 'Invalid JSON',
                'message': 'Request body must be valid JSON'
            }), 400
            
        data = validate_json_input(raw_data or {})
        new_difficulty = data.get('difficulty', current_difficulty).lower()
        
        if new_difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({
                'error': 'Invalid difficulty level',
                'message': 'Difficulty must be one of: easy, medium, hard'
            }), 400
        
        # Reset or create game
        if game_data:
            game = TicTacToeGame.from_dict(game_data)
            game.reset_game(new_difficulty)
        else:
            game = TicTacToeGame(new_difficulty)
        
        # Update session
        session['game'] = game.to_dict()
        
        logger.info(f"Game reset with difficulty: {new_difficulty}")
        
        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'message': game.get_game_state_message()
        }), 200
        
    except Exception as e:
        logger.error(f"Error resetting game: {str(e)}")
        return jsonify({
            'error': 'Failed to reset game',
            'message': 'An unexpected error occurred'
        }), 500


@game_bp.route('/quit', methods=['POST'])
def quit_game():
    """
    End current game and clear session.
    
    Returns:
        JSON response confirming game ended
    """
    try:
        if 'game' in session:
            del session['game']
            logger.info("Game ended and session cleared")
        
        return jsonify({
            'success': True,
            'message': 'Game ended successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error quitting game: {str(e)}")
        return jsonify({
            'error': 'Failed to quit game',
            'message': 'An unexpected error occurred'
        }), 500


@game_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors for game routes."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested game endpoint does not exist'
    }), 404


@game_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors for game routes."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405


@game_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors for game routes."""
    logger.error(f"Internal server error in game routes: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500