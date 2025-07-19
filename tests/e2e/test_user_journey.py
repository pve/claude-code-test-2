import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class BasePage:
    """Page Object Model base class."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def get_title(self):
        return self.driver.title

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click_element(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()


class HomePage(BasePage):
    """Home page object."""

    # Locators
    HEALTH_LINK = (By.LINK_TEXT, "Health")
    ABOUT_LINK = (By.LINK_TEXT, "About")
    WELCOME_HEADING = (By.TAG_NAME, "h2")

    def get_welcome_text(self):
        return self.find_element(self.WELCOME_HEADING).text

    def click_health_check(self):
        self.click_element(self.HEALTH_LINK)

    def click_about(self):
        self.click_element(self.ABOUT_LINK)


@pytest.fixture(scope="session")
def is_ci():
    """Check if running in CI environment."""
    return any([os.getenv("CI"), os.getenv("GITHUB_ACTIONS")])


@pytest.fixture
def user_journey_server():
    """Start the Flask application for testing."""
    import socket
    import time
    import requests
    from app import create_app
    import threading
    
    # Find an available port (avoiding 5000 and 5001)
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
        'SECRET_KEY': 'test-secret-user-journey'
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




@pytest.fixture
def chrome_driver(is_ci):
    """Create Chrome WebDriver with appropriate options."""
    chrome_options = Options()

    if is_ci:
        # CI environment configuration
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
    else:
        # Local development configuration
        chrome_options.add_argument("--window-size=1280,720")

    # Common options
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")

    # Set up driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    # Cleanup
    driver.quit()


@pytest.mark.e2e
def test_home_page_loads(chrome_driver, user_journey_server):
    """Test that the home page loads successfully."""
    driver = chrome_driver
    driver.get(user_journey_server)

    home_page = HomePage(driver)

    # Verify page title
    assert "Tic-Tac-Toe Game" in home_page.get_title()

    # Verify welcome message
    welcome_text = home_page.get_welcome_text()
    assert "Tic-Tac-Toe" in welcome_text


@pytest.mark.e2e
def test_health_check_navigation(chrome_driver, user_journey_server):
    """Test navigation to health check endpoint."""
    driver = chrome_driver
    driver.get(user_journey_server)

    home_page = HomePage(driver)

    # Click health check link
    home_page.click_health_check()

    # Verify we're on the health endpoint
    assert "/health" in driver.current_url

    # Verify JSON response is displayed
    page_source = driver.page_source
    assert "healthy" in page_source
    assert "claude-code-test-2" in page_source


@pytest.mark.e2e
def test_about_navigation(chrome_driver, user_journey_server):
    """Test navigation to about page."""
    driver = chrome_driver
    driver.get(user_journey_server)

    home_page = HomePage(driver)

    # Click about link
    home_page.click_about()

    # Verify we're on the welcome page
    assert "/welcome" in driver.current_url

    # Verify welcome page content is displayed
    page_source = driver.page_source
    assert "Welcome" in page_source


@pytest.mark.e2e
def test_responsive_layout(chrome_driver, user_journey_server):
    """Test responsive design on different screen sizes."""
    driver = chrome_driver
    driver.get(user_journey_server)

    # Test mobile size
    driver.set_window_size(375, 667)
    home_page = HomePage(driver)

    # Verify page still loads and content is accessible
    welcome_text = home_page.get_welcome_text()
    assert "Tic-Tac-Toe" in welcome_text

    # Test desktop size
    driver.set_window_size(1920, 1080)

    # Verify layout still works
    welcome_text = home_page.get_welcome_text()
    assert "Tic-Tac-Toe" in welcome_text


@pytest.mark.e2e
def test_full_user_journey(chrome_driver, user_journey_server):
    """Test complete user journey through the application."""
    driver = chrome_driver
    driver.get(user_journey_server)

    home_page = HomePage(driver)

    # Step 1: Verify home page
    assert "Tic-Tac-Toe Game" in home_page.get_title()
    welcome_text = home_page.get_welcome_text()
    assert "Tic-Tac-Toe" in welcome_text

    # Step 2: Check health endpoint
    home_page.click_health_check()
    assert "/health" in driver.current_url
    assert "healthy" in driver.page_source

    # Step 3: Navigate back to home
    driver.back()
    assert user_journey_server in driver.current_url

    # Step 4: Check about page
    home_page = HomePage(driver)  # Reinitialize after navigation
    home_page.click_about()
    assert "/welcome" in driver.current_url
    assert "Welcome" in driver.page_source

    # Step 5: Navigate back to home again
    driver.back()
    assert user_journey_server in driver.current_url
