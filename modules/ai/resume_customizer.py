"""Resume customization module using AI"""

from typing import Dict, Optional
from modules.ai.smart_apply import SmartApplicationManager
from modules.resumes.manager import ResumeManager
from config.secrets import use_AI, ai_provider

def customize_resume_for_job(
    resume_manager: ResumeManager,
    smart_manager: SmartApplicationManager,
    job_details: Dict,
    platform: str
) -> Optional[str]:
    """Customize resume for a specific job using AI"""
    if not use_AI:
        return None
        
    try:
        # Get job-specific details
        job_id = job_details["id"]
        description = job_details.get("description", "")
        company_info = job_details.get("company_info", "")
        
        # Get resume tailored to job requirements
        resume = resume_manager.get_resume_for_job(
            platform=platform,
            job_id=job_id,
            job_description=description,
            customize=True
        )
        
        if resume and resume.customized:
            return resume.path
            
        return None
        
    except Exception as e:
        print(f"Error customizing resume: {e}")
        return None
