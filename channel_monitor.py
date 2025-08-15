"""
Channel Monitor Module
Monitors channel activities and member changes
"""

import logging
from datetime import datetime
from telegram import ChatMember

class ChannelMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitored_events = []
    
    def is_member_ban(self, old_status, new_status):
        """Check if a member status change represents a ban"""
        ban_transitions = [
            ('member', 'kicked'),
            ('restricted', 'kicked'),
            ('left', 'kicked')
        ]
        return (old_status, new_status) in ban_transitions
    
    def is_admin_action(self, chat_member_update):
        """Check if the update was performed by an admin"""
        return chat_member_update.from_user is not None
    
    def log_member_change(self, chat_id, user_id, old_status, new_status, admin_id=None):
        """Log member status changes"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'chat_id': chat_id,
            'user_id': user_id,
            'old_status': old_status,
            'new_status': new_status,
            'admin_id': admin_id,
            'event_type': 'member_change'
        }
        
        self.monitored_events.append(event)
        self.logger.info(f"Member status change logged: {event}")
        
        # Keep only recent events (last 1000)
        if len(self.monitored_events) > 1000:
            self.monitored_events = self.monitored_events[-1000:]
    
    def get_recent_bans(self, chat_id, limit=10):
        """Get recent ban events for a specific chat"""
        ban_events = [
            event for event in self.monitored_events
            if (event['chat_id'] == chat_id and 
                event['new_status'] == 'kicked' and
                event['old_status'] in ['member', 'restricted'])
        ]
        
        # Sort by timestamp (most recent first)
        ban_events.sort(key=lambda x: x['timestamp'], reverse=True)
        return ban_events[:limit]
    
    def get_admin_ban_count(self, admin_id, chat_id, hours=24):
        """Get the number of bans performed by an admin in the last X hours"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        ban_count = 0
        for event in self.monitored_events:
            event_time = datetime.fromisoformat(event['timestamp'])
            if (event['admin_id'] == admin_id and 
                event['chat_id'] == chat_id and
                event['new_status'] == 'kicked' and
                event_time > cutoff_time):
                ban_count += 1
        
        return ban_count
    
    def is_suspicious_activity(self, admin_id, chat_id):
        """Check if an admin is showing suspicious banning behavior"""
        recent_bans = self.get_admin_ban_count(admin_id, chat_id, hours=1)
        
        # Consider it suspicious if more than 5 bans in 1 hour
        return recent_bans > 5
