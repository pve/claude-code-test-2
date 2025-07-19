/**
 * Tic-Tac-Toe Game Frontend
 * Handles user interactions and communicates with the Flask API
 */

class TicTacToeGame {
    constructor() {
        this.gameState = null;
        this.isGameActive = false;
        this.moveHistory = [];
        
        this.initializeElements();
        this.bindEvents();
        this.showMessage('Welcome! Start a new game to begin.');
    }

    initializeElements() {
        // Game controls
        this.difficultySelect = document.getElementById('difficulty');
        this.newGameBtn = document.getElementById('new-game-btn');
        this.resetGameBtn = document.getElementById('reset-game-btn');
        this.quitGameBtn = document.getElementById('quit-game-btn');
        
        // Game display
        this.gameBoard = document.getElementById('game-board');
        this.gameMessage = document.getElementById('game-message');
        this.moveHistoryList = document.getElementById('move-history');
        
        // Overlays and modals
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorModal = document.getElementById('error-modal');
        this.errorMessage = document.getElementById('error-message');
        this.closeModal = document.querySelector('.close');
        
        // Get all cells
        this.cells = Array.from(document.querySelectorAll('.cell'));
    }

    bindEvents() {
        // Button events
        this.newGameBtn.addEventListener('click', () => this.startNewGame());
        this.resetGameBtn.addEventListener('click', () => this.resetGame());
        this.quitGameBtn.addEventListener('click', () => this.quitGame());
        
        // Cell click events
        this.cells.forEach(cell => {
            cell.addEventListener('click', (e) => this.handleCellClick(e));
        });
        
        // Modal events
        this.closeModal.addEventListener('click', () => this.hideError());
        this.errorModal.addEventListener('click', (e) => {
            if (e.target === this.errorModal) this.hideError();
        });
        
        // Keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.hideError();
        });
    }

    async startNewGame() {
        try {
            this.showLoading();
            const difficulty = this.difficultySelect.value;
            
            const response = await this.makeAPICall('/api/game/new', 'POST', {
                difficulty: difficulty
            });
            
            if (response.success) {
                this.gameState = response.game;
                this.isGameActive = true;
                this.moveHistory = [];
                this.updateGameDisplay();
                this.showMessage('Game started! Make your move.');
                this.updateButtons();
            } else {
                this.showError(response.message || 'Failed to start new game');
            }
        } catch (error) {
            this.showError('Failed to start new game: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async resetGame() {
        try {
            this.showLoading();
            const difficulty = this.difficultySelect.value;
            
            const response = await this.makeAPICall('/api/game/reset', 'POST', {
                difficulty: difficulty
            });
            
            if (response.success) {
                this.gameState = response.game;
                this.isGameActive = true;
                this.moveHistory = [];
                this.updateGameDisplay();
                this.showMessage('Game reset! Make your move.');
                this.updateButtons();
            } else {
                this.showError(response.message || 'Failed to reset game');
            }
        } catch (error) {
            this.showError('Failed to reset game: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async quitGame() {
        try {
            this.showLoading();
            
            const response = await this.makeAPICall('/api/game/quit', 'POST');
            
            if (response.success) {
                this.gameState = null;
                this.isGameActive = false;
                this.moveHistory = [];
                this.clearBoard();
                this.showMessage('Game ended. Start a new game to play again.');
                this.updateButtons();
                this.updateMoveHistory();
            } else {
                this.showError(response.message || 'Failed to quit game');
            }
        } catch (error) {
            this.showError('Failed to quit game: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async handleCellClick(event) {
        if (!this.isGameActive) {
            this.showError('No active game. Please start a new game first.');
            return;
        }

        const cell = event.target;
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);

        // Check if cell is already occupied
        if (cell.textContent) {
            this.showError('This position is already taken!');
            return;
        }

        // Check if it's player's turn
        if (this.gameState && this.gameState.current_player !== 'X') {
            this.showError('Please wait for your turn!');
            return;
        }

        try {
            this.showLoading();
            
            const response = await this.makeAPICall('/api/game/move', 'POST', {
                row: row,
                col: col
            });
            
            if (response.success) {
                this.gameState = response.game;
                this.updateGameDisplay();
                
                // Add move to history
                this.addMoveToHistory(`You: (${row + 1}, ${col + 1})`, false);
                
                if (response.ai_move) {
                    const [aiRow, aiCol] = response.ai_move;
                    this.addMoveToHistory(`AI: (${aiRow + 1}, ${aiCol + 1})`, true);
                }
                
                // Check if game ended
                if (response.game_over) {
                    this.isGameActive = false;
                    this.handleGameEnd();
                } else {
                    this.showMessage('AI made a move. Your turn!');
                }
                
                this.updateButtons();
            } else {
                this.showError(response.message || 'Invalid move');
            }
        } catch (error) {
            this.showError('Failed to make move: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async makeAPICall(endpoint, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    updateGameDisplay() {
        if (!this.gameState) return;

        // Clear previous styling
        this.cells.forEach(cell => {
            cell.classList.remove('player-x', 'player-o', 'winning', 'last-move');
        });

        // Update board
        this.gameState.board.forEach((row, rowIndex) => {
            row.forEach((cell, colIndex) => {
                const cellElement = this.getCellElement(rowIndex, colIndex);
                cellElement.textContent = cell || '';
                
                if (cell === 'X') {
                    cellElement.classList.add('player-x');
                } else if (cell === 'O') {
                    cellElement.classList.add('player-o');
                }
            });
        });

        // Highlight winning cells if game is won
        if (this.gameState.game_status === 'won' && this.gameState.winning_line) {
            this.gameState.winning_line.forEach(([row, col]) => {
                const cellElement = this.getCellElement(row, col);
                cellElement.classList.add('winning');
            });
        }

        // Update game message based on state
        this.updateGameMessage();
    }

    updateGameMessage() {
        if (!this.gameState) return;

        const status = this.gameState.game_status;
        const currentPlayer = this.gameState.current_player;
        
        this.gameMessage.className = 'message'; // Reset classes

        switch (status) {
            case 'playing':
                if (currentPlayer === 'X') {
                    this.showMessage('Your turn! Click a cell to make your move.');
                } else {
                    this.showMessage('AI is thinking...');
                }
                break;
            case 'won':
                if (this.gameState.winner === 'X') {
                    this.showMessage('🎉 Congratulations! You won!', 'success');
                } else {
                    this.showMessage('😔 AI won this round. Try again!', 'error');
                }
                break;
            case 'draw':
                this.showMessage('🤝 It\'s a draw! Good game!', 'warning');
                break;
            default:
                this.showMessage('Ready to play!');
        }
    }

    handleGameEnd() {
        this.isGameActive = false;
        
        // Disable all cells
        this.cells.forEach(cell => {
            cell.classList.add('disabled');
        });
        
        // Update buttons
        this.updateButtons();
        
        // Show game end animation after a short delay
        setTimeout(() => {
            this.showGameEndAnimation();
        }, 500);
    }

    showGameEndAnimation() {
        if (this.gameState.game_status === 'won' && this.gameState.winning_line) {
            // Animate winning line
            this.gameState.winning_line.forEach(([row, col], index) => {
                setTimeout(() => {
                    const cellElement = this.getCellElement(row, col);
                    cellElement.style.animation = 'winningCell 0.6s ease-in-out';
                }, index * 200);
            });
        }
    }

    getCellElement(row, col) {
        return document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    }

    addMoveToHistory(moveText, isAIMove) {
        this.moveHistory.push({ text: moveText, isAI: isAIMove });
        this.updateMoveHistory();
    }

    updateMoveHistory() {
        if (this.moveHistory.length === 0) {
            this.moveHistoryList.innerHTML = '<div class="no-moves">No moves yet</div>';
            return;
        }

        const historyHTML = this.moveHistory.map(move => 
            `<div class="move-item ${move.isAI ? 'ai-move' : ''}">${move.text}</div>`
        ).join('');
        
        this.moveHistoryList.innerHTML = historyHTML;
        this.moveHistoryList.scrollTop = this.moveHistoryList.scrollHeight;
    }

    clearBoard() {
        this.cells.forEach(cell => {
            cell.textContent = '';
            cell.className = 'cell';
        });
    }

    updateButtons() {
        const hasActiveGame = this.isGameActive;
        
        this.resetGameBtn.disabled = !hasActiveGame;
        this.quitGameBtn.disabled = !hasActiveGame;
        
        // Enable/disable difficulty selector
        this.difficultySelect.disabled = hasActiveGame;
    }

    showMessage(message, type = '') {
        this.gameMessage.textContent = message;
        this.gameMessage.className = `message ${type}`;
    }

    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorModal.classList.remove('hidden');
    }

    hideError() {
        this.errorModal.classList.add('hidden');
    }

    // Auto-refresh game state periodically (optional)
    async refreshGameState() {
        if (!this.isGameActive) return;

        try {
            const response = await this.makeAPICall('/api/game/state');
            if (response.success) {
                this.gameState = response.game;
                this.updateGameDisplay();
            }
        } catch (error) {
            console.error('Failed to refresh game state:', error);
        }
    }
}

// Initialize the game when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.tictactoeGame = new TicTacToeGame();
    
    // Optional: Refresh game state every 30 seconds
    // setInterval(() => window.tictactoeGame.refreshGameState(), 30000);
});