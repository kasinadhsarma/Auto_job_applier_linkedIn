"""Smart application scheduling and rate limiting"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os
from pathlib import Path

class ApplicationScheduler:
    def __init__(self, platform_limits: Dict[str, int] = None):
        self.platform_limits = platform_limits or {
            'linkedin': 150,  # LinkedIn typically allows ~100-150 applications per week
            'indeed': 150,   # Indeed typically allows ~150 applications per day
            'dice': 100,     # Dice typically allows ~100 applications per day
            'glassdoor': 100 # Glassdoor typically allows ~100 applications per day
        }
        self.state_file = Path('config/application_state.json')
        self.state = self._load_state()
        
    def _load_state(self) -> Dict:
        """Load application state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
                
        # Initialize default state
        return {
            platform: {
                'daily_count': 0,
                'weekly_count': 0,
                'last_apply_time': None,
                'last_reset_date': datetime.now().strftime('%Y-%m-%d')
            }
            for platform in self.platform_limits
        }
        
    def _save_state(self) -> None:
        """Save application state to disk"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f)
            
    def _reset_counts_if_needed(self, platform: str) -> None:
        """Reset counters if a new day/week has started"""
        platform_state = self.state[platform]
        last_reset = datetime.strptime(platform_state['last_reset_date'], '%Y-%m-%d')
        now = datetime.now()
        
        # Reset daily counts at midnight
        if now.date() > last_reset.date():
            platform_state['daily_count'] = 0
            platform_state['last_reset_date'] = now.strftime('%Y-%m-%d')
            
        # Reset weekly counts on Monday
        if now.date() > last_reset.date() and now.weekday() == 0:
            platform_state['weekly_count'] = 0
            
        self._save_state()
        
    def can_apply(self, platform: str) -> bool:
        """Check if we can apply to more jobs on this platform"""
        if platform not in self.state:
            return False
            
        self._reset_counts_if_needed(platform)
        platform_state = self.state[platform]
        
        # Check daily limit
        if platform_state['daily_count'] >= self.platform_limits[platform]:
            return False
            
        # Check weekly limit for LinkedIn
        if platform == 'linkedin' and platform_state['weekly_count'] >= 150:
            return False
            
        # Check rate limiting
        last_apply = platform_state['last_apply_time']
        if last_apply:
            last_apply = datetime.strptime(last_apply, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_apply < timedelta(seconds=30):
                return False
                
        return True
        
    def record_application(self, platform: str) -> None:
        """Record a successful application"""
        if platform not in self.state:
            return
            
        platform_state = self.state[platform]
        platform_state['daily_count'] += 1
        platform_state['weekly_count'] += 1
        platform_state['last_apply_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._save_state()
        
    def get_platform_stats(self, platform: str) -> Optional[Dict]:
        """Get application statistics for a platform"""
        if platform not in self.state:
            return None
            
        self._reset_counts_if_needed(platform)
        stats = self.state[platform].copy()
        
        # Add remaining counts
        stats['daily_remaining'] = self.platform_limits[platform] - stats['daily_count']
        if platform == 'linkedin':
            stats['weekly_remaining'] = 150 - stats['weekly_count']
            
        return stats
        
    def wait_time_needed(self, platform: str) -> float:
        """Get seconds to wait before next application if needed"""
        if platform not in self.state:
            return 0
            
        last_apply = self.state[platform]['last_apply_time']
        if not last_apply:
            return 0
            
        last_apply = datetime.strptime(last_apply, '%Y-%m-%d %H:%M:%S')
        time_since_last = datetime.now() - last_apply
        
        if time_since_last < timedelta(seconds=30):
            return 30 - time_since_last.total_seconds()
            
        return 0
