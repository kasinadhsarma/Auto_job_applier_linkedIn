"""Smart application module for optimizing job applications using AI"""

from typing import Dict, List
import json
from datetime import datetime
from modules.ai.openaiConnections import ai_completion
from config.search import about_company_good_words, about_company_bad_words, bad_words

class SmartApplicationManager:
    def __init__(self, client):
        self.openai_client = client
        self.application_history = {}
        
    def analyze_job_fit(self, job_description: str, company_info: str) -> Dict:
        """Analyze job fit using AI to determine application strategy"""
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
        
        try:
            response = ai_completion(self.openai_client, [{"role": "user", "content": prompt}])
            return json.loads(response)
        except Exception as e:
            print(f"Error in job fit analysis: {e}")
            return None
            
    def optimize_application(self, job_details: Dict, user_profile: Dict) -> Dict:
        """Optimize application materials based on job requirements"""
        # Extract key requirements and tailor application
        skills_needed = self.extract_required_skills(job_details["description"])
        
        # Customize resume and cover letter
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
        
        # Use AI to analyze company culture and stability
        prompt = f"""
        Analyze this company information and determine if it's a legitimate tech employer:
        
        {company_info}
        
        Consider:
        1. Company stability and reputation
        2. Engineering culture
        3. Red flags (staffing agency, fake listings, etc)
        
        Return only 'true' or 'false'.
        """
        
        try:
            response = ai_completion(self.openai_client, [{"role": "user", "content": prompt}])
            return response.lower().strip() == 'true'
        except:
            # Default to accepting if AI fails
            return True
            
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
                
        # Get AI analysis
        fit_analysis = self.analyze_job_fit(job_details["description"], company_info)
        if fit_analysis and fit_analysis.get("match_score", 0) > 70:
            return True
            
        return False
        
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