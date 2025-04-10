'''
Author:     Kasinadh Sarma
Copyright (C) 2024

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html

version:    24.04.09.22.00
'''

import os
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from modules.ai.openaiConnections import ai_generate_resume
from modules.helpers import print_lg
from config.questions import default_resume_path

@dataclass
class Resume:
    """Represents a resume with its metadata"""
    path: str
    platform: str
    job_id: str
    created_at: datetime
    customized: bool = False

class ResumeManager:
    """Manages resumes across different job platforms"""
    
    def __init__(self, base_dir: str = "all resumes"):
        self.base_dir = base_dir
        self.resume_cache: Dict[str, Resume] = {}
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Ensure required directories exist"""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "temp"), exist_ok=True)
        for platform in ["linkedin", "indeed"]:
            os.makedirs(os.path.join(self.base_dir, platform), exist_ok=True)

    def get_resume_for_job(
        self, 
        platform: str,
        job_id: str,
        job_description: str = "",
        customize: bool = False
    ) -> Optional[Resume]:
        """Get an appropriate resume for a job application"""
        # Check if we already have a customized resume for this job
        cache_key = f"{platform}_{job_id}"
        if cache_key in self.resume_cache:
            return self.resume_cache[cache_key]

        # If customization is requested and we have a job description
        if customize and job_description:
            try:
                # Generate customized resume using AI
                resume_path = os.path.join(
                    self.base_dir,
                    platform,
                    f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )
                
                if ai_generate_resume(job_description, resume_path):
                    resume = Resume(
                        path=resume_path,
                        platform=platform,
                        job_id=job_id,
                        created_at=datetime.now(),
                        customized=True
                    )
                    self.resume_cache[cache_key] = resume
                    return resume
            except Exception as e:
                print_lg(f"Failed to generate custom resume: {e}")

        # Fall back to default resume
        if os.path.exists(default_resume_path):
            resume = Resume(
                path=default_resume_path,
                platform=platform,
                job_id=job_id,
                created_at=datetime.now(),
                customized=False
            )
            self.resume_cache[cache_key] = resume
            return resume

        return None

    def cleanup_old_resumes(self, max_age_days: int = 7) -> None:
        """Remove old temporary resumes"""
        now = datetime.now()
        for platform in ["linkedin", "indeed"]:
            platform_dir = os.path.join(self.base_dir, platform)
            for file in os.listdir(platform_dir):
                if not file.endswith(".pdf"):
                    continue
                    
                file_path = os.path.join(platform_dir, file)
                file_age = datetime.fromtimestamp(os.path.getctime(file_path))
                if (now - file_age).days > max_age_days:
                    try:
                        os.remove(file_path)
                        print_lg(f"Removed old resume: {file_path}")
                    except Exception as e:
                        print_lg(f"Failed to remove old resume {file_path}: {e}")