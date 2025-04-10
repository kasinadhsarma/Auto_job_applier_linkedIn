"""
Job data extraction module for parsing and extracting job information.
"""
import re
from typing import Dict, Any, Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from app.modules.utils.element_helpers import scroll_to_view, try_xp
from app.modules.utils.logging import print_lg

class JobDataExtractor:
    def __init__(self):
        """Initialize job data extractor."""
        self.experience_pattern = re.compile(
            r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?',
            re.IGNORECASE
        )

    def extract_job_details(self, job: WebElement) -> Dict[str, Any]:
        """
        Extract main job details from job listing.
        Returns a dictionary containing job details.
        """
        job_details_button = job.find_element(By.TAG_NAME, 'a')
        scroll_to_view(job.parent, job_details_button, True)
        
        # Extract basic job information
        job_id = job.get_dom_attribute('data-occludable-job-id')
        title = self._extract_title(job_details_button)
        company, work_location, work_style = self._extract_company_and_location(job)
        
        job_details_button.click()
        
        return {
            'job_id': job_id,
            'title': title,
            'company': company,
            'work_location': work_location,
            'work_style': work_style,
            'url': f"https://www.linkedin.com/jobs/view/{job_id}"
        }

    def _extract_title(self, element: WebElement) -> str:
        """Extract job title from element."""
        title = element.text
        return title[:title.find("\n")] if "\n" in title else title

    def _extract_company_and_location(self, job: WebElement) -> Tuple[str, str, str]:
        """Extract company name and location information."""
        company_details = job.find_element(
            By.CLASS_NAME,
            'artdeco-entity-lockup__subtitle'
        ).text
        
        # Parse company details
        index = company_details.find(' · ')
        company = company_details[:index]
        location_info = company_details[index + 3:]
        
        # Extract work style from location
        work_style = self._extract_work_style(location_info)
        work_location = location_info[:location_info.rfind('(')].strip()
        
        return company, work_location, work_style

    def _extract_work_style(self, location_info: str) -> str:
        """Extract work style from location string."""
        start = location_info.rfind('(') + 1
        end = location_info.rfind(')')
        if start > 0 and end > start:
            return location_info[start:end]
        return "Not specified"

    def extract_job_description(self, driver: WebDriver) -> Tuple[str, Optional[int], bool, Optional[str], Optional[str]]:
        """
        Extract and analyze job description.
        Returns: (description, experience_required, should_skip, skip_reason, skip_message)
        """
        try:
            description = self._get_job_description(driver)
            experience_required = self._extract_years_of_experience(description)
            
            should_skip, skip_reason, skip_message = self._analyze_description(
                description.lower(),
                experience_required
            )
            
            return description, experience_required, should_skip, skip_reason, skip_message
            
        except Exception as e:
            print_lg("Failed to extract job description:", e)
            return "Unknown", "Error in extraction", False, None, None

    def _get_job_description(self, driver: WebDriver) -> str:
        """Get raw job description text."""
        description_element = driver.find_element(
            By.CLASS_NAME,
            "jobs-box__html-content"
        )
        return description_element.text

    def _extract_years_of_experience(self, text: str) -> Optional[int]:
        """Extract years of experience requirement from text."""
        matches = re.findall(self.experience_pattern, text)
        if not matches:
            print_lg("Couldn't find experience requirement in job description")
            return None
            
        # Convert matches to integers and get the maximum value
        years = [int(match) for match in matches if int(match) <= 12]
        return max(years) if years else None

    def _analyze_description(self, description: str, experience_required: Optional[int]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Analyze job description for potential skip conditions.
        Returns: (should_skip, skip_reason, skip_message)
        """
        # This would be expanded based on configuration and business rules
        return False, None, None

    def get_about_company(self, driver: WebDriver) -> Optional[str]:
        """Extract company information."""
        try:
            about_company = driver.find_element(
                By.CLASS_NAME,
                "jobs-company__box"
            )
            scroll_to_view(driver, about_company)
            return about_company.text
        except Exception as e:
            print_lg("Failed to extract company information:", e)
            return None

    def get_hr_info(self, driver: WebDriver, wait_time: int = 2) -> Tuple[str, str]:
        """
        Extract HR/recruiter information.
        Returns: (hr_name, hr_link)
        """
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            hr_card = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "hirer-card__hirer-information")
                )
            )
            
            hr_link = hr_card.find_element(By.TAG_NAME, "a").get_attribute("href")
            hr_name = hr_card.find_element(By.TAG_NAME, "span").text
            
            return hr_name, hr_link
            
        except Exception as e:
            print_lg("Failed to extract HR information:", e)
            return "Unknown", "Unknown"
