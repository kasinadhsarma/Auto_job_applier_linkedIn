"""
Browser element interaction helper functions.
"""
from typing import Optional, Union
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException
)

def try_linkText(driver: WebDriver, text: str, wait_time: float = 1) -> Optional[WebElement]:
    """Try to find element by link text."""
    try:
        return WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.LINK_TEXT, text))
        )
    except (TimeoutException, NoSuchElementException):
        return None

def try_xp(driver: WebDriver, xpath: str, click: bool = True, wait_time: float = 2) -> Optional[WebElement]:
    """Try to find and optionally click element by xpath."""
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        if click:
            element.click()
        return element
    except (TimeoutException, NoSuchElementException):
        return None
    except ElementNotInteractableException as e:
        if click:
            try:
                ActionChains(driver).move_to_element(element).click().perform()
                return element
            except:
                return None
        return element

def find_by_class(driver: WebDriver, class_name: str, wait_time: float = 2) -> WebElement:
    """Find element by class name with wait."""
    return WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name))
    )

def try_find_by_classes(driver: WebDriver, class_names: list) -> Optional[WebElement]:
    """Try to find element by multiple class names."""
    for class_name in class_names:
        try:
            return find_by_class(driver, class_name)
        except (TimeoutException, NoSuchElementException):
            continue
    return None

def text_input_by_ID(driver: WebDriver, element_id: str, text: str, wait_time: float = 2) -> None:
    """Input text into element found by ID."""
    element = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text)

def text_input(actions: ActionChains, element: WebElement, text: str, error_context: str) -> None:
    """Input text using ActionChains."""
    try:
        element.clear()
        element.send_keys(text)
    except Exception as e:
        raise Exception(f"Failed to input text for {error_context}") from e

def wait_span_click(driver: WebDriver, text: str, wait_time: float = 2,
                   error_out: bool = True, scrollTop: bool = True) -> bool:
    """Wait for and click span element containing text."""
    try:
        span = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(
                (By.XPATH, f".//span[normalize-space()='{text}']")
            )
        )
        if scrollTop:
            driver.execute_script("arguments[0].scrollIntoView(true);", span)
        span.click()
        return True
    except Exception as e:
        if error_out:
            raise Exception(f"Failed to click span with text: {text}") from e
        return False

def multi_sel_noWait(driver: WebDriver, items: list, actions: Optional[ActionChains] = None) -> None:
    """Select multiple items from a list without waiting."""
    if not items:
        return
        
    for item in items:
        try:
            element = driver.find_element(
                By.XPATH, f".//label[normalize-space()='{item}']"
            )
            if actions:
                actions.move_to_element(element).click().perform()
            else:
                element.click()
        except Exception:
            continue

def boolean_button_click(driver: WebDriver, actions: ActionChains, button_text: str) -> None:
    """Click a boolean type button."""
    try:
        button = driver.find_element(
            By.XPATH, f".//label[normalize-space()='{button_text}']"
        )
        actions.move_to_element(button).click().perform()
    except Exception as e:
        raise Exception(f"Failed to click button: {button_text}") from e

def scroll_to_view(driver: WebDriver, element: WebElement, align_top: bool = False) -> None:
    """Scroll element into view."""
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView(arguments[1]);",
            element,
            align_top
        )
    except Exception as e:
        raise Exception("Failed to scroll element into view") from e

def buffer(seconds: float = 1) -> None:
    """Add a delay buffer."""
    if seconds > 0:
        sleep(seconds)
