'''
Ollama integration for AI-powered features
'''

import requests
import json
from typing import List, Dict, Optional
from app.config.secrets import ollama_host, ollama_model, ollama_timeout

def ollama_completion(messages: List[Dict[str, str]], 
                     temperature: float = 0.7,
                     max_tokens: int = 1000) -> str:
    """
    Get completions from Ollama API
    """
    try:
        # Convert chat messages to a single prompt
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        # Prepare the request
        url = f"{ollama_host}/api/generate"
        data = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Make the request
        response = requests.post(url, json=data, timeout=ollama_timeout)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        return result.get('response', '')
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {str(e)}")
        return ""
        
def ollama_analyze_job(job_description: str, 
                      company_info: str,
                      skills_required: Optional[List[str]] = None) -> Dict:
    """
    Analyze job fit using Ollama
    """
    prompt = f"""Analyze this job description and company information:

JOB DESCRIPTION:
{job_description}

COMPANY INFO:
{company_info}

{f'REQUIRED SKILLS:\n{", ".join(skills_required)}' if skills_required else ''}

Analyze and return a JSON with:
1. Match score (0-100)
2. Key requirements matched
3. Missing skills/requirements
4. Application priority (high/medium/low)
5. Customization needed (resume/cover letter suggestions)

Format the response as valid JSON only.
"""
    
    try:
        response = ollama_completion([{"role": "user", "content": prompt}])
        return json.loads(response)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error analyzing job with Ollama: {str(e)}")
        return {
            "match_score": 0,
            "requirements_matched": [],
            "missing_skills": [],
            "priority": "low",
            "customization": []
        }
        
def ollama_optimize_application(job_details: Dict,
                              user_profile: Dict,
                              required_skills: List[str]) -> Dict:
    """
    Optimize application materials using Ollama
    """
    prompt = f"""Given this job and candidate information, optimize the application:

JOB DETAILS:
{json.dumps(job_details, indent=2)}

USER PROFILE:
{json.dumps(user_profile, indent=2)}

REQUIRED SKILLS:
{", ".join(required_skills)}

Generate optimized application materials as JSON with:
1. Tailored resume points
2. Cover letter key points
3. Application strategy
4. Skills to emphasize

Format the response as valid JSON only.
"""
    
    try:
        response = ollama_completion([{"role": "user", "content": prompt}])
        return json.loads(response)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error optimizing application with Ollama: {str(e)}")
        return {
            "resume_points": [],
            "cover_letter_points": [],
            "strategy": "standard",
            "emphasized_skills": []
        }
        
def ollama_screen_company(company_info: str) -> bool:
    """
    Screen companies using Ollama
    """
    prompt = f"""Analyze this company information and determine if it's a legitimate tech employer:

{company_info}

Consider:
1. Company stability and reputation
2. Engineering culture
3. Red flags (staffing agency, fake listings, etc)

Return only 'true' or 'false'.
"""
    
    try:
        response = ollama_completion([{"role": "user", "content": prompt}])
        return response.lower().strip() == 'true'
    except Exception as e:
        print(f"Error screening company with Ollama: {str(e)}")
        return True  # Default to accepting if AI fails