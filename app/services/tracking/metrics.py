"""
Metrics tracking service for monitoring application statistics.
"""
import csv
import os
from datetime import datetime
from typing import Dict, Any, Set, Optional
from dataclasses import dataclass

@dataclass
class ApplicationStats:
    """Data class for application statistics."""
    total_runs: int = 0
    easy_applied_count: int = 0
    external_jobs_count: int = 0
    failed_count: int = 0
    skip_count: int = 0
    daily_limit_reached: bool = False

class MetricsTracker:
    def __init__(self, base_dir: str = "data"):
        """Initialize metrics tracker with base directory."""
        self.base_dir = base_dir
        self.stats = ApplicationStats()
        self.applied_jobs: Set[str] = set()
        
        # Define file paths
        self.history_dir = os.path.join(base_dir, "history")
        self.applied_file = os.path.join(self.history_dir, "applied.csv")
        self.failed_file = os.path.join(self.history_dir, "failed.csv")
        
        self._ensure_directories()
        self._load_applied_jobs()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        os.makedirs(self.history_dir, exist_ok=True)

    def _load_applied_jobs(self) -> None:
        """Load previously applied job IDs."""
        try:
            with open(self.applied_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    self.applied_jobs.add(row[0])  # Job ID is first column
        except FileNotFoundError:
            pass  # File doesn't exist yet

    def record_application(self, job_details: Dict[str, Any], application_type: str) -> None:
        """Record successful job application."""
        # Update statistics
        if application_type == "easy_apply":
            self.stats.easy_applied_count += 1
        else:
            self.stats.external_jobs_count += 1

        # Add to applied jobs set
        self.applied_jobs.add(job_details['job_id'])

        # Record in CSV
        self._write_application_record(job_details)

    def record_failure(self, job_details: Dict[str, Any], error: str,
                      stack_trace: Optional[str] = None) -> None:
        """Record failed application attempt."""
        self.stats.failed_count += 1
        self._write_failure_record(job_details, error, stack_trace)

    def record_skip(self, reason: str) -> None:
        """Record skipped application."""
        self.stats.skip_count += 1

    def _write_application_record(self, job_details: Dict[str, Any]) -> None:
        """Write successful application record to CSV."""
        fieldnames = [
            'Job ID', 'Title', 'Company', 'Work Location', 'Work Style',
            'About Job', 'Experience required', 'Skills required', 
            'HR Name', 'HR Link', 'Resume', 'Re-posted',
            'Date Posted', 'Date Applied', 'Job Link', 'External Job link',
            'Questions Found', 'Connect Request'
        ]

        file_exists = os.path.exists(self.applied_file)
        
        try:
            with open(self.applied_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'Job ID': job_details['job_id'],
                    'Title': job_details['title'],
                    'Company': job_details['company'],
                    'Work Location': job_details['work_location'],
                    'Work Style': job_details['work_style'],
                    'About Job': job_details.get('description', ''),
                    'Experience required': job_details.get('experience_required', ''),
                    'Skills required': job_details.get('skills', ''),
                    'HR Name': job_details.get('hr_name', 'Unknown'),
                    'HR Link': job_details.get('hr_link', 'Unknown'),
                    'Resume': job_details.get('resume', 'Previous resume'),
                    'Re-posted': job_details.get('reposted', False),
                    'Date Posted': job_details.get('date_posted', 'Unknown'),
                    'Date Applied': datetime.now(),
                    'Job Link': job_details['url'],
                    'External Job link': job_details.get('external_url', 'Easy Applied'),
                    'Questions Found': job_details.get('questions', None),
                    'Connect Request': job_details.get('connect_request', 'Not sent')
                })
        except Exception as e:
            from ...utils.logging import print_lg
            print_lg(f"Failed to write application record: {e}")

    def _write_failure_record(self, job_details: Dict[str, Any],
                            error: str, stack_trace: Optional[str]) -> None:
        """Write failure record to CSV."""
        fieldnames = [
            'Job ID', 'Job Link', 'Resume Tried', 'Date listed',
            'Date Tried', 'Assumed Reason', 'Stack Trace',
            'External Job link', 'Screenshot Name'
        ]

        file_exists = os.path.exists(self.failed_file)
        
        try:
            with open(self.failed_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'Job ID': job_details['job_id'],
                    'Job Link': job_details['url'],
                    'Resume Tried': job_details.get('resume', 'Unknown'),
                    'Date listed': job_details.get('date_posted', 'Unknown'),
                    'Date Tried': datetime.now(),
                    'Assumed Reason': error,
                    'Stack Trace': stack_trace,
                    'External Job link': job_details.get('external_url', 'N/A'),
                    'Screenshot Name': job_details.get('screenshot_name', 'Not Available')
                })
        except Exception as e:
            from ...utils.logging import print_lg
            print_lg(f"Failed to write failure record: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current application statistics."""
        return {
            "Total runs": self.stats.total_runs,
            "Jobs Easy Applied": self.stats.easy_applied_count,
            "External job links collected": self.stats.external_jobs_count,
            "Total applied or collected": (self.stats.easy_applied_count +
                                         self.stats.external_jobs_count),
            "Failed jobs": self.stats.failed_count,
            "Irrelevant jobs skipped": self.stats.skip_count,
            "Daily limit reached": self.stats.daily_limit_reached
        }

    def increment_run_count(self) -> None:
        """Increment total run counter."""
        self.stats.total_runs += 1

    def set_daily_limit_reached(self) -> None:
        """Set daily limit reached flag."""
        self.stats.daily_limit_reached = True
