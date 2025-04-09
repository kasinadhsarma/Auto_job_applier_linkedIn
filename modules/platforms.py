'''
Author:     Kasinadh Sarma
Copyright (C) 2024 

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html

version:    24.04.09.22.00
'''

from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import Literal, List, Dict, Set, Optional

class JobPlatform(ABC):
    """Base class for job platforms like LinkedIn, Indeed, etc."""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.applied_jobs: Set[str] = set()
        self.rejected_jobs: Set[str] = set()
        self.blacklisted_companies: Set[str] = set()
    
    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """Login to the platform. Returns True if successful."""
        pass
        
    @abstractmethod
    def search_jobs(self, keywords: List[str], location: str) -> None:
        """Search for jobs using keywords and location"""
        pass
        
    @abstractmethod
    def apply_filters(self) -> None:
        """Apply job search filters specific to the platform"""
        pass
        
    @abstractmethod
    def get_job_listings(self) -> List[WebElement]:
        """Get list of job elements from current page"""
        pass
        
    @abstractmethod
    def get_job_details(self, job: WebElement) -> Dict:
        """Extract job details from job element"""
        pass
        
    @abstractmethod
    def apply_to_job(self, job: Dict) -> Literal["success", "failed", "skipped"]:
        """Apply to a specific job"""
        pass
        
    @abstractmethod
    def answer_questions(self, form: WebElement) -> bool:
        """Answer application questions"""
        pass

    @abstractmethod
    def upload_resume(self, form: WebElement, resume_path: str) -> bool:
        """Upload resume during application"""
        pass

    @abstractmethod
    def get_next_page(self) -> bool:
        """Navigate to next page of results. Returns False if no more pages."""
        pass

    def save_application_data(self, job_data: Dict) -> None:
        """Save application data to CSV"""
        pass

    def save_failed_application(self, job_data: Dict, error: str) -> None:
        """Save failed application data"""
        pass