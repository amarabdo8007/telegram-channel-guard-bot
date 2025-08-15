"""
Logger Module
Handles logging for the bot with Arabic language support
"""

import os
import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/bot.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )

class BotLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.actions_log_file = 'logs/actions.jsonl'
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Ensure the actions log file exists"""
        if not os.path.exists(self.actions_log_file):
            # Create empty file
            open(self.actions_log_file, 'w', encoding='utf-8').close()
    
    def log_action(self, action, user_id=None, username=None, chat_id=None, 
                   admin_id=None, admin_username=None, reason=None):
        """Log an action to the actions log file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'username': username,
            'chat_id': chat_id,
            'admin_id': admin_id,
            'admin_username': admin_username,
            'reason': reason
        }
        
        try:
            with open(self.actions_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            self.logger.info(f"Action logged: {action} by user {user_id}")
        
        except Exception as e:
            self.logger.error(f"Error logging action: {e}")
    
    def get_recent_logs(self, limit=50):
        """Get recent log entries"""
        logs = []
        
        try:
            with open(self.actions_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Get the last 'limit' lines
                recent_lines = lines[-limit:] if len(lines) > limit else lines
                
                for line in recent_lines:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        
        except FileNotFoundError:
            self.logger.warning("Actions log file not found")
        except Exception as e:
            self.logger.error(f"Error reading logs: {e}")
        
        return logs
    
    def get_logs_by_action(self, action_type, limit=20):
        """Get logs filtered by action type"""
        all_logs = self.get_recent_logs(limit=1000)
        filtered_logs = [log for log in all_logs if log.get('action') == action_type]
        return filtered_logs[-limit:] if len(filtered_logs) > limit else filtered_logs
    
    def get_admin_actions(self, admin_id, limit=20):
        """Get actions performed by a specific admin"""
        all_logs = self.get_recent_logs(limit=1000)
        admin_logs = [log for log in all_logs if log.get('admin_id') == admin_id]
        return admin_logs[-limit:] if len(admin_logs) > limit else admin_logs
    
    def cleanup_old_logs(self, days_to_keep=30):
        """Clean up log entries older than specified days"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            logs = self.get_recent_logs(limit=10000)  # Get more logs for cleanup
            
            # Filter logs newer than cutoff date
            recent_logs = []
            for log in logs:
                try:
                    log_date = datetime.fromisoformat(log['timestamp'])
                    if log_date > cutoff_date:
                        recent_logs.append(log)
                except:
                    continue
            
            # Rewrite the file with only recent logs
            with open(self.actions_log_file, 'w', encoding='utf-8') as f:
                for log in recent_logs:
                    f.write(json.dumps(log, ensure_ascii=False) + '\n')
            
            self.logger.info(f"Cleaned up old logs, kept {len(recent_logs)} entries")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up logs: {e}")
