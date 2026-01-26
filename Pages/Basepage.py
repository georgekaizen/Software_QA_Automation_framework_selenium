import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from Utilities.ConfigReader import ConfigReader
from Utilities.Log import Log


class WebActions:

    DEFAULT_TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver

    # ------------------------------------------------------------------ #
    #  CORE / INTERNAL HELPERS
    # ------------------------------------------------------------------ #

    def _get_by_type(self, locator):
        """Determines Selenium By strategy based on locator suffix."""
        locator = str(locator)

        if locator.endswith("_XPATH"):
            return By.XPATH
        elif locator.endswith("_ID"):
            return By.ID
        elif locator.endswith("_NAME"):
            return By.NAME
        elif locator.endswith("_CSS"):
            return By.CSS_SELECTOR
        elif locator.endswith("_CLASS"):
            return By.CLASS_NAME
        elif locator.endswith("_LINKTEXT"):
            return By.LINK_TEXT
        elif locator.endswith("_PARTIALLINKTEXT"):
            return By.PARTIAL_LINK_TEXT
        else:
            raise ValueError(f"Unsupported locator type: {locator}")

    def _get_element(self, locator, timeout=DEFAULT_TIMEOUT):
        """Fetches a web element using config-based locator and explicit wait."""
        by_type = self._get_by_type(locator)
        locator_value = ConfigReader.readconfig("locators", locator)

        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by_type, locator_value))
        )

    def _get_elements(self, locator, timeout=DEFAULT_TIMEOUT):
        """Fetches all matching web elements using config-based locator."""
        by_type = self._get_by_type(locator)
        locator_value = ConfigReader.readconfig("locators", locator)

        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by_type, locator_value))
        )
        return self.driver.find_elements(by_type, locator_value)

    # ------------------------------------------------------------------ #
    #  BASIC INTERACTIONS
    # ------------------------------------------------------------------ #

    def click(self, locator):
        """Clicks on a web element."""
        self._get_element(locator).click()
        Log.logger.info(f"Clicked on element: {locator}")

    def type(self, locator, text):
        """Clears a field and types the given text."""
        element = self._get_element(locator)
        element.clear()
        element.send_keys(text)
        Log.logger.info(f"Typed '{text}' into element: {locator}")

    def clear(self, locator):
        """Clears the text from an input field."""
        self._get_element(locator).clear()
        Log.logger.info(f"Cleared element: {locator}")

    def submit(self, locator):
        """Submits a form via the given element."""
        self._get_element(locator).submit()
        Log.logger.info(f"Submitted form via element: {locator}")

    def press_key(self, locator, key_name):
        """
        Presses a keyboard key on an element.
        key_name should be a Keys attribute name, e.g. 'ENTER', 'TAB', 'ESCAPE'.
        """
        key = getattr(Keys, key_name.upper(), None)
        if key is None:
            raise ValueError(f"Unknown key: '{key_name}'. Use Keys attribute names like ENTER, TAB, ESCAPE.")
        self._get_element(locator).send_keys(key)
        Log.logger.info(f"Pressed key '{key_name}' on element: {locator}")

    def upload_file(self, locator, file_path):
        """Uploads a file via a file input element."""
        abs_path = os.path.abspath(file_path)
        self._get_element(locator).send_keys(abs_path)
        Log.logger.info(f"Uploaded file '{abs_path}' to element: {locator}")

    # ------------------------------------------------------------------ #
    #  ELEMENT STATE
    # ------------------------------------------------------------------ #

    def get_text(self, locator):
        """Returns the visible text of an element."""
        text = self._get_element(locator).text
        Log.logger.info(f"Got text '{text}' from element: {locator}")
        return text

    def get_attribute(self, locator, attribute):
        """Returns the value of an element's attribute."""
        value = self._get_element(locator).get_attribute(attribute)
        Log.logger.info(f"Got attribute '{attribute}' = '{value}' from element: {locator}")
        return value

    def is_displayed(self, locator, timeout=DEFAULT_TIMEOUT):
        """Returns True if the element is visible on the page."""
        try:
            by_type = self._get_by_type(locator)
            locator_value = ConfigReader.readconfig("locators", locator)
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by_type, locator_value))
            )
            Log.logger.info(f"Element is displayed: {locator}")
            return True
        except Exception:
            Log.logger.info(f"Element is NOT displayed: {locator}")
            return False

    def is_enabled(self, locator):
        """Returns True if the element is enabled."""
        enabled = self._get_element(locator).is_enabled()
        Log.logger.info(f"Element enabled={enabled}: {locator}")
        return enabled

    def is_selected(self, locator):
        """Returns True if the element is selected (checkbox, radio, option)."""
        selected = self._get_element(locator).is_selected()
        Log.logger.info(f"Element selected={selected}: {locator}")
        return selected

    def get_element_count(self, locator, timeout=DEFAULT_TIMEOUT):
        """Returns the number of elements matching the locator."""
        elements = self._get_elements(locator, timeout)
        count = len(elements)
        Log.logger.info(f"Found {count} elements for: {locator}")
        return count

    # ------------------------------------------------------------------ #
    #  WAITS
    # ------------------------------------------------------------------ #

    def wait_for_element_visible(self, locator, timeout=DEFAULT_TIMEOUT):
        """Waits until an element is visible on the page."""
        by_type = self._get_by_type(locator)
        locator_value = ConfigReader.readconfig("locators", locator)
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by_type, locator_value))
        )
        Log.logger.info(f"Element is now visible: {locator}")
        return element

    def wait_for_element_invisible(self, locator, timeout=DEFAULT_TIMEOUT):
        """Waits until an element is no longer visible on the page."""
        by_type = self._get_by_type(locator)
        locator_value = ConfigReader.readconfig("locators", locator)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((by_type, locator_value))
        )
        Log.logger.info(f"Element is now invisible: {locator}")

    def wait_for_text_present(self, locator, text, timeout=DEFAULT_TIMEOUT):
        """Waits until the specified text is present in an element."""
        by_type = self._get_by_type(locator)
        locator_value = ConfigReader.readconfig("locators", locator)
        WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element((by_type, locator_value), text)
        )
        Log.logger.info(f"Text '{text}' is now present in element: {locator}")

    def wait_for_url_contains(self, text, timeout=DEFAULT_TIMEOUT):
        """Waits until the current URL contains the specified text."""
        WebDriverWait(self.driver, timeout).until(EC.url_contains(text))
        Log.logger.info(f"URL now contains: '{text}'")

    # ------------------------------------------------------------------ #
    #  DROPDOWNS (SELECT)
    # ------------------------------------------------------------------ #

    def select_by_visible_text(self, locator, text):
        """Selects a dropdown option by its visible text."""
        select = Select(self._get_element(locator))
        select.select_by_visible_text(text)
        Log.logger.info(f"Selected text '{text}' in dropdown: {locator}")

    def select_by_value(self, locator, value):
        """Selects a dropdown option by its value attribute."""
        select = Select(self._get_element(locator))
        select.select_by_value(value)
        Log.logger.info(f"Selected value '{value}' in dropdown: {locator}")

    def select_by_index(self, locator, index):
        """Selects a dropdown option by its index (0-based)."""
        select = Select(self._get_element(locator))
        select.select_by_index(index)
        Log.logger.info(f"Selected index {index} in dropdown: {locator}")

    def get_selected_option_text(self, locator):
        """Returns the text of the currently selected dropdown option."""
        select = Select(self._get_element(locator))
        text = select.first_selected_option.text
        Log.logger.info(f"Selected option text is '{text}' in dropdown: {locator}")
        return text

    def get_all_option_texts(self, locator):
        """Returns a list of all option texts in a dropdown."""
        select = Select(self._get_element(locator))
        texts = [option.text for option in select.options]
        Log.logger.info(f"Dropdown options for {locator}: {texts}")
        return texts

    # ------------------------------------------------------------------ #
    #  ADVANCED MOUSE INTERACTIONS
    # ------------------------------------------------------------------ #

    def hover(self, locator):
        """Moves the mouse to hover over an element."""
        element = self._get_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()
        Log.logger.info(f"Hovered over element: {locator}")

    def double_click(self, locator):
        """Double-clicks on an element."""
        element = self._get_element(locator)
        ActionChains(self.driver).double_click(element).perform()
        Log.logger.info(f"Double-clicked on element: {locator}")

    def right_click(self, locator):
        """Right-clicks (context click) on an element."""
        element = self._get_element(locator)
        ActionChains(self.driver).context_click(element).perform()
        Log.logger.info(f"Right-clicked on element: {locator}")

    def drag_and_drop(self, source_locator, target_locator):
        """Drags an element from source and drops it on target."""
        source = self._get_element(source_locator)
        target = self._get_element(target_locator)
        ActionChains(self.driver).drag_and_drop(source, target).perform()
        Log.logger.info(f"Dragged '{source_locator}' to '{target_locator}'")

    def scroll_to_element(self, locator):
        """Scrolls the page until the element is in view."""
        element = self._get_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        Log.logger.info(f"Scrolled to element: {locator}")

    def click_with_js(self, locator):
        """Clicks an element using JavaScript (useful when normal click is intercepted)."""
        element = self._get_element(locator)
        self.driver.execute_script("arguments[0].click();", element)
        Log.logger.info(f"JS-clicked on element: {locator}")

    # ------------------------------------------------------------------ #
    #  BROWSER UTILITIES
    # ------------------------------------------------------------------ #

    def get_current_url(self):
        """Returns the current page URL."""
        url = self.driver.current_url
        Log.logger.info(f"Current URL: {url}")
        return url

    def get_page_title(self):
        """Returns the current page title."""
        title = self.driver.title
        Log.logger.info(f"Page title: {title}")
        return title

    def navigate_to(self, url):
        """Navigates the browser to the given URL."""
        self.driver.get(url)
        Log.logger.info(f"Navigated to: {url}")

    def refresh_page(self):
        """Refreshes the current page."""
        self.driver.refresh()
        Log.logger.info("Page refreshed")

    def go_back(self):
        """Navigates back to the previous page."""
        self.driver.back()
        Log.logger.info("Navigated back")

    def go_forward(self):
        """Navigates forward to the next page."""
        self.driver.forward()
        Log.logger.info("Navigated forward")

    def take_screenshot(self, filename):
        """
        Saves a screenshot to the screenshots/ directory.
        filename should not include a path, just the name (e.g. 'login_page.png').
        """
        screenshots_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots"
        )
        os.makedirs(screenshots_dir, exist_ok=True)
        filepath = os.path.join(screenshots_dir, filename)
        self.driver.save_screenshot(filepath)
        Log.logger.info(f"Screenshot saved: {filepath}")
        return filepath

    def execute_javascript(self, script, *args):
        """Executes JavaScript in the browser and returns the result."""
        result = self.driver.execute_script(script, *args)
        Log.logger.info(f"Executed JS: {script[:80]}...")
        return result

    # ------------------------------------------------------------------ #
    #  FRAMES
    # ------------------------------------------------------------------ #

    def switch_to_frame(self, locator):
        """Switches context to an iframe identified by the locator."""
        frame = self._get_element(locator)
        self.driver.switch_to.frame(frame)
        Log.logger.info(f"Switched to frame: {locator}")

    def switch_to_frame_by_index(self, index):
        """Switches context to an iframe by its index (0-based)."""
        self.driver.switch_to.frame(index)
        Log.logger.info(f"Switched to frame index: {index}")

    def switch_to_default_content(self):
        """Switches back to the main page from any iframe."""
        self.driver.switch_to.default_content()
        Log.logger.info("Switched to default content")

    def switch_to_parent_frame(self):
        """Switches to the parent frame from a nested iframe."""
        self.driver.switch_to.parent_frame()
        Log.logger.info("Switched to parent frame")

    # ------------------------------------------------------------------ #
    #  WINDOWS / TABS
    # ------------------------------------------------------------------ #

    def switch_to_window(self, index):
        """Switches to a browser window/tab by index (0-based)."""
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[index])
        Log.logger.info(f"Switched to window index: {index}")

    def switch_to_new_window(self):
        """Switches to the most recently opened window/tab."""
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])
        Log.logger.info("Switched to newest window")

    def close_current_window(self):
        """Closes the current window/tab and switches back to the first one."""
        self.driver.close()
        handles = self.driver.window_handles
        if handles:
            self.driver.switch_to.window(handles[0])
        Log.logger.info("Closed current window")

    def get_window_count(self):
        """Returns the number of open browser windows/tabs."""
        count = len(self.driver.window_handles)
        Log.logger.info(f"Open windows: {count}")
        return count

    # ------------------------------------------------------------------ #
    #  ALERTS
    # ------------------------------------------------------------------ #

    def accept_alert(self, timeout=DEFAULT_TIMEOUT):
        """Waits for an alert and accepts (clicks OK)."""
        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        Log.logger.info("Alert accepted")

    def dismiss_alert(self, timeout=DEFAULT_TIMEOUT):
        """Waits for an alert and dismisses (clicks Cancel)."""
        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        self.driver.switch_to.alert.dismiss()
        Log.logger.info("Alert dismissed")

    def get_alert_text(self, timeout=DEFAULT_TIMEOUT):
        """Waits for an alert and returns its text."""
        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        text = self.driver.switch_to.alert.text
        Log.logger.info(f"Alert text: {text}")
        return text

    def type_into_alert(self, text, timeout=DEFAULT_TIMEOUT):
        """Waits for a prompt alert and types text into it, then accepts."""
        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert.send_keys(text)
        alert.accept()
        Log.logger.info(f"Typed '{text}' into alert and accepted")
