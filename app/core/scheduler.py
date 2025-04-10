"""
Scheduler module for managing application runs and timing.
"""
from datetime import datetime
from time import sleep
from typing import Dict, Any, Optional
import pyautogui

from app.core.application import JobApplication
from app.core.browser import BrowserManager
from app.modules.utils.logging import print_lg

class ApplicationScheduler:
    def __init__(self, browser: BrowserManager, config: Dict[str, Any]):
        """Initialize application scheduler."""
        self.browser = browser
        self.config = config
        self.job_application = JobApplication(browser, config)
        self.total_runs = 0
        self.daily_limit_reached = False

    def run(self) -> None:
        """Main run method to handle application scheduling."""
        try:
            self._initialize_browser()
            self._execute_application_cycles()
        except Exception as e:
            print_lg("Error in application scheduler:", e)
        finally:
            self._cleanup()

    def _initialize_browser(self) -> None:
        """Initialize browser and perform login."""
        try:
            self.browser.initialize_browser()
            self.browser.driver.get("https://www.linkedin.com/login")
            
            if not self.browser.is_logged_in_linkedin():
                self.browser.login_linkedin()
        except Exception as e:
            print_lg("Failed to initialize browser:", e)
            raise

    def _execute_application_cycles(self) -> None:
        """Execute application cycles based on configuration."""
        self.total_runs = 1

        while not self.daily_limit_reached:
            print_lg("\n" + "="*100)
            print_lg(f"Date and Time: {datetime.now()}")
            print_lg(f"Cycle number: {self.total_runs}")
            print_lg(f"Currently looking for jobs posted within '{self.config['date_posted']}' "
                    f"and sorting them by '{self.config['sort_by']}'")

            self.job_application.apply_to_jobs(self.config['search_terms'])
            
            if self.daily_limit_reached:
                print_lg("\n### Daily application limit for Easy Apply is reached! ###\n")
                break

            if not self.config.get('run_non_stop', False):
                break

            self._handle_cycle_options()
            
            if not self.daily_limit_reached:
                self._sleep_between_cycles()

            self.total_runs += 1

    def _handle_cycle_options(self) -> None:
        """Handle cycling options for date posted and sort by."""
        if self.config.get('cycle_date_posted', False):
            self._cycle_date_posted()
            
        if self.config.get('alternate_sortby', False):
            self._alternate_sort_by()

    def _cycle_date_posted(self) -> None:
        """Cycle through date posted options."""
        date_options = ["Any time", "Past month", "Past week", "Past 24 hours"]
        current_index = date_options.index(self.config['date_posted'])
        
        if self.config.get('stop_date_cycle_at_24hr', False):
            next_index = current_index + 1 if current_index + 1 < len(date_options) else -1
        else:
            next_index = 0 if current_index + 1 >= len(date_options) else current_index + 1
            
        self.config['date_posted'] = date_options[next_index]

    def _alternate_sort_by(self) -> None:
        """Alternate between sort by options."""
        self.config['sort_by'] = ("Most recent" if self.config['sort_by'] == "Most relevant" 
                                 else "Most relevant")

    def _sleep_between_cycles(self) -> None:
        """Handle sleep between application cycles."""
        print_lg("Sleeping for 10 min...")
        sleep(300)  # 5 minutes
        print_lg("Few more min... Gonna start within next 5 min...")
        sleep(300)  # 5 more minutes

    def _cleanup(self) -> None:
        """Cleanup and display final statistics."""
        stats = {
            "Total runs": self.total_runs,
            "Jobs Easy Applied": self.job_application.easy_applied_count,
            "External job links collected": self.job_application.external_jobs_count,
            "Total applied or collected": (self.job_application.easy_applied_count + 
                                         self.job_application.external_jobs_count),
            "Failed jobs": self.job_application.failed_count,
            "Irrelevant jobs skipped": self.job_application.skip_count
        }

        self._display_final_stats(stats)
        self._display_closing_message()

    def _display_final_stats(self, stats: Dict[str, int]) -> None:
        """Display final application statistics."""
        print_lg("\nFinal Statistics:")
        print_lg("=" * 50)
        
        for key, value in stats.items():
            if key == "Total applied or collected":
                print_lg("-" * 50)
            print_lg(f"{key + ':':30} {value}")

    def _display_closing_message(self) -> None:
        """Display closing message and quote."""
        quotes = [
            "You're one step closer than before.",
            "All the best with your future interviews.",
            "Keep up with the progress. You got this.",
            "If you're tired, learn to take rest but never give up.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence.",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance.",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt"
        ]
        
        from random import choice
        quote = choice(quotes)
        
        msg = (f"\n{quote}\n\n\nBest regards,\n"
               "LinkedIn Auto Job Applier\n"
               "https://github.com/GodsScion/Auto_job_applier_linkedIn\n")
        
        pyautogui.alert(msg, "Exiting..")
        print_lg(msg)

        if self.browser.tabs_count >= 10:
            tab_warning = ("NOTE: IF YOU HAVE MORE THAN 10 TABS OPENED, "
                         "PLEASE CLOSE OR BOOKMARK THEM!\n\n"
                         "Or it's highly likely that application will just "
                         "open browser and not do anything next time!")
            pyautogui.alert(tab_warning, "Info")
            print_lg("\n" + tab_warning)
