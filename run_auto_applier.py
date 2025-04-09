'''
Auto job application script with multi-platform support and rotation
'''

import pyautogui
from datetime import datetime
from typing import List, Dict
from selenium.webdriver.remote.webdriver import WebDriver
from modules.platforms import DailyLimitError

from config.settings import run_in_background, run_non_stop
from config.search import search_terms, companies
from config.secrets import (
    use_AI, username, password,
    indeed_username, indeed_password,
    glassdoor_username, glassdoor_password,
    dice_username, dice_password,
    openai_api_key
)

from modules.open_chrome import driver, wait, actions
from modules.helpers import print_lg, buffer
from modules.platforms.linkedin import LinkedInPlatform
from modules.platforms.indeed import IndeedPlatform
from modules.platforms.glassdoor import GlassdoorPlatform
from modules.platforms.dice import DicePlatform
from modules.ai.smart_apply import SmartApplicationManager
from openai import OpenAI

# Platform configurations with daily limits
PLATFORMS = {
    "LinkedIn": {
        "class": LinkedInPlatform,
        "credentials": (username, password),
        "daily_limit": 100  # LinkedIn's typical daily limit
    },
    "Indeed": {
        "class": IndeedPlatform,
        "credentials": (indeed_username, indeed_password),
        "daily_limit": 150  # Indeed's typical daily limit
    },
    "Glassdoor": {
        "class": GlassdoorPlatform,
        "credentials": (glassdoor_username, glassdoor_password),
        "daily_limit": 100  # Glassdoor's typical daily limit
    },
    "Dice": {
        "class": DicePlatform,
        "credentials": (dice_username, dice_password),
        "daily_limit": 100  # Dice's typical daily limit
    }
}

def validate_platform_config(platform_name: str, username: str, password: str) -> bool:
    """Validate platform configuration"""
    if not username or not password:
        print_lg(f"Missing {platform_name} credentials in config/secrets.py")
        return False
    return True

def get_next_available_platform(current_platform: str = None) -> str:
    """Get next available platform that hasn't hit daily limit"""
    platform_order = ["LinkedIn", "Indeed", "Glassdoor", "Dice"]
    
    if current_platform:
        # Start from the platform after the current one
        start_idx = platform_order.index(current_platform) + 1
        platform_order = platform_order[start_idx:] + platform_order[:start_idx]
    
    for platform_name in platform_order:
        config = PLATFORMS[platform_name]
        username, password = config["credentials"]
        
        if validate_platform_config(platform_name, username, password):
            try:
                platform = config["class"](driver)
                available, remaining = platform.get_platform_status()
                if available and remaining > 0:
                    print_lg(f"Switching to {platform_name} ({remaining} applications remaining)")
                    return platform_name
            except Exception as e:
                print_lg(f"Error checking {platform_name} availability: {str(e)}")
                continue
    
    return None

def run_platform(
    platform_name: str,
    platform_class: type,
    driver: WebDriver,
    username: str,
    password: str,
    daily_limit: int,
    smart_manager: SmartApplicationManager = None
) -> Dict:
    """Run job applications for a specific platform"""
    print_lg(f"\nStarting {platform_name} job applications...")
    
    # Initialize platform
    platform = platform_class(driver)
    
    # Login
    if not platform.login(username, password):
        print_lg(f"Failed to log in to {platform_name}, skipping...")
        return {
            "applied": 0,
            "failed": 0,
            "skipped": 0
        }

    stats = {
        "applied": 0,
        "failed": 0,
        "skipped": 0
    }
    
    try:
        # Run job search and applications
        for keyword in search_terms:
            platform.search_jobs([keyword], "")
            platform.apply_filters()
            
            while True:
                # Check daily limit before processing page
                platform.check_daily_limit(daily_limit)
                
                jobs = platform.get_job_listings()
                if not jobs:
                    break
                    
                for job in jobs:
                    # Check daily limit before each application
                    platform.check_daily_limit(daily_limit)
                    
                    # Get full job details
                    job_details = platform.get_job_details(job)
                    if not job_details:
                        continue

                    # Smart filtering with AI if enabled
                    if smart_manager and use_AI:
                        if not smart_manager.should_apply(job_details, job_details.get("company_info", "")):
                            stats["skipped"] += 1
                            print_lg(f"Skipping {job['title']} at {job['company']} (AI recommendation)")
                            continue
                            
                        # Get optimized application materials
                        materials = smart_manager.optimize_application(
                            job_details, 
                            {"profile": "user profile"}  # Add user profile details
                        )
                        
                    result = platform.apply_to_job(job_details)
                    if result == "success":
                        stats["applied"] += 1
                        platform.jobs_applied += 1
                        if smart_manager:
                            smart_manager.track_application(
                                job["id"], 
                                job["company"], 
                                "successful"
                            )
                    elif result == "failed":
                        stats["failed"] += 1
                        if smart_manager:
                            smart_manager.track_application(
                                job["id"],
                                job["company"],
                                "failed"
                            )
                    else:
                        stats["skipped"] += 1
                        
                if not platform.get_next_page():
                    break
                    
    except DailyLimitError as e:
        print_lg(str(e))
        # Platform rotation will be handled by main loop
        
    except Exception as e:
        print_lg(f"Error in platform {platform_name}: {str(e)}")
        
    finally:
        platform._save_platform_state()
        
    return stats

def main() -> None:
    """Main entry point for multi-platform job application bot"""
    try:
        # Initialize AI manager if enabled
        smart_manager = None
        if use_AI:
            print_lg("Initializing AI-powered application manager...")
            openai_client = OpenAI(api_key=openai_api_key)
            smart_manager = SmartApplicationManager(openai_client)
        
        total_stats = {}
        cycle = 1
        current_platform = None
        
        while True:
            print_lg(f"\n=== Starting application cycle {cycle} ===")
            cycle_stats = {}
            
            # Get next available platform
            current_platform = get_next_available_platform(current_platform)
            if not current_platform:
                print_lg("All platforms have reached their daily limits")
                if not run_non_stop:
                    break
                print_lg("Waiting 1 hour before retrying...")
                buffer(3600)  # Wait 1 hour
                continue
            
            # Run selected platform
            config = PLATFORMS[current_platform]
            username, password = config["credentials"]
            stats = run_platform(
                current_platform,
                config["class"],
                driver,
                username,
                password,
                config["daily_limit"],
                smart_manager
            )
            
            cycle_stats[current_platform] = stats
            
            # Update total stats
            if current_platform not in total_stats:
                total_stats[current_platform] = {
                    "applied": 0,
                    "failed": 0,
                    "skipped": 0
                }
            for key in stats:
                total_stats[current_platform][key] += stats[key]
            
            print_lg("\n=== Cycle Statistics ===")
            for platform, stats in cycle_stats.items():
                print_lg(f"\n{platform}:")
                print_lg(f"  Applied: {stats['applied']}")
                print_lg(f"  Failed: {stats['failed']}")
                print_lg(f"  Skipped: {stats['skipped']}")
            
            if smart_manager:
                ai_stats = smart_manager.get_stats()
                print_lg("\nAI-Powered Application Stats:")
                print_lg(f"  Total Applications: {ai_stats['total']}")
                print_lg(f"  Success Rate: {(ai_stats['successful'] / ai_stats['total'] * 100):.1f}%")
            
            if not run_non_stop:
                break
                
            print_lg("\nWaiting 10 minutes before next cycle...")
            buffer(600)  # 10 minutes
            cycle += 1
            
    except Exception as e:
        print_lg(f"Error in main: {e}")
        if not run_in_background:
            pyautogui.alert("An error occurred. Check the logs for details.", "Error")
    finally:
        print_lg("\n=== Total Statistics ===")
        for platform, stats in total_stats.items():
            print_lg(f"\n{platform} Total:")
            print_lg(f"  Total Applied: {stats['applied']}")
            print_lg(f"  Total Failed: {stats['failed']}")
            print_lg(f"  Total Skipped: {stats['skipped']}")
        
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()