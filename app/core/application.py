"""
Core application module handling job application logic.
"""
from datetime import datetime
from typing import Set, Tuple, Optional, Dict, Any, List
from selenium.webdriver.remote.webelement import WebElement

from app.core.browser import BrowserManager
from app.core.filters import FilterManager
from app.modules.jobs.validator import JobValidator
from app.modules.jobs.extractor import JobDataExtractor
from app.services.tracking.metrics import MetricsTracker
from app.modules.utils.logging import print_lg

class JobApplication:
    def __init__(self, browser: BrowserManager, config: Dict[str, Any]):
        """Initialize job application manager."""
        self.browser = browser
        self.config = config
        self.metrics = MetricsTracker()
        self.validator = JobValidator(config)
        self.extractor = JobDataExtractor()
        self.filter_manager = FilterManager(browser.driver, config)
        
        self.applied_jobs: Set[str] = set()
        self.rejected_jobs: Set[str] = set()
        self.blacklisted_companies: Set[str] = set()
        
        self.easy_applied_count = 0
        self.external_jobs_count = 0
        self.failed_count = 0
        self.skip_count = 0

    def apply_to_jobs(self, search_terms: List[str]) -> None:
        """
        Main method to handle job application process for given search terms.
        """
        self.applied_jobs = self._load_applied_jobs()
        
        for search_term in search_terms:
            print_lg(f'\n>>>> Now searching for "{search_term}" <<<<\n\n')
            
            # Navigate to jobs search
            self.browser.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={search_term}")
            
            # Apply search filters
            self.filter_manager.apply_filters()
            
            self._process_job_listings()

    def _load_applied_jobs(self) -> Set[str]:
        """Load previously applied job IDs."""
        # TODO: Implement loading applied jobs from history
        return set()

    def _process_job_listings(self) -> None:
        """Process all job listings on current page."""
        current_count = 0
        
        while current_count < self.config['switch_number']:
            # Get job listings
            job_listings = self._get_job_listings()
            if not job_listings:
                break

            for job in job_listings:
                if current_count >= self.config['switch_number']:
                    break

                job_details = self._process_single_job(job)
                if not job_details:
                    continue

                if self._should_skip_job(job_details):
                    continue

                if self._attempt_job_application(job_details):
                    current_count += 1

            if not self._go_to_next_page():
                break

    def _get_job_listings(self) -> List[WebElement]:
        """Get all job listings from current page."""
        try:
            return self.browser.driver.find_elements_by_xpath("//li[@data-occludable-job-id]")
        except Exception as e:
            print_lg("Failed to find job listings")
            return []

    def _process_single_job(self, job: WebElement) -> Optional[Dict[str, Any]]:
        """Extract and process single job listing."""
        try:
            return self.extractor.extract_job_details(job)
        except Exception as e:
            print_lg(f"Failed to process job: {e}")
            return None

    def _should_skip_job(self, job_details: Dict[str, Any]) -> bool:
        """Determine if job should be skipped based on various criteria."""
        if job_details['job_id'] in self.applied_jobs:
            print_lg(f"Already applied to {job_details['title']}")
            return True

        if job_details['company'] in self.blacklisted_companies:
            print_lg(f"Company {job_details['company']} is blacklisted")
            return True

        return False

    def _attempt_job_application(self, job_details: Dict[str, Any]) -> bool:
        """Attempt to apply for a job."""
        try:
            if self._is_easy_apply():
                return self._handle_easy_apply(job_details)
            else:
                return self._handle_external_apply(job_details)
        except Exception as e:
            print_lg(f"Failed to apply: {e}")
            self.failed_count += 1
            return False

    def _is_easy_apply(self) -> bool:
        """Check if job has Easy Apply option."""
        # TODO: Implement Easy Apply check
        return False

    def _handle_easy_apply(self, job_details: Dict[str, Any]) -> bool:
        """Handle Easy Apply process."""
        # TODO: Implement Easy Apply handling
        return False

    def _handle_external_apply(self, job_details: Dict[str, Any]) -> bool:
        """Handle external application process."""
        # TODO: Implement external application handling
        return False

    def _go_to_next_page(self) -> bool:
        """Navigate to next page of job listings."""
        # TODO: Implement pagination
        return False
