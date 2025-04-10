'''
Platform implementation for Dice.com job applications
'''

from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.platforms import JobPlatform
from modules.helpers import print_lg, buffer
from config.settings import click_gap

class DicePlatform(JobPlatform):
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "https://www.dice.com"
        self.wait = WebDriverWait(driver, 10)
        
    def login(self, username: str, password: str) -> bool:
        """Login to Dice"""
        try:
            self.driver.get(f"{self.base_url}/dashboard/login")
            
            # Enter credentials
            email_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "email")))
            email_input.send_keys(username)
            
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(password)
            
            # Submit login
            sign_in_button = self.driver.find_element(By.CSS_SELECTOR,
                "button[type='submit']")
            sign_in_button.click()
            buffer(click_gap)
            
            # Verify login success
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".user-menu")))
            return True
            
        except Exception as e:
            print_lg(f"Dice login failed: {str(e)}")
            return False
            
    def search_jobs(self, keywords: List[str], location: str) -> None:
        """Search for jobs with given keywords and location"""
        try:
            self.driver.get(f"{self.base_url}/jobs")
            
            # Enter search terms
            search_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "typeaheadInput")))
            search_input.clear()
            search_input.send_keys(", ".join(keywords))
            
            # Enter location
            if location:
                location_input = self.driver.find_element(By.ID, "location")
                location_input.clear()
                location_input.send_keys(location)
            
            # Submit search
            search_button = self.driver.find_element(By.CSS_SELECTOR,
                "button[data-testid='search-button']")
            search_button.click()
            buffer(click_gap)
            
        except Exception as e:
            print_lg(f"Job search failed: {str(e)}")
            
    def apply_filters(self) -> None:
        """Apply search filters"""
        try:
            # Open filters
            filter_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-testid='filter-button']")))
            filter_button.click()
            
            # Job Type filter
            job_type_dropdown = self.driver.find_element(By.ID, "jobType")
            job_type_dropdown.click()
            
            # Select Full-time and Contract
            for job_type in ["Full-time", "Contract"]:
                option = self.driver.find_element(By.XPATH,
                    f"//label[contains(text(), '{job_type}')]")
                option.click()
            
            # Experience Level
            exp_dropdown = self.driver.find_element(By.ID, "experienceLevel")
            exp_dropdown.click()
            
            entry_level = self.driver.find_element(By.XPATH,
                "//label[contains(text(), 'Entry Level')]")
            entry_level.click()
            
            # Apply filters
            apply_button = self.driver.find_element(By.CSS_SELECTOR,
                "[data-testid='apply-filters-button']")
            apply_button.click()
            buffer(click_gap)
            
        except Exception as e:
            print_lg(f"Failed to apply filters: {str(e)}")
            
    def get_job_listings(self) -> List[Dict]:
        """Get jobs from current page"""
        jobs = []
        try:
            job_cards = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[data-testid='job-card']")))
            
            for card in job_cards:
                job_info = {
                    "id": card.get_attribute("data-id"),
                    "title": card.find_element(By.CSS_SELECTOR,
                        ".job-title").text,
                    "company": card.find_element(By.CSS_SELECTOR,
                        ".employer").text,
                    "location": card.find_element(By.CSS_SELECTOR,
                        ".location").text,
                    "link": card.find_element(By.CSS_SELECTOR,
                        "a.card-title-link").get_attribute("href")
                }
                jobs.append(job_info)
                
        except Exception as e:
            print_lg(f"Failed to get job listings: {str(e)}")
            
        return jobs
        
    def get_job_details(self, job: Dict) -> Optional[Dict]:
        """Get full job details"""
        try:
            self.driver.get(job["link"])
            
            description = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".job-description"))).text
                
            company_info = self.driver.find_element(By.CSS_SELECTOR,
                ".company-header").text
                
            return {
                **job,
                "description": description,
                "company_info": company_info
            }
            
        except Exception as e:
            print_lg(f"Failed to get job details: {str(e)}")
            return None
            
    def apply_to_job(self, job_details: Dict) -> str:
        """Apply to a job"""
        try:
            # Find and click apply button
            apply_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-testid='apply-button']")))
            apply_button.click()
            buffer(click_gap)
            
            # Check if external application
            try:
                external_warning = self.driver.find_element(By.CSS_SELECTOR,
                    ".external-application-warning")
                if external_warning.is_displayed():
                    return "skipped"  # Skip external applications
            except:
                pass
            
            # Fill application form
            self._fill_application_form()
            
            # Submit application
            submit_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-testid='submit-application']")))
            submit_button.click()
            buffer(click_gap)
            
            return "success"
            
        except Exception as e:
            print_lg(f"Failed to apply: {str(e)}")
            return "failed"
            
    def get_next_page(self) -> bool:
        """Go to next page of results"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR,
                "[data-testid='next-page']")
            
            if "disabled" in next_button.get_attribute("class"):
                return False
                
            next_button.click()
            buffer(click_gap)
            return True
            
        except:
            return False
            
    def _fill_application_form(self):
        """Helper to fill out application forms"""
        # Implementation for filling common form fields
        pass