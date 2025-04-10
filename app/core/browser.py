"""
Browser management module for handling browser initialization and login functionality.
"""
import os
from typing import Literal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from app.modules.utils.logging import print_lg
from app.modules.utils.element_helpers import try_linkText, try_xp, find_by_class, text_input_by_ID

class BrowserManager:
    def __init__(self, username: str, password: str, wait_timeout: int = 10):
        """Initialize browser manager with credentials and settings."""
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.tabs_count = 0
        self.main_tab = None
        self.wait_timeout = wait_timeout

    def initialize_browser(self):
        """Initialize and configure the browser."""
        # TODO: Move browser initialization from runAiBot.py
        pass

    def is_logged_in_linkedin(self) -> bool:
        """
        Check if user is logged in to LinkedIn
        Returns: True if user is logged in, False otherwise
        """
        if self.driver.current_url == "https://www.linkedin.com/feed/":
            return True
        if try_linkText(self.driver, "Sign in"):
            return False
        if try_xp(self.driver, '//button[@type="submit" and contains(text(), "Sign in")]'):
            return False
        if try_linkText(self.driver, "Join now"):
            return False
        print_lg("Didn't find Sign in link, so assuming user is logged in!")
        return True

    def login_linkedin(self) -> None:
        """
        Handle LinkedIn login process using provided credentials
        """
        self.driver.get("https://www.linkedin.com/login")
        try:
            self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
            try:
                text_input_by_ID(self.driver, "username", self.username, 1)
            except Exception as e:
                print_lg("Couldn't find username field.")
            try:
                text_input_by_ID(self.driver, "password", self.password, 1)
            except Exception as e:
                print_lg("Couldn't find password field.")
            
            # Find and click login submit button
            self.driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
        except Exception as e1:
            try:
                profile_button = find_by_class(self.driver, "profile__details")
                profile_button.click()
            except Exception as e2:
                print_lg("Couldn't Login!")

        try:
            # Wait for successful redirect indicating login
            self.wait.until(EC.url_to_be("https://www.linkedin.com/feed/"))
            print_lg("Login successful!")
            return
        except Exception as e:
            print_lg("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
            self.manual_login_retry()

    def manual_login_retry(self, max_retries: int = 2):
        """Handle manual login retry process."""
        # TODO: Implement manual login retry logic
        pass

    def switch_to_tab(self, tab_handle: str):
        """Switch browser focus to specified tab."""
        self.driver.switch_to.window(tab_handle)

    def close_browser(self):
        """Close browser and cleanup."""
        if self.driver:
            self.driver.quit()
