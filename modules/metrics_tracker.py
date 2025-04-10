"""Application metrics and tracking system"""

import csv
from datetime import datetime
from typing import Dict, List
import os
from pathlib import Path

class MetricsTracker:
    def __init__(self, base_dir: str = "all excels"):
        self.base_dir = Path(base_dir)
        self.applied_file = self.base_dir / "all_applied_applications_history.csv"
        self.failed_file = self.base_dir / "all_failed_applications_history.csv"
        self._ensure_files()
        
    def _ensure_files(self) -> None:
        """Ensure required files and directories exist"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create files if they don't exist and add headers
        if not self.applied_file.exists():
            self._create_applied_file()
        if not self.failed_file.exists():
            self._create_failed_file()
            
    def _create_applied_file(self) -> None:
        """Create applied applications tracking file with headers"""
        headers = [
            'Job ID', 'Title', 'Company', 'Work Location', 'Work Style',
            'About Job', 'Experience required', 'Skills required',
            'HR Name', 'HR Link', 'Resume', 'Re-posted',
            'Date Posted', 'Date Applied', 'Job Link',
            'External Job link', 'Questions Found', 'Connect Request'
        ]
        with open(self.applied_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
    def _create_failed_file(self) -> None:
        """Create failed applications tracking file with headers"""
        headers = [
            'Job ID', 'Error', 'Exception Details', 'Resume',
            'Date Listed', 'Job Link', 'External Job Link',
            'Screenshot', 'Date Failed'
        ]
        with open(self.failed_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
    def track_successful_application(self, application_data: Dict) -> None:
        """Track a successful job application"""
        try:
            with open(self.applied_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'Job ID', 'Title', 'Company', 'Work Location', 'Work Style',
                    'About Job', 'Experience required', 'Skills required',
                    'HR Name', 'HR Link', 'Resume', 'Re-posted',
                    'Date Posted', 'Date Applied', 'Job Link',
                    'External Job link', 'Questions Found', 'Connect Request'
                ])
                writer.writerow(application_data)
        except Exception as e:
            print(f"Error tracking successful application: {e}")
            
    def track_failed_application(self, failure_data: Dict) -> None:
        """Track a failed job application"""
        try:
            with open(self.failed_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'Job ID', 'Error', 'Exception Details', 'Resume',
                    'Date Listed', 'Job Link', 'External Job Link',
                    'Screenshot', 'Date Failed'
                ])
                failure_data['Date Failed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow(failure_data)
        except Exception as e:
            print(f"Error tracking failed application: {e}")
            
    def get_application_stats(self) -> Dict:
        """Get statistics about applications"""
        stats = {
            'total_applied': 0,
            'total_failed': 0,
            'success_rate': 0,
            'companies': set(),
            'skills': set()
        }
        
        # Count successful applications
        try:
            with open(self.applied_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stats['total_applied'] += 1
                    stats['companies'].add(row['Company'])
                    if row['Skills required'] and row['Skills required'] != 'In Development':
                        skills = eval(row['Skills required'])
                        stats['skills'].update(skills)
        except Exception as e:
            print(f"Error reading applied applications: {e}")
            
        # Count failed applications
        try:
            with open(self.failed_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                stats['total_failed'] = sum(1 for _ in reader)
        except Exception as e:
            print(f"Error reading failed applications: {e}")
            
        # Calculate success rate
        total = stats['total_applied'] + stats['total_failed']
        if total > 0:
            stats['success_rate'] = (stats['total_applied'] / total) * 100
            
        return stats
