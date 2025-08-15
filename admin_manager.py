"""
Admin Manager Module
Handles admin-related operations like removing and banning admins
"""

import logging
from telegram.error import TelegramError

class AdminManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def remove_and_ban_admin(self, bot, chat_id, admin_user_id):
        """Remove an admin from the channel and ban them"""
        try:
            # First, try to restrict the admin (remove admin privileges)
            success_restrict = await self.restrict_admin_privileges(bot, chat_id, admin_user_id)
            
            if success_restrict:
                # Then ban the user from the channel
                success_ban = await self.ban_user(bot, chat_id, admin_user_id)
                
                if success_ban:
                    self.logger.info(f"Successfully removed and banned admin {admin_user_id} from chat {chat_id}")
                    return True
                else:
                    self.logger.error(f"Failed to ban admin {admin_user_id} from chat {chat_id}")
            else:
                self.logger.error(f"Failed to restrict admin privileges for {admin_user_id} in chat {chat_id}")
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error removing and banning admin {admin_user_id}: {e}")
            return False
    
    async def restrict_admin_privileges(self, bot, chat_id, admin_user_id):
        """Remove admin privileges from a user"""
        try:
            # Promote user with no privileges (effectively demoting them)
            await bot.promote_chat_member(
                chat_id=chat_id,
                user_id=admin_user_id,
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_post_messages=False,
                can_edit_messages=False
            )
            
            self.logger.info(f"Successfully restricted privileges for admin {admin_user_id} in chat {chat_id}")
            return True
        
        except TelegramError as e:
            self.logger.error(f"Telegram error restricting admin {admin_user_id}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error restricting admin {admin_user_id}: {e}")
            return False
    
    async def ban_user(self, bot, chat_id, user_id):
        """Ban a user from the channel"""
        try:
            await bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id
            )
            
            self.logger.info(f"Successfully banned user {user_id} from chat {chat_id}")
            return True
        
        except TelegramError as e:
            self.logger.error(f"Telegram error banning user {user_id}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error banning user {user_id}: {e}")
            return False
    
    async def add_monitored_admin(self, bot, chat_id, user_id, config):
        """Add an admin to the monitored list"""
        try:
            # Verify the user is actually an admin
            chat_member = await bot.get_chat_member(chat_id, user_id)
            
            if chat_member.status == 'administrator':
                if user_id not in config["channel_settings"]["monitored_admins"]:
                    config["channel_settings"]["monitored_admins"].append(user_id)
                    self.logger.info(f"Added admin {user_id} to monitored list for chat {chat_id}")
                    return True
            else:
                self.logger.warning(f"User {user_id} is not an admin in chat {chat_id}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error adding monitored admin {user_id}: {e}")
            return False
    
    async def get_channel_admins(self, bot, chat_id):
        """Get list of all admins in a channel"""
        try:
            admins = await bot.get_chat_administrators(chat_id)
            admin_list = []
            
            for admin in admins:
                admin_info = {
                    'user_id': admin.user.id,
                    'username': admin.user.username,
                    'first_name': admin.user.first_name,
                    'status': admin.status,
                    'can_restrict_members': getattr(admin, 'can_restrict_members', False)
                }
                admin_list.append(admin_info)
            
            return admin_list
        
        except Exception as e:
            self.logger.error(f"Error getting channel admins for {chat_id}: {e}")
            return []
    
    async def check_bot_permissions(self, bot, chat_id):
        """Check if the bot has necessary permissions"""
        try:
            bot_member = await bot.get_chat_member(chat_id, bot.id)
            
            required_permissions = [
                'can_restrict_members',
                'can_promote_members'
            ]
            
            missing_permissions = []
            
            for perm in required_permissions:
                if not getattr(bot_member, perm, False):
                    missing_permissions.append(perm)
            
            if missing_permissions:
                self.logger.warning(f"Bot missing permissions in chat {chat_id}: {missing_permissions}")
                return False, missing_permissions
            
            return True, []
        
        except Exception as e:
            self.logger.error(f"Error checking bot permissions for chat {chat_id}: {e}")
            return False, ['unknown_error']
