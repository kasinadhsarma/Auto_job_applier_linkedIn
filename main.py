#!/usr/bin/env python3
"""
Main entry point for the LinkedIn Auto Job Applier.
"""
import sys
import traceback
from app.core import setup_application
from app.utils.logging import print_lg, error_log

def main():
    """Main application entry point."""
    print_lg("\nStarting LinkedIn Auto Job Applier...")
    
    try:
        # Initialize application
        scheduler = setup_application()
        
        # Run application
        scheduler.run()
        
    except KeyboardInterrupt:
        print_lg("\nApplication terminated by user.")
        sys.exit(0)
        
    except Exception as e:
        error_msg = "An unexpected error occurred:"
        error_log(error_msg, e)
        print_lg(f"{error_msg}\n{str(e)}\n")
        print_lg("Stack trace:")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print_lg("Application shutdown complete.")

if __name__ == "__main__":
    main()
