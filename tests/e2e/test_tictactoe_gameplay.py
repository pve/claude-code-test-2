"""End-to-end tests for tic-tac-toe gameplay."""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="session")
def is_ci():
    """Check if running in CI environment."""
    import os
    return any([os.getenv("CI"), os.getenv("GITHUB_ACTIONS")])


@pytest.fixture
def driver(is_ci):
    """Create WebDriver instance."""
    chrome_options = Options()
    
    if is_ci:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    driver.quit()


@pytest.fixture
def live_server():
    """Start the Flask application for testing."""
    import socket
    import time
    import requests
    from app import create_app
    import threading
    
    # Find an available port (avoiding 5000)
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    port = find_free_port()
    
    # Create test app
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-e2e'
    })
    
    # Start the server in a separate thread
    def run_server():
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    base_url = f'http://127.0.0.1:{port}'
    for _ in range(30):
        try:
            response = requests.get(f'{base_url}/health', timeout=1)
            if response.status_code == 200:
                break
        except:
            time.sleep(0.5)
    else:
        pytest.skip("Could not start test server")
    
    yield base_url


@pytest.mark.e2e
def test_complete_game_flow(driver, live_server):
    """Test complete tic-tac-toe game flow from start to finish."""
    # Navigate to the game page
    driver.get(f"{live_server}/")
    
    # Wait for page to load
    wait = WebDriverWait(driver, 10)
    
    # Check page title
    assert "Tic-Tac-Toe" in driver.title
    
    # Verify game board is present
    game_board = wait.until(EC.presence_of_element_located((By.ID, "game-board")))
    assert game_board is not None
    
    # Check that cells are present
    cells = driver.find_elements(By.CLASS_NAME, "cell")
    assert len(cells) == 9
    
    # Verify initial message
    message = driver.find_element(By.ID, "game-message")
    assert "Welcome" in message.text
    
    # Start a new game
    new_game_btn = driver.find_element(By.ID, "new-game-btn")
    new_game_btn.click()
    
    # Wait for game to start
    wait.until(EC.text_to_be_present_in_element((By.ID, "game-message"), "Game started!"))
    
    # Make the first move (click center cell)
    center_cell = driver.find_element(By.CSS_SELECTOR, '[data-row="1"][data-col="1"]')
    center_cell.click()
    
    # Wait for AI move (with loading overlay)
    wait.until(EC.text_to_be_present_in_element((By.ID, "game-message"), "AI"))
    
    # Verify that center cell now contains X
    assert center_cell.text == "X"
    
    # Check that at least one other cell now contains O (AI move)
    o_cells = driver.find_elements(By.CLASS_NAME, "player-o")
    assert len(o_cells) >= 1
    
    # Verify move history is updated
    move_history = driver.find_element(By.ID, "move-history")
    assert "You:" in move_history.text
    assert "AI:" in move_history.text


@pytest.mark.e2e
def test_difficulty_selection(driver, live_server):
    """Test that difficulty selection works."""
    driver.get(f"{live_server}/")
    
    wait = WebDriverWait(driver, 10)
    
    # Select difficulty dropdown
    difficulty_select = Select(driver.find_element(By.ID, "difficulty"))
    
    # Verify all difficulty options are present
    options = [option.get_attribute("value") for option in difficulty_select.options]
    assert "easy" in options
    assert "medium" in options
    assert "hard" in options
    
    # Select hard difficulty
    difficulty_select.select_by_value("hard")
    
    # Start new game
    new_game_btn = driver.find_element(By.ID, "new-game-btn")
    new_game_btn.click()
    
    # Wait for game to start
    wait.until(EC.text_to_be_present_in_element((By.ID, "game-message"), "Game started!"))
    
    # Verify difficulty selector is disabled during game
    assert not driver.find_element(By.ID, "difficulty").is_enabled()


@pytest.mark.e2e 
def test_game_controls(driver, live_server):
    """Test that game control buttons work correctly."""
    driver.get(f"{live_server}/")
    
    wait = WebDriverWait(driver, 10)
    
    # Initially reset and quit should be disabled
    reset_btn = driver.find_element(By.ID, "reset-game-btn")
    quit_btn = driver.find_element(By.ID, "quit-game-btn")
    
    assert not reset_btn.is_enabled()
    assert not quit_btn.is_enabled()
    
    # Start new game
    new_game_btn = driver.find_element(By.ID, "new-game-btn")
    new_game_btn.click()
    
    # Wait for game to start
    wait.until(EC.text_to_be_present_in_element((By.ID, "game-message"), "Game started!"))
    
    # Now reset and quit should be enabled
    assert reset_btn.is_enabled()
    assert quit_btn.is_enabled()
    
    # Test reset
    reset_btn.click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "game-message"), "Game reset"))
    
    # Verify board is cleared
    cells = driver.find_elements(By.CLASS_NAME, "cell")
    for cell in cells:
        assert cell.text == ""
    
    # Test quit
    quit_btn.click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "game-message"), "Game ended"))
    
    # Verify buttons are disabled again
    assert not reset_btn.is_enabled()
    assert not quit_btn.is_enabled()


@pytest.mark.e2e
def test_error_handling(driver, live_server):
    """Test error handling for invalid moves."""
    driver.get(f"{live_server}/")
    
    wait = WebDriverWait(driver, 10)
    
    # Try to make move without starting game
    center_cell = driver.find_element(By.CSS_SELECTOR, '[data-row="1"][data-col="1"]')
    center_cell.click()
    
    # Should show error modal
    error_modal = wait.until(EC.visibility_of_element_located((By.ID, "error-modal")))
    error_message = driver.find_element(By.ID, "error-message")
    assert "No active game" in error_message.text
    
    # Close error modal
    close_btn = driver.find_element(By.CLASS_NAME, "close")
    close_btn.click()
    
    wait.until(EC.invisibility_of_element_located((By.ID, "error-modal")))
    
    # Start game and test occupied cell error
    new_game_btn = driver.find_element(By.ID, "new-game-btn")
    new_game_btn.click()
    
    wait.until(EC.text_to_be_present_in_element((By.ID, "game-message"), "Game started!"))
    
    # Make a move
    center_cell.click()
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '[data-row="1"][data-col="1"]'), "X"))
    
    # Try to click same cell again
    center_cell.click()
    
    # Should show error
    error_modal = wait.until(EC.visibility_of_element_located((By.ID, "error-modal")))
    error_message = driver.find_element(By.ID, "error-message")
    assert "already taken" in error_message.text


@pytest.mark.e2e
def test_responsive_design(driver, live_server):
    """Test that the game works on different screen sizes."""
    driver.get(f"{live_server}/")
    
    # Test mobile size
    driver.set_window_size(480, 800)
    time.sleep(1)
    
    # Game board should still be visible and clickable
    game_board = driver.find_element(By.ID, "game-board")
    assert game_board.is_displayed()
    
    cells = driver.find_elements(By.CLASS_NAME, "cell")
    assert len(cells) == 9
    
    # Test tablet size
    driver.set_window_size(768, 1024)
    time.sleep(1)
    
    # Elements should still be properly arranged
    controls = driver.find_element(By.CLASS_NAME, "game-controls")
    assert controls.is_displayed()
    
    # Test desktop size
    driver.set_window_size(1920, 1080)
    time.sleep(1)
    
    # All elements should be visible
    history = driver.find_element(By.CLASS_NAME, "game-history")
    assert history.is_displayed()