"""
Filter management module for handling job search filters and criteria.
"""
from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException

from app.modules.utils.logging import print_lg
from app.modules.utils.element_helpers import (
    try_xp,
    wait_span_click,
    multi_sel_noWait,
    boolean_button_click,
    text_input
)

class FilterManager:
    def __init__(self, driver: WebDriver, config: Dict[str, Any]):
        """Initialize filter manager with WebDriver and configuration."""
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 10)
        self.actions = ActionChains(driver)

    def apply_filters(self) -> None:
        """Apply all configured job search filters."""
        try:
            self._set_search_location()
            self._open_filter_modal()
            self._apply_sort_and_date()
            self._apply_experience_and_company()
            self._apply_job_type_and_location()
            self._apply_misc_filters()
            self._apply_benefits_and_commitments()
            self._show_results()
            
            if self.config.get('pause_after_filters', False):
                self._handle_filter_confirmation()

        except Exception as e:
            print_lg("Setting the preferences failed!")

    def _set_search_location(self) -> None:
        """Set the job search location."""
        search_location = self.config.get('search_location', '').strip()
        if not search_location:
            return

        try:
            print_lg(f'Setting search location as: "{search_location}"')
            location_input = try_xp(
                self.driver,
                ".//input[@aria-label='City, state, or zip code'and not(@disabled)]",
                False
            )
            text_input(self.actions, location_input, search_location, "Search Location")
        except ElementNotInteractableException:
            self._handle_location_input_fallback(search_location)
        except Exception as e:
            try_xp(self.driver, ".//button[@aria-label='Cancel']")
            print_lg("Failed to update search location, continuing with default location!")

    def _handle_location_input_fallback(self, search_location: str) -> None:
        """Handle alternative method for location input if primary fails."""
        try:
            try_xp(self.driver, ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']")
            self.actions.send_keys(ActionChains.TAB, ActionChains.TAB).perform()
            self.actions.key_down(ActionChains.CONTROL).send_keys("a").key_up(ActionChains.CONTROL).perform()
            self.actions.send_keys(search_location.strip()).perform()
            self.actions.send_keys(ActionChains.ENTER).perform()
        except Exception:
            try_xp(self.driver, ".//button[@aria-label='Cancel']")
            raise

    def _open_filter_modal(self) -> None:
        """Open the filters modal dialog."""
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//button[normalize-space()="All filters"]')
        )).click()
        self._buffer_click()

    def _apply_sort_and_date(self) -> None:
        """Apply sorting and date posted filters."""
        wait_span_click(self.driver, self.config['sort_by'])
        wait_span_click(self.driver, self.config['date_posted'])
        self._buffer_click()

    def _apply_experience_and_company(self) -> None:
        """Apply experience level and company filters."""
        multi_sel_noWait(self.driver, self.config.get('experience_level', []))
        multi_sel_noWait(self.driver, self.config.get('companies', []), self.actions)
        if self.config.get('experience_level') or self.config.get('companies'):
            self._buffer_click()

    def _apply_job_type_and_location(self) -> None:
        """Apply job type and work location filters."""
        multi_sel_noWait(self.driver, self.config.get('job_type', []))
        multi_sel_noWait(self.driver, self.config.get('on_site', []))
        if self.config.get('job_type') or self.config.get('on_site'):
            self._buffer_click()

        if self.config.get('easy_apply_only', False):
            boolean_button_click(self.driver, self.actions, "Easy Apply")

    def _apply_misc_filters(self) -> None:
        """Apply miscellaneous filters like industry and function."""
        multi_sel_noWait(self.driver, self.config.get('location', []))
        multi_sel_noWait(self.driver, self.config.get('industry', []))
        if self.config.get('location') or self.config.get('industry'):
            self._buffer_click()

        multi_sel_noWait(self.driver, self.config.get('job_function', []))
        multi_sel_noWait(self.driver, self.config.get('job_titles', []))
        if self.config.get('job_function') or self.config.get('job_titles'):
            self._buffer_click()

        # Apply boolean filters
        for filter_name, button_text in [
            ('under_10_applicants', 'Under 10 applicants'),
            ('in_your_network', 'In your network'),
            ('fair_chance_employer', 'Fair Chance Employer')
        ]:
            if self.config.get(filter_name, False):
                boolean_button_click(self.driver, self.actions, button_text)

        wait_span_click(self.driver, self.config.get('salary', ''))
        self._buffer_click()

    def _apply_benefits_and_commitments(self) -> None:
        """Apply benefits and workplace commitment filters."""
        multi_sel_noWait(self.driver, self.config.get('benefits', []))
        multi_sel_noWait(self.driver, self.config.get('commitments', []))
        if self.config.get('benefits') or self.config.get('commitments'):
            self._buffer_click()

    def _show_results(self) -> None:
        """Click the show results button to apply filters."""
        show_results_button = self.driver.find_element(
            By.XPATH,
            '//button[contains(@aria-label, "Apply current filters to show")]'
        )
        show_results_button.click()

    def _handle_filter_confirmation(self) -> None:
        """Handle confirmation dialog after applying filters."""
        import pyautogui
        response = pyautogui.confirm(
            "These are your configured search results and filter. "
            "It is safe to change them while this dialog is open, "
            "any changes later could result in errors and skipping this search run.",
            "Please check your results",
            ["Turn off Pause after search", "Look's good, Continue"]
        )
        if response == "Turn off Pause after search":
            self.config['pause_after_filters'] = False

    def _buffer_click(self) -> None:
        """Add delay between clicks if configured."""
        from time import sleep
        recommended_wait = 1 if self.config.get('click_gap', 0) < 1 else 0
        if recommended_wait:
            sleep(recommended_wait)
