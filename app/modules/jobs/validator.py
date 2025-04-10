"""
Job validator module for validating jobs against configured criteria.
"""
from typing import Dict, Any, List, Set, Tuple, Optional
from app.modules.utils.logging import print_lg

class JobValidator:
    def __init__(self, config: Dict[str, Any]):
        """Initialize job validator with configuration."""
        self.config = config
        self.bad_words = set(config.get('bad_words', []))
        self.good_words = set(config.get('about_company_good_words', []))
        self.security_clearance_required = config.get('security_clearance', False)
        self.current_experience = config.get('current_experience', -1)
        self.did_masters = config.get('did_masters', False)

    def validate_job(self, job_details: Dict[str, Any],
                    applied_jobs: Set[str],
                    rejected_jobs: Set[str],
                    blacklisted_companies: Set[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate job against all criteria.
        Returns: (is_valid, rejection_reason)
        """
        # Check if already processed
        if not self._check_job_status(
            job_details['job_id'],
            job_details['company'],
            applied_jobs,
            rejected_jobs,
            blacklisted_companies
        ):
            return False, "Job already processed or company blacklisted"

        # Validate description
        if 'description' in job_details:
            is_valid, reason = self._validate_description(job_details['description'])
            if not is_valid:
                return False, reason

        return True, None

    def _check_job_status(self, job_id: str, company: str,
                         applied_jobs: Set[str],
                         rejected_jobs: Set[str],
                         blacklisted_companies: Set[str]) -> bool:
        """Check if job has been previously processed."""
        if job_id in applied_jobs:
            print_lg(f"Already applied to job ID: {job_id}")
            return False

        if job_id in rejected_jobs:
            print_lg(f"Previously rejected job ID: {job_id}")
            return False

        if company in blacklisted_companies:
            print_lg(f"Company {company} is blacklisted")
            return False

        return True

    def validate_company(self, about_company: str) -> Tuple[bool, Optional[str]]:
        """
        Validate company information against criteria.
        Returns: (is_valid, rejection_reason)
        """
        about_company_lower = about_company.lower()

        # Check for good words that bypass other checks
        for word in self.good_words:
            if word.lower() in about_company_lower:
                print_lg(f'Found good word "{word}". Skipping other validation.')
                return True, None

        # Check for bad words
        for word in self.bad_words:
            if word.lower() in about_company_lower:
                return False, f'Found bad word "{word}" in company description'

        return True, None

    def _validate_description(self, description: str) -> Tuple[bool, Optional[str]]:
        """
        Validate job description against criteria.
        Returns: (is_valid, rejection_reason)
        """
        description_lower = description.lower()

        # Check for bad words
        for word in self.bad_words:
            if word.lower() in description_lower:
                return False, f'Found bad word "{word}" in job description'

        # Check for security clearance requirement
        if not self.security_clearance_required:
            clearance_terms = {'polygraph', 'clearance', 'secret'}
            if any(term in description_lower for term in clearance_terms):
                return False, "Security clearance required"

        return True, None

    def validate_experience(self, required_experience: int) -> Tuple[bool, Optional[str]]:
        """
        Validate experience requirements.
        Returns: (is_valid, rejection_reason)
        """
        if self.current_experience == -1:  # No experience validation needed
            return True, None

        # Add bonus years for masters degree
        total_experience = self.current_experience
        if self.did_masters:
            total_experience += 2

        if required_experience > total_experience:
            return False, (f"Required experience ({required_experience} years) exceeds "
                         f"current experience ({total_experience} years)")

        return True, None

    def validate_work_style(self, work_style: str) -> bool:
        """Validate work style against preferences."""
        preferred_styles = self.config.get('preferred_work_styles', [])
        if not preferred_styles:  # No preferences set
            return True
        
        return work_style in preferred_styles

    def validate_location(self, location: str) -> bool:
        """Validate job location against preferences."""
        preferred_locations = self.config.get('preferred_locations', [])
        if not preferred_locations:  # No location preferences set
            return True

        location_lower = location.lower()
        return any(loc.lower() in location_lower for loc in preferred_locations)

    def validate_title(self, title: str) -> bool:
        """Validate job title against preferences and exclusions."""
        excluded_titles = self.config.get('excluded_titles', [])
        if any(excluded.lower() in title.lower() for excluded in excluded_titles):
            return False

        preferred_titles = self.config.get('preferred_titles', [])
        if not preferred_titles:  # No title preferences set
            return True

        return any(preferred.lower() in title.lower() for preferred in preferred_titles)

    def get_validation_score(self, job_details: Dict[str, Any]) -> float:
        """
        Calculate a validation score for the job.
        Returns a score between 0 and 1, where 1 is the best match.
        """
        score = 0.0
        weights = {
            'title': 0.3,
            'location': 0.2,
            'work_style': 0.2,
            'experience': 0.3
        }

        if self.validate_title(job_details['title']):
            score += weights['title']

        if self.validate_location(job_details['work_location']):
            score += weights['location']

        if self.validate_work_style(job_details['work_style']):
            score += weights['work_style']

        if 'experience_required' in job_details:
            is_valid, _ = self.validate_experience(job_details['experience_required'])
            if is_valid:
                score += weights['experience']

        return score
