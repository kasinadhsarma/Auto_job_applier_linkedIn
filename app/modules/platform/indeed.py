'''
Author:     Kasinadh Sarma
Copyright (C) 2024 

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html

version:    24.04.09.22.00
'''

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import NoSuchElementException
from typing import List, Dict, Literal, Optional, Tuple
from selenium.webdriver.remote.webelement import WebElement
from modules.platforms import JobPlatform, DailyLimitError
from modules.helpers import buffer, print_lg
from config.settings import click_gap

class IndeedPlatform(JobPlatform):
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "https://www.indeed.com"
        self.wait = WebDriverWait(driver, 10)
        self.DAILY_LIMIT = 150  # Indeed typically allows more applications per day
        
    def login(self, username: str, password: str) -> bool:
        """Login to Indeed"""
        try:
            self.driver.get(f"{self.base_url}/account/login")
            
            # Enter email
            email_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "ifl-InputFormField-3")))
            email_input.send_keys(username)
            
            # Click continue
            continue_button = self.driver.find_element(By.CSS_SELECTOR,
                "button[type='submit']")
            continue_button.click()
            buffer(click_gap)
            
            # Enter password
            password_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "ifl-InputFormField-7")))
            password_input.send_keys(password)
            
            # Submit login
            sign_in_button = self.driver.find_element(By.CSS_SELECTOR,
                "button[type='submit']")
            sign_in_button.click()
            buffer(click_gap)
            
            # Verify login success
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-testid='user-menu']")))
            return True
            
        except Exception as e:
            print_lg(f"Indeed login failed: {str(e)}")
            return False
            
    def search_jobs(self, keywords: List[str], location: str) -> None:
        """Search for jobs with given keywords and location"""
        try:
            self.driver.get(self.base_url)
            
            # Enter keywords
            what_input = self.wait.until(EC.presence_of_element_located(
                (By.ID, "text-input-what")))
            what_input.clear()
            what_input.send_keys(", ".join(keywords))
            
            # Enter location if provided
            if location:
                where_input = self.driver.find_element(By.ID, "text-input-where")
                where_input.clear()
                where_input.send_keys(location)
            
            # Submit search
            search_button = self.driver.find_element(By.CSS_SELECTOR,
                "button[type='submit']")
            search_button.click()
            buffer(click_gap)
            
        except Exception as e:
            print_lg(f"Job search failed: {str(e)}")
            
    def apply_filters(self) -> None:
        """Apply search filters"""
        try:
            # Date Posted filter
            date_filter = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "filter-dateposted")))
            date_filter.click()
            
            # Experience Level filter
            exp_filter = self.driver.find_element(By.ID, "filter-explvl")
            exp_filter.click()
            
            entry_level = self.driver.find_element(By.CSS_SELECTOR,
                "[data-testid='filter-explvl-entry_level']")
            entry_level.click()
            
            # Job Type filter
            job_type = self.driver.find_element(By.ID, "filter-jobtype")
            job_type.click()
            
            fulltime = self.driver.find_element(By.CSS_SELECTOR,
                "[data-testid='filter-jobtype-fulltime']")
            fulltime.click()
            
        except Exception as e:
            print_lg(f"Failed to apply filters: {str(e)}")
            
    def get_job_listings(self) -> List[Dict]:
        """Get jobs from current page"""
        jobs = []
        try:
            job_cards = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".job_seen_beacon")))
            
            for card in job_cards:
                try:
                    job_info = {
                        "id": card.get_attribute("data-jk"),
                        "title": card.find_element(By.CSS_SELECTOR,
                            ".jobTitle").text,
                        "company": card.find_element(By.CSS_SELECTOR,
                            ".companyName").text,
                        "location": card.find_element(By.CSS_SELECTOR,
                            ".companyLocation").text,
                        "link": card.find_element(By.CSS_SELECTOR,
                            "h2 a").get_attribute("href")
                    }
                    jobs.append(job_info)
                except:
                    continue
                    
        except Exception as e:
            print_lg(f"Failed to get job listings: {str(e)}")
            
        return jobs
        
    def get_job_details(self, job: Dict) -> Optional[Dict]:
        """Get full job details"""
        try:
            self.driver.get(job["link"])
            
            description = self.wait.until(EC.presence_of_element_located(
                (By.ID, "jobDescriptionText"))).text
                
            company_info = ""
            try:
                company_info = self.driver.find_element(By.ID,
                    "companyInfoText").text
            except:
                pass
                
            return {
                **job,
                "description": description,
                "company_info": company_info
            }
            
        except Exception as e:
            print_lg(f"Failed to get job details: {str(e)}")
            return None
            
    def apply_to_job(self, job_details: Dict) -> str:
        """Apply to a job with limit checking"""
        try:
            # Check limits before attempting application
            self.check_application_blocked()
            self.check_daily_limit(self.DAILY_LIMIT)
            
            # Find and click apply button
            apply_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".jobsearch-IndeedApplyButton-newDesign")))
            apply_button.click()
            buffer(click_gap)
            
            # Switch to application iframe
            iframe = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#indeedapply-modal iframe")))
            self.driver.switch_to.frame(iframe)
            
            # Fill application form
            self._fill_application_form()
            
            # Submit application
            continue_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='continue-button']")))
            continue_button.click()
            buffer(click_gap)
            
            submit_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='submit-application-button']")))
            submit_button.click()
            buffer(click_gap)
            
            # Switch back to main content
            self.driver.switch_to.default_content()
            
            # Check for post-application limit warnings
            self.check_application_blocked()
            
            return "success"
            
        except DailyLimitError:
            self.daily_limit_reached = True
            raise
            
        except Exception as e:
            print_lg(f"Failed to apply: {str(e)}")
            # Switch back to main content in case of error
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return "failed"
            
    def get_next_page(self) -> bool:
        """Go to next page of results"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR,
                "[aria-label='Next Page']")
            
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
        
    def get_platform_status(self) -> Tuple[bool, int]:
        """Get Indeed-specific platform status"""
        try:
            # Check for any Indeed-specific limit indicators
            if self.driver.current_url.startswith(self.base_url):
                try:
                    limit_warning = self.driver.find_element(By.CSS_SELECTOR, 
                        ".job-alert-popup")
                    if "limit" in limit_warning.text.lower():
                        self.daily_limit_reached = True
                        return False, 0
                except:
                    pass
            
            remaining = self.DAILY_LIMIT - self.jobs_applied
            return not self.daily_limit_reached, remaining
            
        except Exception as e:
            print_lg(f"Error checking Indeed status: {str(e)}")
            return True, self.DAILY_LIMIT  # Default to available if check fails
            
    def check_application_blocked(self):
        """Check if Indeed is showing application limit warnings"""
        try:
            # Check for various Indeed limit indicators
            limit_indicators = [
                ".job-alert-popup",
                "[data-testid='error-message']",
                ".application-limit-warning"
            ]
            
            for selector in limit_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if any(word in element.text.lower() for word in 
                        ["limit", "maximum", "too many", "try again"]):
                        raise DailyLimitError("Indeed daily limit reached")
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            if "daily limit" in str(e).lower():
                raise