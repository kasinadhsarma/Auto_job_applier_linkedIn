"""
Configuration management module.
"""
import os
import importlib.util
from typing import Dict, Any, Optional

def load_module(module_path: str) -> Optional[Dict[str, Any]]:
    """Load a Python module and return its attributes as a dictionary."""
    try:
        spec = importlib.util.spec_from_file_location(
            os.path.basename(module_path),
            module_path
        )
        if not spec or not spec.loader:
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return {
            key: value for key, value in module.__dict__.items()
            if not key.startswith('_')  # Exclude private attributes
        }
    except Exception:
        return None

def load_config() -> Dict[str, Any]:
    """Load application configuration from all sources."""
    # Base configuration
    config = {
        # File paths and directories
        'base_dir': os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'data_dir': 'data',
        'logs_dir': os.path.join('data', 'logs'),
        'screenshots_dir': os.path.join('data', 'logs', 'screenshots'),
        'resume_dir': os.path.join('data', 'resumes'),
        
        # Browser settings
        'run_in_background': False,
        'keep_screen_awake': True,
        'close_tabs': True,
        
        # Application behavior
        'run_non_stop': False,
        'cycle_date_posted': False,
        'stop_date_cycle_at_24hr': True,
        'alternate_sortby': False,
        'pause_after_filters': True,
        'pause_at_failed_question': True,
        'pause_before_submit': True,
        'overwrite_previous_answers': False,
        
        # Job search settings
        'easy_apply_only': True,
        'randomize_search_order': False,
        'switch_number': 25,
        'click_gap': 2,
        
        # Search filters
        'date_posted': "Past 24 hours",
        'sort_by': "Most recent",
        'experience_level': [],
        'job_type': [],
        'on_site': [],
        'salary': "",
        'under_10_applicants': False,
        'in_your_network': False,
        'fair_chance_employer': False,
        
        # Job parameters
        'search_location': "",
        'search_terms': [],
        'current_experience': -1,
        'did_masters': False
    }

    # Configuration file paths
    config_files = {
        'settings': os.path.join(config['base_dir'], 'config', 'settings.py'),
        'search': os.path.join(config['base_dir'], 'config', 'search.py'),
        'personals': os.path.join(config['base_dir'], 'config', 'personals.py'),
        'secrets': os.path.join(config['base_dir'], 'config', 'secrets.py')
    }

    # Load and merge configurations
    for module_name, file_path in config_files.items():
        if module_config := load_module(file_path):
            config.update(module_config)

    # Ensure required directories exist
    _ensure_directories(config)

    return config

def _ensure_directories(config: Dict[str, Any]) -> None:
    """Ensure all required directories exist."""
    for dir_path in [
        config['data_dir'],
        config['logs_dir'],
        config['screenshots_dir'],
        config['resume_dir']
    ]:
        os.makedirs(dir_path, exist_ok=True)

def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration settings."""
    required_fields = [
        'search_terms',
        'search_location',
        'default_resume_path'
    ]
    
    missing_fields = [
        field for field in required_fields 
        if not config.get(field)
    ]
    
    if missing_fields:
        raise ValueError(
            f"Missing required configuration fields: {', '.join(missing_fields)}"
        )
    
    if not os.path.exists(config['default_resume_path']):
        raise FileNotFoundError(
            f"Resume file not found at {config['default_resume_path']}"
        )

    # Validate credentials
    if not all(key in config for key in ['username', 'password']):
        raise ValueError(
            "LinkedIn credentials not found. Please ensure username and password "
            "are defined in config/secrets.py"
        )
