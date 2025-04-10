"""
Tracking service module for application metrics and history.
"""
from datetime import datetime
from typing import Dict, Any, Optional

from .metrics import MetricsTracker

class ApplicationStatus:
    """Application status constants."""
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLACKLISTED = "blacklisted"

class TrackingService:
    """Service for tracking application metrics and history."""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = MetricsTracker(config.get('data_dir', 'data'))
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")

    def start_session(self) -> None:
        """Start a new tracking session."""
        self.metrics.increment_run_count()

    def track_application(self, job_details: Dict[str, Any], 
                        status: str, error: Optional[str] = None) -> None:
        """Track a job application attempt."""
        if status == ApplicationStatus.APPLIED:
            self.metrics.record_application(
                job_details,
                "easy_apply" if job_details.get('easy_apply', True) else "external"
            )
        elif status == ApplicationStatus.FAILED:
            self.metrics.record_failure(job_details, error or "Unknown error")
        elif status == ApplicationStatus.SKIPPED:
            self.metrics.record_skip(error or "No reason provided")

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session."""
        return self.metrics.get_stats()

__all__ = ['MetricsTracker', 'ApplicationStatus', 'TrackingService']
