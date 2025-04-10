"""Smart job filtering and prioritization system"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config.search import (
    about_company_good_words,
    about_company_bad_words,
    bad_words,
    current_experience
)

class JobFilter:
    def __init__(self):
        self.blacklisted_companies = set()
        self.skipped_jobs = set()
        
    def is_job_suitable(self, job_details: Dict) -> bool:
        """Check if a job posting is suitable based on configured criteria"""
        
        # Skip if already processed
        if job_details['id'] in self.skipped_jobs:
            return False
            
        # Skip blacklisted companies
        if job_details['company'] in self.blacklisted_companies:
            return False
            
        # Check company description for blacklist words
        company_info = job_details.get('company_info', '').lower()
        if any(word.lower() in company_info for word in about_company_bad_words):
            if not any(word.lower() in company_info for word in about_company_good_words):
                self.blacklisted_companies.add(job_details['company'])
                return False
                
        # Check job description for bad words
        description = job_details.get('description', '').lower()
        if any(word.lower() in description for word in bad_words):
            return False
            
        # Check experience requirements
        if current_experience >= 0:
            required_exp = job_details.get('experience_required', 0)
            if required_exp and required_exp > current_experience:
                return False
                
        return True
        
    def prioritize_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Prioritize jobs based on various factors"""
        
        def get_job_score(job: Dict) -> float:
            score = 0.0
            
            # Prefer jobs with Easy Apply
            if job.get('easy_apply', False):
                score += 2.0
                
            # Prefer recently posted jobs
            posted_date = job.get('date_posted')
            if posted_date:
                days_old = (datetime.now() - posted_date).days
                if days_old <= 1:
                    score += 1.5
                elif days_old <= 3:
                    score += 1.0
                elif days_old <= 7:
                    score += 0.5
                    
            # Prefer jobs matching experience level
            if current_experience >= 0:
                required_exp = job.get('experience_required', 0)
                if required_exp and required_exp <= current_experience:
                    score += 1.0
                    
            # Prefer jobs from good companies
            company_info = job.get('company_info', '').lower()
            if any(word.lower() in company_info for word in about_company_good_words):
                score += 1.0
                
            # Prefer jobs with fewer applicants
            applicants = job.get('applicant_count', 0)
            if applicants < 10:
                score += 1.0
            elif applicants < 25:
                score += 0.5
                
            return score
            
        # Sort jobs by score in descending order
        return sorted(jobs, key=get_job_score, reverse=True)
        
    def track_skipped_job(self, job_id: str) -> None:
        """Track skipped jobs to avoid reprocessing"""
        self.skipped_jobs.add(job_id)
        
    def track_blacklisted_company(self, company: str) -> None:
        """Track blacklisted companies"""
        self.blacklisted_companies.add(company)
