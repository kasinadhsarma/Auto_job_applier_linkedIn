"""
Core module initialization and application setup.
"""
from .config import load_config, validate_config
from .browser import BrowserManager
from .application import JobApplication
from .scheduler import ApplicationScheduler

def setup_application():
    """
    Initialize and configure the application.
    Returns: Configured ApplicationScheduler instance
    """
    # Load and validate configuration
    config = load_config()
    validate_config(config)
    
    # Initialize components
    browser = BrowserManager(
        username=config['username'],
        password=config['password']
    )
    
    app = JobApplication(browser, config)
    scheduler = ApplicationScheduler(browser, config)
    
    return scheduler

__all__ = ['setup_application', 'load_config', 'validate_config']
