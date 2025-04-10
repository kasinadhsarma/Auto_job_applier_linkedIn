"""
Main LinkedIn bot implementation.
"""
from typing import Dict, Any, Optional
from time import sleep
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..core.browser import BrowserManager
from ..modules.utils.element_helpers import (
    try_linkText,
    try_xp,
    find_by_class,
    try_find_by_classes,
    text_input_by_ID,
    text_input,
    wait_span_click,
    multi_sel_noWait,
    boolean_button_click,
    scroll_to_view,
    buffer
)
from app.modules.utils.logging import print_lg, error_log

class LinkedInBot:
    """LinkedIn automation bot."""
    
    def __init__(self, browser: BrowserManager, config: Dict[str, Any]):
        """Initialize bot with browser and configuration."""
        self.browser = browser
        self.driver = browser.driver
        self.config = config
        self.actions = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self) -> bool:
        """
        Perform LinkedIn login.
        Returns True if successful, False otherwise.
        """
        try:
            # Navigate to login page
            self.driver.get('https://www.linkedin.com/login')
            buffer()

            # Enter credentials
            text_input_by_ID(self.driver, 'username', self.config['username'])
            text_input_by_ID(self.driver, 'password', self.config['password'])
            
            # Submit login form
            self.driver.find_element(By.CLASS_NAME, 'btn__primary--large').click()
            buffer()

            return True

        except Exception as e:
            error_log("Login failed", e)
            return False

    def manual_login_retry(self) -> None:
        """Handle manual login if automated login fails."""
        print_lg("Automated login failed. Please login manually...")
        wait = input("Press enter once you have logged in...")
        print_lg("Continuing...")
        buffer()

    def navigate_to_jobs(self) -> bool:
        """Navigate to jobs page."""
        try:
            # Click Jobs link
            jobs_button = try_xp(self.driver, "//a[@href='/jobs/']")
            if not jobs_button:
                jobs_button = try_linkText(self.driver, "Jobs")
            
            if not jobs_button:
                return False

            jobs_button.click()
            buffer()
            return True

        except Exception as e:
            error_log("Failed to navigate to jobs", e)
            return False

    def apply_search_filters(self) -> None:
        """Apply job search filters."""
        try:
            # Date posted filter
            if self.config.get('date_posted'):
                date_posted_button = find_by_class(self.driver, "jobs-search-box__controls")
                if date_posted_button:
                    scroll_to_view(self.driver, date_posted_button)
                    date_posted_button.click()
                    buffer()

            # Additional filters based on config
            if self.config.get('experience_level'):
                self._apply_experience_filter()

            if self.config.get('job_type'):
                self._apply_job_type_filter()

            if self.config.get('on_site'):
                self._apply_remote_filter()

        except Exception as e:
            error_log("Failed to apply filters", e)

    def _apply_experience_filter(self) -> None:
        """Apply experience level filter."""
        try:
            filter_button = try_find_by_classes(self.driver, ["artdeco-pill", "artdeco-pill--2"])
            if filter_button:
                scroll_to_view(self.driver, filter_button)
                filter_button.click()
                buffer()

                # Select experience levels
                for level in self.config['experience_level']:
                    checkbox = try_xp(self.driver, f"//label[contains(.,'{level}')]")
                    if checkbox:
                        checkbox.click()
                        buffer()

        except Exception as e:
            error_log("Failed to apply experience filter", e)

    def _apply_job_type_filter(self) -> None:
        """Apply job type filter."""
        pass  # Implementation similar to experience filter

    def _apply_remote_filter(self) -> None:
        """Apply remote work filter."""
        pass  # Implementation similar to experience filter

    def get_job_listings(self) -> list:
        """Get list of job listings from current page."""
        try:
            return self.driver.find_elements(
                By.CLASS_NAME,
                "jobs-search-results__list-item"
            )
        except Exception:
            return []

    def scroll_to_job(self, job_element) -> None:
        """Scroll job into view."""
        try:
            scroll_to_view(self.driver, job_element)
            buffer()
        except Exception as e:
            error_log("Failed to scroll to job", e)

    def close_browser(self) -> None:
        """Close browser instance."""
        self.browser.close()
