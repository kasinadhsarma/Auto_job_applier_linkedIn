"""
Resume management service for handling resume storage and customization.
"""
import os
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...modules.ai.smart_apply import SmartApply
from ...utils.logging import print_lg, error_log

class ResumeManager:
    """Manager for handling resumes and their customization."""
    
    def __init__(self, config: Dict[str, Any], ai_service: Optional[SmartApply] = None):
        """Initialize resume manager with configuration."""
        self.config = config
        self.ai_service = ai_service
        self.resume_dir = config.get('resume_dir', 'data/resumes')
        self.default_resume_path = config.get('default_resume_path')
        
        # Ensure resume directory exists
        os.makedirs(self.resume_dir, exist_ok=True)

    def get_resume(self, job_details: Dict[str, Any]) -> str:
        """
        Get appropriate resume for a job application.
        May return customized resume if AI is enabled.
        """
        if not self.default_resume_path or not os.path.exists(self.default_resume_path):
            raise FileNotFoundError("Default resume not found")

        if not self.ai_service or not self.config.get('use_resume_generator', False):
            return self.default_resume_path

        try:
            return self._create_custom_resume(job_details)
        except Exception as e:
            error_log("Failed to create custom resume", e)
            return self.default_resume_path

    def _create_custom_resume(self, job_details: Dict[str, Any]) -> str:
        """Create a customized resume for specific job."""
        # Read original resume
        with open(self.default_resume_path, 'r', encoding='utf-8') as f:
            original_resume = f.read()

        # Get job details
        job_id = job_details['job_id']
        description = job_details.get('description', '')
        
        # Generate customized content
        customized_content = self.ai_service.customize_resume(
            description,
            original_resume,
            priority=1  # Moderate customization
        )

        # Save customized resume
        custom_resume_path = self._get_custom_resume_path(job_id)
        with open(custom_resume_path, 'w', encoding='utf-8') as f:
            f.write(customized_content)

        return custom_resume_path

    def _get_custom_resume_path(self, job_id: str) -> str:
        """Generate path for custom resume file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"custom_resume_{job_id}_{timestamp}.pdf"
        return os.path.join(self.resume_dir, filename)

    def backup_resume(self) -> Optional[str]:
        """Create a backup of the default resume."""
        if not self.default_resume_path or not os.path.exists(self.default_resume_path):
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(
                self.resume_dir,
                f"backup_{os.path.basename(self.default_resume_path)}_{timestamp}"
            )
            shutil.copy2(self.default_resume_path, backup_path)
            return backup_path
        except Exception as e:
            error_log("Failed to backup resume", e)
            return None

    def cleanup_old_resumes(self, max_age_days: int = 7) -> None:
        """Remove old customized resumes."""
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.resume_dir):
                if filename.startswith('custom_resume_'):
                    file_path = os.path.join(self.resume_dir, filename)
                    file_age = current_time - datetime.fromtimestamp(
                        os.path.getctime(file_path)
                    )
                    
                    if file_age.days > max_age_days:
                        os.remove(file_path)
                        print_lg(f"Removed old resume: {filename}")
        except Exception as e:
            error_log("Failed to cleanup old resumes", e)

    def get_supported_formats(self) -> List[str]:
        """Get list of supported resume formats."""
        return ['.pdf', '.doc', '.docx']

    def validate_resume(self, resume_path: str) -> bool:
        """Validate resume file format and accessibility."""
        if not os.path.exists(resume_path):
            return False

        file_ext = os.path.splitext(resume_path)[1].lower()
        return file_ext in self.get_supported_formats()
