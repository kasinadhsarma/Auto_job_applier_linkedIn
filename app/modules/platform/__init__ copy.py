"""
Platform-specific implementations for job application automation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from datetime import datetime, timedelta
import json
import os

from modules.platforms.linkedin import LinkedInPlatform
from modules.platforms.indeed import IndeedPlatform

__all__ = ['LinkedInPlatform', 'IndeedPlatform']

class DailyLimitError(Exception):
    """Raised when a platform hits its daily application limit"""
    pass

class JobPlatform(ABC):
    """Base class for all job platforms"""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.jobs_applied = 0
        self.jobs_failed = 0
        self.jobs_skipped = 0
        self.daily_limit_reached = False
        self.platform_name = self.__class__.__name__.replace('Platform', '')
        self._load_platform_state()
        
    def _load_platform_state(self):
        """Load platform state from disk"""
        try:
            state_file = f"platform_state_{self.platform_name.lower()}.json"
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    last_reset = datetime.fromisoformat(state['last_reset'])
                    if datetime.now() - last_reset > timedelta(days=1):
                        # Reset daily counters if more than 24 hours passed
                        self._reset_daily_counts()
                    else:
                        self.jobs_applied = state['jobs_applied']
        except:
            self._reset_daily_counts()
            
    def _save_platform_state(self):
        """Save platform state to disk"""
        try:
            state = {
                'last_reset': datetime.now().isoformat(),
                'jobs_applied': self.jobs_applied
            }
            state_file = f"platform_state_{self.platform_name.lower()}.json"
            with open(state_file, 'w') as f:
                json.dump(state, f)
        except:
            pass
            
    def _reset_daily_counts(self):
        """Reset daily application counters"""
        self.jobs_applied = 0
        self.daily_limit_reached = False
        self._save_platform_state()
        
    def check_daily_limit(self, platform_limit: int) -> None:
        """Check if daily application limit is reached"""
        if self.jobs_applied >= platform_limit:
            self.daily_limit_reached = True
            self._save_platform_state()
            raise DailyLimitError(f"{self.platform_name} daily limit reached ({platform_limit} applications)")
            
    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """Login to the platform"""
        pass
        
    @abstractmethod
    def search_jobs(self, keywords: List[str], location: str) -> None:
        """Search for jobs with given keywords and location"""
        pass
        
    @abstractmethod
    def apply_filters(self) -> None:
        """Apply search filters like experience, job type etc."""
        pass
        
    @abstractmethod
    def get_job_listings(self) -> List[Dict]:
        """Get list of jobs from current page"""
        pass
        
    @abstractmethod
    def get_job_details(self, job: Dict) -> Optional[Dict]:
        """Get full details of a specific job"""
        pass
        
    @abstractmethod
    def apply_to_job(self, job_details: Dict) -> str:
        """Apply to a specific job. Returns 'success', 'failed' or 'skipped'"""
        pass
        
    @abstractmethod
    def get_next_page(self) -> bool:
        """Move to next page of results. Returns True if successful."""
        pass

    def is_company_verified(self, company_name: str) -> bool:
        """Check if company is verified/legitimate"""
        # Implement company verification logic
        pass

    def is_job_relevant(self, job_details: Dict) -> bool:
        """Check if job matches user's preferences and requirements"""
        # Implement job matching logic
        pass

    def prepare_application(self, job_details: Dict) -> Dict:
        """Prepare application details based on job requirements"""
        # Implement application preparation logic
        pass

    def track_application(self, job_details: Dict, status: str) -> None:
        """Track application status and update metrics"""
        # Implement application tracking logic
        pass

    def get_platform_status(self) -> Tuple[bool, int]:
        """Get platform availability status and applications remaining"""
        # Each platform can override this with specific logic
        daily_limit = 100  # Default limit
        remaining = daily_limit - self.jobs_applied
        return not self.daily_limit_reached, remaining
