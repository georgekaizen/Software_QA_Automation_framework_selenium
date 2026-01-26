import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVERS_DIR = os.path.join(PROJECT_ROOT, "drivers")

# Map browser names to their manual driver binary filenames
_MANUAL_DRIVER_NAMES = {
    "chrome": "chromedriver",
    "firefox": "geckodriver",
    "edge": "msedgedriver",
}


def pytest_addoption(parser):
    """Register the --browser-name command-line option."""
    parser.addoption(
        "--browser-name",
        action="store",
        default=None,
        help="Browser to run tests on: chrome, firefox, or edge",
    )


def _get_browser_name(request):
    """
    Determine which browser to use.
    CLI flag --browser-name overrides config.ini [browser] default_browser.
    """
    cli_browser = request.config.getoption("--browser-name")
    if cli_browser:
        return cli_browser.lower()

    from Utilities.ConfigReader import ConfigReader

    try:
        return ConfigReader.readconfig("browser", "default_browser").lower()
    except Exception:
        return "chrome"


def _find_manual_driver(browser_name):
    """
    Look for a manually placed driver binary in the drivers/ directory.
    Returns the path if found, otherwise None.
    """
    binary = _MANUAL_DRIVER_NAMES.get(browser_name)
    if not binary:
        return None

    driver_path = os.path.join(DRIVERS_DIR, binary)
    if os.path.isfile(driver_path):
        return driver_path
    return None


def _create_driver_auto(browser_name):
    """
    Create a WebDriver using Selenium's built-in driver manager (Selenium 4.6+).
    Falls back to webdriver-manager library if needed.
    """
    if browser_name == "chrome":
        return webdriver.Chrome()
    elif browser_name == "firefox":
        return webdriver.Firefox()
    elif browser_name == "edge":
        return webdriver.Edge()

    raise ValueError(
        f"Unsupported browser: '{browser_name}'. Use chrome, firefox, or edge."
    )


def _create_driver_with_manual_path(browser_name, driver_path):
    """
    Create a WebDriver using a manually placed driver binary from drivers/.
    """
    if browser_name == "chrome":
        service = ChromeService(executable_path=driver_path)
        return webdriver.Chrome(service=service)

    elif browser_name == "firefox":
        service = FirefoxService(executable_path=driver_path)
        return webdriver.Firefox(service=service)

    elif browser_name == "edge":
        service = EdgeService(executable_path=driver_path)
        return webdriver.Edge(service=service)

    raise ValueError(
        f"Unsupported browser: '{browser_name}'. Use chrome, firefox, or edge."
    )


def _create_driver(browser_name):
    """
    Create and return a WebDriver instance for the given browser.

    Strategy:
      1. Try Selenium's built-in driver manager (auto-download).
      2. If that fails, fall back to a manual driver binary in drivers/.
    """
    os.makedirs(DRIVERS_DIR, exist_ok=True)

    # --- Attempt 1: Selenium's built-in driver manager ---
    try:
        driver = _create_driver_auto(browser_name)
        driver.maximize_window()
        return driver
    except Exception as manager_err:
        print(
            f"[conftest] Auto driver setup failed for '{browser_name}': {manager_err}"
        )

    # --- Attempt 2: manual driver in drivers/ ---
    manual_path = _find_manual_driver(browser_name)
    if manual_path:
        print(f"[conftest] Falling back to manual driver: {manual_path}")
        driver = _create_driver_with_manual_path(browser_name, manual_path)
        driver.maximize_window()
        return driver

    raise RuntimeError(
        f"Could not create a '{browser_name}' driver.\n"
        f"  - Auto driver setup failed (see above).\n"
        f"  - No manual driver found at: "
        f"{os.path.join(DRIVERS_DIR, _MANUAL_DRIVER_NAMES.get(browser_name, '?'))}\n"
        f"Place the driver binary in the drivers/ directory and retry."
    )


@pytest.fixture
def driver(request):
    """
    Pytest fixture that provides a WebDriver instance.
    Yields the driver to the test, then quits during teardown.
    """
    browser_name = _get_browser_name(request)
    web_driver = _create_driver(browser_name)
    yield web_driver
    web_driver.quit()


@pytest.fixture
def navigate_to_saucedemo(driver):
    """
    Convenience fixture that opens the SauceDemo URL before the test.
    """
    from Utilities.ConfigReader import ConfigReader

    url = ConfigReader.readconfig("locators", "sauce_demo_url")
    driver.get(url)
    return driver
