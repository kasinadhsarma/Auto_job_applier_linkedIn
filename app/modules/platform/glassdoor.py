'''
Platform implementation for Glassdoor job applications
'''

from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.platforms import JobPlatform
from modules.helpers import print_lg, buffer
from config.settings import click_gap

class GlassdoorPlatform(JobPlatform):
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "https://www.glassdoor.com"
        self.wait = WebDriverWait(driver, 10)
        
    def login(self, username: str, password: str) -> bool:
        """Login to Glassdoor"""
        try:
            self.driver.get(f"{self.base_url}/profile/login_input")
            
            # Handle cookie consent if present
            try:
                cookie_button = self.wait.until(EC.element_to_be_clickable(
                    (By.ID, "onetrust-accept-btn-handler")))
                cookie_button.click()
            except:
                pass

            # Enter email
            email_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "modalUserEmail")))
            email_input.send_keys(username)
            
            continue_button = self.driver.find_element(By.CSS_SELECTOR, 
                "button[data-test='email-form-submit']")
            continue_button.click()
            buffer(click_gap)
            
            # Enter password
            password_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "modalUserPassword")))
            password_input.send_keys(password)
            
            sign_in_button = self.driver.find_element(By.CSS_SELECTOR,
                "button[data-test='password-form-submit']")
            sign_in_button.click()
            buffer(click_gap)
            
            # Verify login success
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-test='profile-menu']")))
            return True
            
        except Exception as e:
            print_lg(f"Glassdoor login failed: {str(e)}")
            return False
            
    def search_jobs(self, keywords: List[str], location: str) -> None:
        """Search for jobs with given keywords and location"""
        try:
            self.driver.get(f"{self.base_url}/Job/jobs.htm")
            
            # Enter keywords
            keyword_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "searchBar-keyword")))
            keyword_input.clear()
            keyword_input.send_keys(", ".join(keywords))
            
            # Enter location if provided
            if location:
                location_input = self.driver.find_element(By.ID, "searchBar-location")
                location_input.clear()
                location_input.send_keys(location)
            
            # Submit search
            search_button = self.driver.find_element(By.CSS_SELECTOR,
                "button[data-test='search-bar-submit']")
            search_button.click()
            buffer(click_gap)
            
        except Exception as e:
            print_lg(f"Job search failed: {str(e)}")
            
    def apply_filters(self) -> None:
        """Apply search filters"""
        try:
            # Date Posted filter
            self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-test='date-posted-filter']"))).click()
            
            # Easy Apply filter
            easy_apply = self.driver.find_element(By.CSS_SELECTOR,
                "[data-test='easy-apply-filter']")
            if not easy_apply.is_selected():
                easy_apply.click()
                
            # Experience Level filter
            exp_filter = self.driver.find_element(By.CSS_SELECTOR,
                "[data-test='experience-level-filter']")
            exp_filter.click()
            
            entry_level = self.driver.find_element(By.CSS_SELECTOR,
                "[data-test='ENTRY_LEVEL-experience-filter']")
            if not entry_level.is_selected():
                entry_level.click()
                
        except Exception as e:
            print_lg(f"Failed to apply filters: {str(e)}")
            
    def get_job_listings(self) -> List[Dict]:
        """Get jobs from current page"""
        jobs = []
        try:
            job_cards = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[data-test='job-link']")))
            
            for card in job_cards:
                job_info = {
                    "id": card.get_attribute("data-id"),
                    "title": card.find_element(By.CSS_SELECTOR, 
                        ".job-title").text,
                    "company": card.find_element(By.CSS_SELECTOR,
                        ".job-company").text,
                    "location": card.find_element(By.CSS_SELECTOR,
                        ".job-location").text,
                    "link": card.get_attribute("href")
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
                ".company-description").text
                
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
                (By.CSS_SELECTOR, "[data-test='apply-button']")))
            apply_button.click()
            buffer(click_gap)
            
            # Fill application form
            self._fill_application_form()
            
            # Submit application
            submit_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-test='submit-application']")))
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
                "[data-test='pagination-next']")
            
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