"""
Logging utility module for consistent logging throughout the application.
"""
from datetime import datetime
from typing import Any, Optional
import os
import json

class Logger:
    def __init__(self, log_file: str = "application.log", screenshots_dir: str = "screenshots"):
        """Initialize logger with log file and screenshots directory."""
        self.log_file = log_file
        self.screenshots_dir = screenshots_dir
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure log and screenshot directories exist."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)

    def log(self, message: str, level: str = "INFO", pretty: bool = False) -> None:
        """Log a message with timestamp and level."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = self._format_message(message, pretty)
        log_entry = f"[{timestamp}] [{level}] {formatted_message}\n"
        
        # Print to console
        print(log_entry.strip())
        
        # Write to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to write to log file: {e}")

    def _format_message(self, message: Any, pretty: bool = False) -> str:
        """Format message for logging."""
        if isinstance(message, (dict, list)):
            try:
                return json.dumps(message, indent=2 if pretty else None)
            except:
                return str(message)
        return str(message)

    def error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message with optional exception details."""
        error_message = f"{message}"
        if error:
            error_message += f"\nError: {str(error)}"
            if hasattr(error, "__traceback__"):
                import traceback
                error_message += f"\nTraceback:\n{''.join(traceback.format_tb(error.__traceback__))}"
        
        self.log(error_message, "ERROR")

    def critical(self, context: str, error: Exception) -> None:
        """Log a critical error with context."""
        self.error(f"Critical error in {context}", error)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.log(message, "DEBUG")

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.log(message, "WARNING")

# Global logger instance
_logger = Logger()

def print_lg(message: Any, *args, **kwargs) -> None:
    """Global logging function."""
    if args:
        message = f"{message} {' '.join(str(arg) for arg in args)}"
    _logger.log(message, **kwargs)

def error_log(message: str, error: Optional[Exception] = None) -> None:
    """Global error logging function."""
    _logger.error(message, error)

def critical_error_log(context: str, error: Exception) -> None:
    """Global critical error logging function."""
    _logger.critical(context, error)

def debug_log(message: str) -> None:
    """Global debug logging function."""
    _logger.debug(message)

def warning_log(message: str) -> None:
    """Global warning logging function."""
    _logger.warning(message)

def get_screenshot_path(job_id: str, context: str) -> str:
    """Generate a screenshot filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{job_id}_{context}_{timestamp}.png"
    return os.path.join(_logger.screenshots_dir, filename.replace(":", "."))

def format_json_output(data: Any) -> str:
    """Format data as pretty JSON string."""
    try:
        return json.dumps(data, indent=2)
    except:
        return str(data)
