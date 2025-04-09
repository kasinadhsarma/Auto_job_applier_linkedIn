'''
Author:     Kasinadh Sarma
Copyright (C) 2024 

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html

version:    24.04.09.22.00
'''

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from typing import List, Literal, Dict
from selenium.webdriver.remote.webelement import WebElement

from modules.platforms import JobPlatform
from modules.helpers import buffer, print_lg
from modules.clickers_and_finders import (
    wait_span_click, multi_sel_noWait, boolean_button_click,
    find_by_class, scroll_to_view, text_input_by_ID, try_xp
)
from config.settings import click_gap
from config.search import (
    experience_level, companies, job_type, on_site,
    location, industry, job_function, job_titles,
    benefits, commitments, easy_apply_only,
    under_10_applicants, in_your_network, fair_chance_employer
)

class LinkedInPlatform(JobPlatform):
    def login(self, username: str, password: str) -> bool:
        """Login to LinkedIn"""
        self.driver.get("https://www.linkedin.com/login")
        try:
            text_input_by_ID(self.driver, "username", username)
            text_input_by_ID(self.driver, "password", password)
            self.driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
            
            # Wait for successful login
            WebDriverWait(self.driver, 5).until(EC.url_to_be("https://www.linkedin.com/feed/"))
            return True
        except Exception as e:
            print_lg("LinkedIn login failed:", e)
            return False

    def search_jobs(self, keywords: List[str], location: str) -> None:
        """Search for jobs on LinkedIn"""
        for keyword in keywords:
            self.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={keyword}")
            if location:
                try:
                    location_input = try_xp(self.driver, ".//input[@aria-label='City, state, or zip code'and not(@disabled)]", False)
                    location_input.clear()
                    location_input.send_keys(location)
                except Exception as e:
                    print_lg("Failed to set location:", e)

    def apply_filters(self) -> None:
        """Apply LinkedIn job search filters"""
        try:
            # Open filters dialog
            self.driver.find_element(By.XPATH, '//button[normalize-space()="All filters"]').click()
            buffer(click_gap)

            # Apply experience level filter
            multi_sel_noWait(self.driver, experience_level)
            
            # Apply company filter  
            multi_sel_noWait(self.driver, companies)

            # Apply job type filter
            multi_sel_noWait(self.driver, job_type)
            
            # Apply on-site/remote filter
            multi_sel_noWait(self.driver, on_site)

            # Apply Easy Apply filter
            if easy_apply_only:
                boolean_button_click(self.driver, None, "Easy Apply")

            # Apply location filter
            multi_sel_noWait(self.driver, location)
            
            # Apply industry filter
            multi_sel_noWait(self.driver, industry)

            # Apply function filter
            multi_sel_noWait(self.driver, job_function)
            
            # Apply job titles filter
            multi_sel_noWait(self.driver, job_titles)

            # Apply other boolean filters
            if under_10_applicants:
                boolean_button_click(self.driver, None, "Under 10 applicants")
            if in_your_network:
                boolean_button_click(self.driver, None, "In your network")
            if fair_chance_employer:
                boolean_button_click(self.driver, None, "Fair Chance Employer")

            # Apply benefits filter
            multi_sel_noWait(self.driver, benefits)
            
            # Apply commitments filter
            multi_sel_noWait(self.driver, commitments)

            # Show filtered results
            self.driver.find_element(By.XPATH, '//button[contains(@aria-label, "Apply current filters to show")]').click()

        except Exception as e:
            print_lg("Failed to apply filters:", e)

    def get_job_listings(self) -> List[WebElement]:
        """Get job listings from current page"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]"))
            )
            return self.driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")
        except Exception as e:
            print_lg("Failed to get job listings:", e)
            return []

    def get_job_details(self, job: WebElement) -> Dict:
        """Extract job details from LinkedIn job element"""
        try:
            job_link = job.find_element(By.TAG_NAME, 'a')
            scroll_to_view(self.driver, job_link, True)
            
            job_id = job.get_dom_attribute('data-occludable-job-id')
            title = job_link.text.split('\n')[0]
            
            details = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
            company_end = details.find(' · ')
            company = details[:company_end]
            
            location_details = details[company_end + 3:]
            work_style = location_details[location_details.rfind('(')+1:location_details.rfind(')')]
            location = location_details[:location_details.rfind('(')].strip()

            return {
                'id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'work_style': work_style,
                'link': f"https://www.linkedin.com/jobs/view/{job_id}"
            }

        except Exception as e:
            print_lg("Failed to extract job details:", e)
            return {}

    def apply_to_job(self, job: Dict) -> Literal["success", "failed", "skipped"]:
        """Apply to a job on LinkedIn"""
        if job['company'] in self.blacklisted_companies:
            return "skipped"
            
        if job['id'] in self.applied_jobs:
            return "skipped"

        try:
            # Check for Easy Apply button
            easy_apply = try_xp(self.driver, 
                ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3') and contains(@aria-label, 'Easy')]")
            
            if easy_apply:
                modal = find_by_class(self.driver, "jobs-easy-apply-modal")
                if not self.answer_questions(modal):
                    return "failed"
                
                # Submit application
                if wait_span_click(self.driver, "Submit application", 2, scrollTop=True):
                    wait_span_click(self.driver, "Done", 2)
                    return "success"
                    
            return "failed"

        except Exception as e:
            print_lg(f"Failed to apply to job {job['id']}:", e)
            return "failed"

    def answer_questions(self, form: WebElement) -> bool:
        """Answer LinkedIn application form questions"""
        try:
            questions = form.find_elements(By.XPATH, ".//div[@data-test-form-element]")
            for question in questions:
                # Handle different question types (select, radio, text, etc)
                if try_xp(question, ".//select", False):
                    self._handle_select_question(question)
                elif try_xp(question, ".//input[@type='text']", False):
                    self._handle_text_question(question)
                elif try_xp(question, ".//textarea", False):
                    self._handle_textarea_question(question)
                    
            return True

        except Exception as e:
            print_lg("Failed to answer questions:", e)
            return False

    def upload_resume(self, form: WebElement, resume_path: str) -> bool:
        """Upload resume to LinkedIn application"""
        try:
            form.find_element(By.NAME, "file").send_keys(resume_path)
            return True
        except Exception as e:
            print_lg("Failed to upload resume:", e)
            return False

    def get_next_page(self) -> bool:
        """Navigate to next page of LinkedIn job results"""
        try:
            pagination = self.driver.find_element(
                By.CLASS_NAME, "artdeco-pagination__pages"
            )
            current_page = int(
                pagination.find_element(
                    By.XPATH, "//button[contains(@class, 'active')]"
                ).text
            )
            next_button = pagination.find_element(
                By.XPATH, f"//button[@aria-label='Page {current_page + 1}']"
            )
            next_button.click()
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            print_lg("Failed to navigate to next page:", e)
            return False

    def _handle_select_question(self, question: WebElement) -> None:
        """Handle dropdown select questions"""
        pass  # Implementation needed

    def _handle_text_question(self, question: WebElement) -> None:
        """Handle text input questions"""
        pass  # Implementation needed

    def _handle_textarea_question(self, question: WebElement) -> None:
        """Handle textarea questions"""
        pass  # Implementation needed