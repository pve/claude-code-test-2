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
    HEALTH_LINK = (By.LINK_TEXT, "Health Check")
    API_STATUS_LINK = (By.LINK_TEXT, "API Status")
    WELCOME_HEADING = (By.TAG_NAME, "h2")

    def get_welcome_text(self):
        return self.find_element(self.WELCOME_HEADING).text

    def click_health_check(self):
        self.click_element(self.HEALTH_LINK)

    def click_api_status(self):
        self.click_element(self.API_STATUS_LINK)


@pytest.fixture(scope="session")
def is_ci():
    """Check if running in CI environment."""
    return any([os.getenv("CI"), os.getenv("GITHUB_ACTIONS")])


@pytest.fixture(scope="session")
def app_url():
    """Get application URL for testing."""
    return os.environ.get("TEST_URL", "http://127.0.0.1:5001")


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
def test_home_page_loads(chrome_driver, app_url):
    """Test that the home page loads successfully."""
    driver = chrome_driver
    driver.get(app_url)

    home_page = HomePage(driver)

    # Verify page title
    assert "Claude Code Test 2" in home_page.get_title()

    # Verify welcome message
    welcome_text = home_page.get_welcome_text()
    assert "Welcome to Claude Code Test 2" in welcome_text


@pytest.mark.e2e
def test_health_check_navigation(chrome_driver, app_url):
    """Test navigation to health check endpoint."""
    driver = chrome_driver
    driver.get(app_url)

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
def test_api_status_navigation(chrome_driver, app_url):
    """Test navigation to API status endpoint."""
    driver = chrome_driver
    driver.get(app_url)

    home_page = HomePage(driver)

    # Click API status link
    home_page.click_api_status()

    # Verify we're on the API status endpoint
    assert "/api/status" in driver.current_url

    # Verify JSON response is displayed
    page_source = driver.page_source
    assert "api_version" in page_source
    assert "operational" in page_source


@pytest.mark.e2e
def test_responsive_layout(chrome_driver, app_url):
    """Test responsive design on different screen sizes."""
    driver = chrome_driver
    driver.get(app_url)

    # Test mobile size
    driver.set_window_size(375, 667)
    home_page = HomePage(driver)

    # Verify page still loads and content is accessible
    welcome_text = home_page.get_welcome_text()
    assert "Welcome to Claude Code Test 2" in welcome_text

    # Test desktop size
    driver.set_window_size(1920, 1080)

    # Verify layout still works
    welcome_text = home_page.get_welcome_text()
    assert "Welcome to Claude Code Test 2" in welcome_text


@pytest.mark.e2e
def test_full_user_journey(chrome_driver, app_url):
    """Test complete user journey through the application."""
    driver = chrome_driver
    driver.get(app_url)

    home_page = HomePage(driver)

    # Step 1: Verify home page
    assert "Claude Code Test 2" in home_page.get_title()
    welcome_text = home_page.get_welcome_text()
    assert "Welcome to Claude Code Test 2" in welcome_text

    # Step 2: Check health endpoint
    home_page.click_health_check()
    assert "/health" in driver.current_url
    assert "healthy" in driver.page_source

    # Step 3: Navigate back to home
    driver.back()
    assert app_url in driver.current_url

    # Step 4: Check API status
    home_page = HomePage(driver)  # Reinitialize after navigation
    home_page.click_api_status()
    assert "/api/status" in driver.current_url
    assert "operational" in driver.page_source

    # Step 5: Navigate back to home again
    driver.back()
    assert app_url in driver.current_url
