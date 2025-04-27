from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException, 
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException
)
from app.modules.clickers_and_finders import wait_span_click, try_xp
from app.modules.helpers import print_lg, buffer
import time

class JobApplier:
    def __init__(self, driver, wait, actions):
        self.driver = driver
        self.wait = wait
        self.actions = actions
        
    def retry_click(self, element, retries=3, delay=1):
        """Retry clicking an element with exponential backoff"""
        for attempt in range(retries):
            try:
                element.click()
                return True
            except (StaleElementReferenceException, ElementClickInterceptedException):
                if attempt == retries - 1:
                    return False
                time.sleep(delay * (2 ** attempt))
                element = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//*[normalize-space()='{element.text}']")
                ))
        return False

    def safe_click(self, text, wait_time=5, scroll=True):
        """Click element containing text with retries and error handling"""
        try:
            element = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//*[normalize-space()='{text}']")
            ))
            
            if scroll:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
                time.sleep(0.5)
                
            try:
                element.click()
                return True
            except:
                try:
                    self.actions.move_to_element(element).click().perform()
                    return True
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    except:
                        return False
                        
        except (TimeoutException, NoSuchElementException):
            return False

    def fill_form(self, question_map):
        """Fill out job application form with error handling"""
        success = True
        for question, answer in question_map.items():
            try:
                # Find question element
                question_elem = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//label[contains(text(), '{question}')]")
                ))
                
                # Get input element
                input_elem = question_elem.find_element(By.XPATH, ".//following::input[1]")
                
                # Clear and fill
                input_elem.clear()
                input_elem.send_keys(answer)
                
                buffer(0.5)
                
            except Exception as e:
                print_lg(f"Failed to fill question '{question}': {str(e)}")
                success = False
                
        return success
        
    def navigate_next(self):
        """Navigate to next page safely"""
        success = False
        buttons = ['Next', 'Review', 'Submit application', 'Done']
        
        for button in buttons:
            if self.safe_click(button):
                success = True
                break
                
        if not success:
            # Try alternate strategies like pressing Enter
            try:
                self.actions.send_keys(Keys.ENTER).perform()
                success = True
            except:
                pass
                
        return success
