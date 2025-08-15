"""
Bot Handler Module
Handles all bot commands and chat member updates
"""

import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from channel_monitor import ChannelMonitor
from admin_manager import AdminManager
from messages import Messages
from logger import BotLogger

class BotHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bot_logger = BotLogger()
        self.channel_monitor = ChannelMonitor()
        self.admin_manager = AdminManager()
        self.messages = Messages()
        self.load_config()
    
    def load_config(self):
        """Load bot configuration from JSON file"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.logger.error("Config file not found, using defaults")
            self.config = {
                "bot_settings": {"language": "ar"},
                "channel_settings": {"auto_ban_enabled": True}
            }
    
    def save_config(self):
        """Save current configuration to JSON file"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        self.bot_logger.log_action(
            action="start_command",
            user_id=user.id,
            username=user.username,
            chat_id=chat.id
        )
        
        welcome_message = self.messages.get_message("welcome")
        
        # Create inline keyboard with buttons
        keyboard = [
            [
                InlineKeyboardButton("🛡️ إضافة قناة للحماية", callback_data="add_channel")
            ],
            [
                InlineKeyboardButton("👤 إضافة مشرف للمراقبة", callback_data="add_admin"),
                InlineKeyboardButton("📝 عرض المشرفين", callback_data="list_admins")
            ],
            [
                InlineKeyboardButton("📊 حالة البوت", callback_data="status"),
                InlineKeyboardButton("📋 المساعدة", callback_data="help")
            ],
            [
                InlineKeyboardButton("📋 السجلات", callback_data="logs"),
                InlineKeyboardButton("⚙️ الإعدادات", callback_data="config")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not update.message:
            return
            
        help_message = self.messages.get_message("help")
        await update.message.reply_text(help_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if user is authorized
        if not await self.is_authorized_user(user.id, chat.id, context):
            await update.message.reply_text(self.messages.get_message("unauthorized"))
            return
        
        status_info = {
            "protected_channels": len(self.config["channel_settings"]["protected_channels"]),
            "monitored_admins": len(self.config["channel_settings"]["monitored_admins"]),
            "auto_ban_enabled": self.config["channel_settings"]["auto_ban_enabled"],
            "bot_active": True
        }
        
        status_message = self.messages.get_status_message(status_info)
        await update.message.reply_text(status_message)
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if user is authorized
        if not await self.is_authorized_user(user.id, chat.id, context):
            await update.message.reply_text(self.messages.get_message("unauthorized"))
            return
        
        recent_logs = self.bot_logger.get_recent_logs(limit=10)
        logs_message = self.messages.get_logs_message(recent_logs)
        await update.message.reply_text(logs_message)
    
    async def config_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /config command"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if user is authorized
        if not await self.is_authorized_user(user.id, chat.id, context):
            await update.message.reply_text(self.messages.get_message("unauthorized"))
            return
        
        config_message = self.messages.get_config_message(self.config)
        await update.message.reply_text(config_message)
    
    async def add_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add an admin to the monitored list"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if user is authorized (must be channel owner/creator)
        if not await self.is_channel_creator(user.id, chat.id, context):
            await update.message.reply_text(self.messages.get_message("only_creator_allowed"))
            return
        
        # Get admin user ID from command arguments
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(self.messages.get_message("add_admin_usage"))
            return
        
        try:
            admin_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text(self.messages.get_message("invalid_user_id"))
            return
        
        # Add channel to protected list if not already there
        if chat.id not in self.config["channel_settings"]["protected_channels"]:
            self.config["channel_settings"]["protected_channels"].append(chat.id)
        
        # Add admin to monitored list
        success = await self.admin_manager.add_monitored_admin(context.bot, chat.id, admin_id, self.config)
        
        if success:
            self.save_config()
            self.bot_logger.log_action(
                action="admin_added_to_monitor",
                user_id=admin_id,
                chat_id=chat.id,
                admin_id=user.id,
                admin_username=user.username
            )
            await update.message.reply_text(self.messages.get_message("admin_added_success", admin_id=admin_id))
        else:
            await update.message.reply_text(self.messages.get_message("admin_add_failed"))
    
    async def remove_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove an admin from the monitored list"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if user is authorized (must be channel owner/creator)
        if not await self.is_channel_creator(user.id, chat.id, context):
            await update.message.reply_text(self.messages.get_message("only_creator_allowed"))
            return
        
        # Get admin user ID from command arguments
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(self.messages.get_message("remove_admin_usage"))
            return
        
        try:
            admin_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text(self.messages.get_message("invalid_user_id"))
            return
        
        # Remove admin from monitored list
        if admin_id in self.config["channel_settings"]["monitored_admins"]:
            self.config["channel_settings"]["monitored_admins"].remove(admin_id)
            self.save_config()
            
            self.bot_logger.log_action(
                action="admin_removed_from_monitor",
                user_id=admin_id,
                chat_id=chat.id,
                admin_id=user.id,
                admin_username=user.username
            )
            
            await update.message.reply_text(self.messages.get_message("admin_removed_success", admin_id=admin_id))
        else:
            await update.message.reply_text(self.messages.get_message("admin_not_monitored"))
    
    async def list_admins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all monitored admins in the channel"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if user is authorized
        if not await self.is_authorized_user(user.id, chat.id, context):
            await update.message.reply_text(self.messages.get_message("unauthorized"))
            return
        
        monitored_admins = self.config["channel_settings"]["monitored_admins"]
        
        if not monitored_admins:
            await update.message.reply_text(self.messages.get_message("no_monitored_admins"))
            return
        
        # Get detailed info about monitored admins
        admin_details = []
        for admin_id in monitored_admins:
            try:
                member = await context.bot.get_chat_member(chat.id, admin_id)
                admin_info = {
                    'id': admin_id,
                    'username': member.user.username,
                    'first_name': member.user.first_name,
                    'status': member.status
                }
                admin_details.append(admin_info)
            except:
                admin_details.append({'id': admin_id, 'username': None, 'first_name': 'Unknown', 'status': 'unknown'})
        
        message = self.messages.get_monitored_admins_message(admin_details)
        await update.message.reply_text(message)
    
    async def add_channel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add current channel to protected channels list"""
        if not update.effective_user or not update.effective_chat or not update.message:
            return
            
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if user is channel creator
        if not await self.is_channel_creator(user.id, chat.id, context):
            await update.message.reply_text(self.messages.get_message("only_creator_allowed"))
            return
        
        # Add channel to protected list if not already there
        if chat.id not in self.config["channel_settings"]["protected_channels"]:
            self.config["channel_settings"]["protected_channels"].append(chat.id)
            self.save_config()
            
            self.bot_logger.log_action(
                action="channel_added_to_protection",
                chat_id=chat.id,
                admin_id=user.id,
                admin_username=user.username
            )
            
            await update.message.reply_text(self.messages.get_message("channel_added_success"))
        else:
            await update.message.reply_text(self.messages.get_message("channel_already_protected"))
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        query = update.callback_query
        if not query:
            return
            
        await query.answer()
        
        if query.data == "add_channel":
            # Show instructions for adding channel
            keyboard = [[InlineKeyboardButton("✅ إضافة هذه القناة", callback_data="confirm_add_channel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = self.messages.get_message("add_channel_instructions")
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        elif query.data == "confirm_add_channel":
            # Add current channel to protection
            if not query.from_user or not query.message or not query.message.chat:
                return
                
            user = query.from_user
            chat = query.message.chat
            
            # Check if user is channel creator
            if not await self.is_channel_creator(user.id, chat.id, context):
                await query.edit_message_text(self.messages.get_message("only_creator_allowed"))
                return
            
            # Add channel to protected list
            if chat.id not in self.config["channel_settings"]["protected_channels"]:
                self.config["channel_settings"]["protected_channels"].append(chat.id)
                self.save_config()
                
                self.bot_logger.log_action(
                    action="channel_added_to_protection",
                    chat_id=chat.id,
                    admin_id=user.id,
                    admin_username=user.username
                )
                
                await query.edit_message_text(self.messages.get_message("channel_added_success"))
            else:
                await query.edit_message_text(self.messages.get_message("channel_already_protected"))
                
        elif query.data == "add_admin":
            # Show instructions for adding admin
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = self.messages.get_message("add_admin_instructions")
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        elif query.data == "status":
            # Show bot status
            if not query.from_user or not query.message or not query.message.chat:
                return
                
            user = query.from_user
            chat = query.message.chat
            
            if not await self.is_authorized_user(user.id, chat.id, context):
                await query.edit_message_text(self.messages.get_message("unauthorized"))
                return
            
            status_info = {
                "protected_channels": len(self.config["channel_settings"]["protected_channels"]),
                "monitored_admins": len(self.config["channel_settings"]["monitored_admins"]),
                "auto_ban_enabled": self.config["channel_settings"]["auto_ban_enabled"],
                "bot_active": True
            }
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            status_message = self.messages.get_status_message(status_info)
            await query.edit_message_text(status_message, reply_markup=reply_markup)
            
        elif query.data == "help":
            # Show help message
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            help_message = self.messages.get_message("help")
            await query.edit_message_text(help_message, reply_markup=reply_markup)
            
        elif query.data == "list_admins":
            # Show list of monitored admins
            if not query.from_user or not query.message or not query.message.chat:
                return
                
            user = query.from_user
            chat = query.message.chat
            
            if not await self.is_authorized_user(user.id, chat.id, context):
                await query.edit_message_text(self.messages.get_message("unauthorized"))
                return
            
            monitored_admins = self.config["channel_settings"]["monitored_admins"]
            
            if not monitored_admins:
                await query.edit_message_text(self.messages.get_message("no_monitored_admins"))
                return
            
            # Get detailed info about monitored admins
            admin_details = []
            for admin_id in monitored_admins:
                try:
                    member = await context.bot.get_chat_member(chat.id, admin_id)
                    admin_info = {
                        'id': admin_id,
                        'username': member.user.username,
                        'first_name': member.user.first_name,
                        'status': member.status
                    }
                    admin_details.append(admin_info)
                except:
                    admin_details.append({'id': admin_id, 'username': None, 'first_name': 'Unknown', 'status': 'unknown'})
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = self.messages.get_monitored_admins_message(admin_details)
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        elif query.data == "logs":
            # Show recent logs
            if not query.from_user or not query.message or not query.message.chat:
                return
                
            user = query.from_user
            chat = query.message.chat
            
            if not await self.is_authorized_user(user.id, chat.id, context):
                await query.edit_message_text(self.messages.get_message("unauthorized"))
                return
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            recent_logs = self.bot_logger.get_recent_logs(limit=10)
            logs_message = self.messages.get_logs_message(recent_logs)
            await query.edit_message_text(logs_message, reply_markup=reply_markup)
            
        elif query.data == "config":
            # Show configuration
            if not query.from_user or not query.message or not query.message.chat:
                return
                
            user = query.from_user
            chat = query.message.chat
            
            if not await self.is_authorized_user(user.id, chat.id, context):
                await query.edit_message_text(self.messages.get_message("unauthorized"))
                return
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            config_message = self.messages.get_config_message(self.config)
            await query.edit_message_text(config_message, reply_markup=reply_markup)
            
        elif query.data == "main_menu":
            # Show main menu
            keyboard = [
                [
                    InlineKeyboardButton("🛡️ إضافة قناة للحماية", callback_data="add_channel")
                ],
                [
                    InlineKeyboardButton("👤 إضافة مشرف للمراقبة", callback_data="add_admin"),
                    InlineKeyboardButton("📝 عرض المشرفين", callback_data="list_admins")
                ],
                [
                    InlineKeyboardButton("📊 حالة البوت", callback_data="status"),
                    InlineKeyboardButton("📋 المساعدة", callback_data="help")
                ],
                [
                    InlineKeyboardButton("📋 السجلات", callback_data="logs"),
                    InlineKeyboardButton("⚙️ الإعدادات", callback_data="config")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_message = self.messages.get_message("welcome")
            await query.edit_message_text(welcome_message, reply_markup=reply_markup)
    
    async def chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle chat member updates"""
        try:
            if not update.effective_chat:
                return
                
            chat = update.effective_chat
            
            # Only monitor channels and supergroups
            if chat.type not in ['channel', 'supergroup']:
                return
            
            # Check if this channel is being monitored
            if chat.id not in self.config["channel_settings"]["protected_channels"]:
                return
            
            # Get the chat member update
            chat_member_update = update.chat_member
            if not chat_member_update:
                return
            
            old_member = chat_member_update.old_chat_member
            new_member = chat_member_update.new_chat_member
            updated_by = chat_member_update.from_user
            
            # Check if someone was banned
            if (old_member and new_member and 
                old_member.status in ['member', 'restricted'] and 
                new_member.status == 'kicked'):
                
                # Log the ban action
                self.bot_logger.log_action(
                    action="member_banned",
                    user_id=new_member.user.id if new_member and new_member.user else None,
                    username=new_member.user.username if new_member and new_member.user else None,
                    chat_id=chat.id,
                    admin_id=updated_by.id if updated_by else None,
                    admin_username=updated_by.username if updated_by else None
                )
                
                # Check if the admin who banned the user should be punished
                if updated_by and new_member and new_member.user:
                    await self.handle_admin_ban_action(
                        context, chat.id, updated_by, new_member.user
                    )
        
        except Exception as e:
            self.logger.error(f"Error handling chat member update: {e}")
    
    async def handle_admin_ban_action(self, context, chat_id, admin_user, banned_user):
        """Handle when an admin bans a regular member"""
        try:
            # Check if auto-ban is enabled
            if not self.config["channel_settings"]["auto_ban_enabled"]:
                return
            
            # Check if the admin is in our monitored list (admins added by bot)
            if admin_user.id not in self.config["channel_settings"]["monitored_admins"]:
                return
            
            # Don't ban if the banned user was also an admin
            try:
                banned_member = await context.bot.get_chat_member(chat_id, banned_user.id)
                if banned_member.status in ['administrator', 'creator']:
                    return
            except:
                pass  # Continue with the ban if we can't check status
            
            # Remove the admin from the channel
            success = await self.admin_manager.remove_and_ban_admin(
                context.bot, chat_id, admin_user.id
            )
            
            if success:
                # Remove from monitored admins list
                if admin_user.id in self.config["channel_settings"]["monitored_admins"]:
                    self.config["channel_settings"]["monitored_admins"].remove(admin_user.id)
                    self.save_config()
                
                # Log the action
                self.bot_logger.log_action(
                    action="admin_banned_for_abuse",
                    user_id=admin_user.id,
                    username=admin_user.username,
                    chat_id=chat_id,
                    reason=f"Banned regular member {banned_user.id}"
                )
                
                # Send notification if enabled
                if self.config["channel_settings"]["notification_enabled"]:
                    notification_message = self.messages.get_admin_banned_message(
                        admin_user.username or str(admin_user.id),
                        banned_user.username or str(banned_user.id)
                    )
                    
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=notification_message
                        )
                    except Exception as e:
                        self.logger.error(f"Error sending notification: {e}")
        
        except Exception as e:
            self.logger.error(f"Error handling admin ban action: {e}")
    
    async def is_authorized_user(self, user_id, chat_id, context):
        """Check if user is authorized to use admin commands"""
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            return chat_member.status in ['creator', 'administrator']
        except:
            return False
    
    async def is_channel_creator(self, user_id, chat_id, context):
        """Check if user is the channel creator/owner"""
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            return chat_member.status == 'creator'
        except:
            return False
