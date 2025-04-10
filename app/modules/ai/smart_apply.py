"""Smart application module for optimizing job applications using AI"""

from typing import Dict, List
import json
from datetime import datetime
from app.config.search import about_company_good_words, about_company_bad_words, bad_words
from app.config.secrets import ai_provider, use_AI

# Import AI providers
from app.modules.ai.openaiConnections import ai_completion as openai_completion
from app.modules.ai.ollamaConnections import (
    ollama_completion,
    ollama_analyze_job,
    ollama_optimize_application,
    ollama_screen_company
)

class SmartApplicationManager:
    def __init__(self, client=None):
        self.openai_client = client  # Only used if ai_provider is "openai"
        self.application_history = {}
        self.ai_provider = ai_provider
        
    def _get_completion(self, messages: List[Dict[str, str]]) -> str:
        """Get completion from configured AI provider"""
        if not use_AI:
            return ""
            
        try:
            if self.ai_provider == "ollama":
                return ollama_completion(messages)
            else:
                return openai_completion(self.openai_client, messages)
        except Exception as e:
            print(f"Error getting AI completion: {e}")
            return ""
            
    def analyze_job_fit(self, job_description: str, company_info: str) -> Dict:
        """Analyze job fit using AI to determine application strategy"""
        if not use_AI:
            return None
            
        try:
            if self.ai_provider == "ollama":
                return ollama_analyze_job(job_description, company_info)
                
            # OpenAI path
            prompt = f"""
            Analyze this job description and company information for application suitability:
            
            JOB DESCRIPTION:
            {job_description}
            
            COMPANY INFO:
            {company_info}
            
            Evaluate and return a JSON with:
            1. Match score (0-100)
            2. Key requirements matched
            3. Missing skills/requirements
            4. Application priority (high/medium/low)
            5. Customization needed (resume/cover letter suggestions)
            """
            
            response = openai_completion(self.openai_client, [{"role": "user", "content": prompt}])
            return json.loads(response)
            
        except Exception as e:
            print(f"Error in job fit analysis: {e}")
            return None
            
    def optimize_application(self, job_details: Dict, user_profile: Dict) -> Dict:
        """Optimize application materials based on job requirements"""
        if not use_AI:
            return None
            
        try:
            # Extract key requirements and tailor application
            skills_needed = self.extract_required_skills(job_details["description"])
            
            if self.ai_provider == "ollama":
                return ollama_optimize_application(job_details, user_profile, skills_needed)
                
            # OpenAI path will continue with existing implementation
            customized_materials = self.customize_materials(
                job_details,
                user_profile,
                skills_needed
            )
            
            return {
                "tailored_resume": customized_materials["resume"],
                "cover_letter": customized_materials["cover_letter"],
                "application_notes": customized_materials["notes"]
            }
            
        except Exception as e:
            print(f"Error optimizing application: {e}")
            return None
    
    def screen_company(self, company_info: str) -> bool:
        """Screen companies based on defined criteria and AI analysis"""
        # Check against bad word lists
        for word in about_company_bad_words:
            if word.lower() in company_info.lower():
                # Check for exceptions
                for good_word in about_company_good_words:
                    if good_word.lower() in company_info.lower():
                        return True
                return False
        
        if not use_AI:
            return True
            
        try:
            if self.ai_provider == "ollama":
                return ollama_screen_company(company_info)
                
            # OpenAI path
            prompt = f"""
            Analyze this company information and determine if it's a legitimate tech employer:
            
            {company_info}
            
            Consider:
            1. Company stability and reputation
            2. Engineering culture
            3. Red flags (staffing agency, fake listings, etc)
            
            Return only 'true' or 'false'.
            """
            
            response = self._get_completion([{"role": "user", "content": prompt}])
            return response.lower().strip() == 'true'
            
        except:
            return True  # Default to accepting if AI fails
            
    def should_apply(self, job_details: Dict, company_info: str) -> bool:
        """Make final decision on whether to apply to a job"""
        # Basic screening
        if not self.screen_company(company_info):
            return False
            
        # Check for bad words in job description
        desc_lower = job_details["description"].lower()
        for word in bad_words:
            if word.lower() in desc_lower:
                return False
                
        if not use_AI:
            return True
                
        # Get AI analysis
        fit_analysis = self.analyze_job_fit(job_details["description"], company_info)
        if fit_analysis and fit_analysis.get("match_score", 0) > 70:
            return True
            
        return False
        
    def extract_required_skills(self, description: str) -> List[str]:
        """Extract required skills from job description"""
        if not use_AI:
            return []
            
        prompt = f"""
        Extract required technical skills from this job description:
        
        {description}
        
        Return the skills as a comma-separated list.
        """
        
        try:
            response = self._get_completion([{"role": "user", "content": prompt}])
            return [skill.strip() for skill in response.split(",")]
        except:
            return []
        
    def track_application(self, job_id: str, company: str, status: str):
        """Track application for optimization"""
        self.application_history[job_id] = {
            "company": company,
            "status": status,
            "date": datetime.now().isoformat()
        }
        
    def get_stats(self) -> Dict:
        """Get application statistics"""
        stats = {
            "total": len(self.application_history),
            "successful": 0,
            "failed": 0,
            "pending": 0
        }
        
        for app in self.application_history.values():
            stats[app["status"]] = stats.get(app["status"], 0) + 1
            
        return stats