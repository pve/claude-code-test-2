"""Game routes blueprint for tic-tac-toe functionality."""

from flask import Blueprint, request, jsonify, session
from app.models.tictactoe import TicTacToeGame
from app.utils.ai import get_ai_move
from app.utils.validation import validate_json_input
import logging

logger = logging.getLogger(__name__)

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


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
        # Get and validate JSON input
        try:
            raw_data = request.get_json()
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
        
        try:
            row = int(data['row'])
            col = int(data['col'])
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid move coordinates',
                'message': 'Row and col must be integers between 0 and 2'
            }), 400
        
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return jsonify({
                'error': 'Invalid move coordinates',
                'message': 'Row and col must be between 0 and 2'
            }), 400
        
        # Get current game
        game_data = session.get('game')
        if not game_data:
            return jsonify({
                'error': 'No active game',
                'message': 'Please start a new game first'
            }), 404
        
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
        # Get current game or create new one
        game_data = session.get('game')
        if game_data:
            game = TicTacToeGame.from_dict(game_data)
            current_difficulty = game.difficulty
        else:
            current_difficulty = 'medium'
        
        # Check for new difficulty
        try:
            raw_data = request.get_json()
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