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
        
        await self.show_main_menu(update, context)
    
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
        self.bot_logger.log_action(
            action="add_admin_command_called",
            user_id=update.effective_user.id if update.effective_user else None,
            admin_id=update.effective_user.id if update.effective_user else None
        )
        
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
        if admin_id not in self.config["channel_settings"]["monitored_admins"]:
            self.config["channel_settings"]["monitored_admins"].append(admin_id)
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
            await update.message.reply_text(f"⚠️ المشرف {admin_id} موجود بالفعل في قائمة المراقبة!")
    
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
        """Add specified channel to protected channels list"""
        self.bot_logger.log_action(
            action="add_channel_command_called",
            user_id=update.effective_user.id if update.effective_user else None,
            admin_id=update.effective_user.id if update.effective_user else None
        )
        
        if not update.effective_user or not update.message:
            return
            
        if not context.args:
            await update.message.reply_text(
                "📝 الاستخدام: /add_channel [ID_القناة]\n\n"
                "مثال:\n/add_channel -1001234567890\n\n"
                "📋 طريقة الحصول على ID القناة:\n"
                "• استخدم @userinfobot في القناة\n"
                "• أو استخدم @getidsbot مع اسم المستخدم\n"
                "• أو انسخ رابط القناة واستخرج الID منه"
            )
            return
            
        user = update.effective_user
        
        try:
            channel_id = int(context.args[0])
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ معرف القناة غير صحيح\n📝 الاستخدام: /add_channel [ID_القناة]\nمثال: /add_channel -1001234567890"
            )
            return
        
        try:
            # Check if user is member of the channel and get their status
            member = await context.bot.get_chat_member(channel_id, user.id)
            if member.status not in ['creator', 'administrator']:
                await update.message.reply_text(
                    "❌ يجب أن تكون مالك القناة أو مشرف لإضافتها للحماية"
                )
                return
                
            # Get channel info
            channel_info = await context.bot.get_chat(channel_id)
            channel_title = channel_info.title or f"Channel {channel_id}"
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ فشل في الوصول للقناة {channel_id}\n"
                "تأكد من:\n"
                "• صحة معرف القناة\n"
                "• إضافة البوت كمشرف في القناة\n"
                "• منح البوت الصلاحيات المطلوبة"
            )
            return
        
        # Add channel to protected list if not already there
        if channel_id not in self.config["channel_settings"]["protected_channels"]:
            self.config["channel_settings"]["protected_channels"].append(channel_id)
            self.save_config()
            
            self.bot_logger.log_action(
                action="channel_added_to_protection",
                chat_id=channel_id,
                admin_id=user.id,
                admin_username=user.username
            )
            
            # Show success message with button to return to main menu
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ تم إضافة القناة {channel_title} إلى قائمة الحماية بنجاح!\n"
                f"🆔 معرف القناة: {channel_id}\n\n"
                "البوت الآن سيراقب أنشطة المشرفين المحددين في هذه القناة.\n\n"
                "💡 اضغط العودة للقائمة الرئيسية لإضافة مشرفين للمراقبة.",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(f"⚠️ القناة {channel_title} محمية بالفعل!")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        query = update.callback_query
        if not query:
            return
            
        await query.answer()
        
        if query.data == "add_channel":
            # Show instructions and wait for channel ID input
            keyboard = [
                [InlineKeyboardButton("📝 إدخال ID القناة", callback_data="input_channel_id")],
                [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = self.messages.get_message("add_channel_instructions")
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        elif query.data == "input_channel_id":
            # Ask user to send channel ID
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🆔 أرسل ID القناة الآن:\n\n"
                "مثال: -1001234567890\n\n"
                "ملاحظة: أرسل ID القناة كرسالة منفصلة (ليس كرد على هذه الرسالة)",
                reply_markup=reply_markup
            )
            
            # Store that we're waiting for channel ID from this user
            context.user_data['waiting_for'] = 'channel_id'
                
        elif query.data == "add_admin":
            # Show instructions and wait for admin ID input
            keyboard = [
                [InlineKeyboardButton("📝 إدخال ID المشرف", callback_data="input_admin_id")],
                [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = self.messages.get_message("add_admin_instructions")
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        elif query.data == "input_admin_id":
            # Ask user to send admin ID
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🆔 أرسل ID المشرف الآن:\n\n"
                "مثال: 123456789\n\n"
                "ملاحظة: أرسل ID المشرف كرسالة منفصلة (ليس كرد على هذه الرسالة)",
                reply_markup=reply_markup
            )
            
            # Store that we're waiting for admin ID from this user
            context.user_data['waiting_for'] = 'admin_id'
            
        elif query.data.startswith("add_admin_to_channel_"):
            # Extract channel ID from callback data
            channel_id = int(query.data.replace("add_admin_to_channel_", ""))
            
            # Store the channel ID for later use
            context.user_data['target_channel_id'] = channel_id
            
            # Get channel name for display
            try:
                channel_info = await context.bot.get_chat(channel_id)
                channel_name = channel_info.title or f"Channel {channel_id}"
            except:
                channel_name = f"Channel {channel_id}"
            
            # Show instructions for adding admin to specific channel
            keyboard = [
                [InlineKeyboardButton("📝 إدخال ID المشرف", callback_data="input_admin_id")],
                [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"👤 إضافة مشرف للمراقبة في القناة {channel_name}\n\n"
                "📋 لإضافة مشرف للمراقبة:\n"
                "• احصل على معرف المشرف (User ID)\n"
                "• تأكد من أن المشرف موجود في هذه القناة\n"
                "• اضغط على 'إدخال ID المشرف' وأرسل المعرف\n\n"
                "💡 طرق الحصول على معرف المشرف:\n"
                "• استخدم @userinfobot\n"
                "• أو استخدم @getidsbot\n"
                "• أو ابحث في إعدادات التيليجرام",
                reply_markup=reply_markup
            )

        elif query.data.startswith("remove_channel_"):
            # Handle channel removal
            channel_id = int(query.data.replace("remove_channel_", ""))
            
            if channel_id in self.config["channel_settings"]["protected_channels"]:
                self.config["channel_settings"]["protected_channels"].remove(channel_id)
                self.save_config()
                
                self.bot_logger.log_action(
                    action="channel_removed_from_protection",
                    chat_id=channel_id,
                    admin_id=query.from_user.id if query.from_user else None,
                    admin_username=query.from_user.username if query.from_user else None
                )
                
                keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"✅ تم حذف القناة {channel_id} من قائمة الحماية بنجاح!",
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text("❌ القناة غير موجودة في قائمة الحماية!")
                
        elif query.data.startswith("remove_admin_"):
            # Handle admin removal
            admin_id = int(query.data.replace("remove_admin_", ""))
            
            if admin_id in self.config["channel_settings"]["monitored_admins"]:
                self.config["channel_settings"]["monitored_admins"].remove(admin_id)
                self.save_config()
                
                self.bot_logger.log_action(
                    action="admin_removed_from_monitor",
                    user_id=admin_id,
                    admin_id=query.from_user.id if query.from_user else None,
                    admin_username=query.from_user.username if query.from_user else None
                )
                
                keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"✅ تم حذف المشرف {admin_id} من قائمة المراقبة بنجاح!",
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text("❌ المشرف غير موجود في قائمة المراقبة!")
                
        elif query.data.startswith("show_channel_admins_"):
            # Show current admins in channel
            channel_id = int(query.data.replace("show_channel_admins_", ""))
            await self.show_channel_admins(update, context, channel_id)
            
        elif query.data.startswith("show_monitored_status_"):
            # Show status of monitored admins
            channel_id = int(query.data.replace("show_monitored_status_", ""))
            await self.show_monitored_status(update, context, channel_id)
            
        elif query.data == "main_menu":
            # Show main menu using the new dynamic interface
            await self.show_main_menu(update, context)
    
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
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the main menu based on current state"""
        welcome_message = self.messages.get_message("welcome")
        
        # Check if there are protected channels
        protected_channels = self.config.get("channel_settings", {}).get("protected_channels", [])
        
        keyboard = []
        
        if not protected_channels:
            # No channels added yet - show only add channel button
            keyboard = [
                [InlineKeyboardButton("🛡️ إضافة قناة للحماية", callback_data="add_channel")]
            ]
        else:
            # Channels exist - show add channel and channel-specific admin buttons
            keyboard = [
                [InlineKeyboardButton("🛡️ إضافة قناة جديدة للحماية", callback_data="add_channel")]
            ]
            
            # Add button for each protected channel to add admins
            for channel_id in protected_channels:
                try:
                    # Get channel info
                    channel_info = await context.bot.get_chat(channel_id)
                    channel_name = channel_info.title or f"Channel {channel_id}"
                    button_text = f"👤 إضافة مشرف للقناة {channel_name}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"add_admin_to_channel_{channel_id}")])
                except:
                    # If can't get channel info, use ID
                    button_text = f"👤 إضافة مشرف للقناة {channel_id}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"add_admin_to_channel_{channel_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        elif hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup)

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
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for ID input"""
        if not update.message or not update.message.text or not update.effective_user:
            return
            
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        # Check if we're waiting for input from this user
        waiting_for = context.user_data.get('waiting_for')
        
        if waiting_for == 'channel_id':
            await self.handle_channel_id_input(update, context, text)
        elif waiting_for == 'admin_id':
            await self.handle_admin_id_input(update, context, text)
    
    async def handle_channel_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id_text: str):
        """Handle channel ID input"""
        user = update.effective_user
        
        try:
            channel_id = int(channel_id_text)
        except ValueError:
            await update.message.reply_text(
                "❌ معرف القناة غير صحيح\n"
                "يجب أن يكون رقم صحيح مثل: -1001234567890"
            )
            return
        
        try:
            # Check if user is member of the channel and get their status
            member = await context.bot.get_chat_member(channel_id, user.id)
            if member.status not in ['creator', 'administrator']:
                await update.message.reply_text(
                    "❌ يجب أن تكون مالك القناة أو مشرف لإضافتها للحماية"
                )
                return
                
            # Get channel info
            channel_info = await context.bot.get_chat(channel_id)
            channel_title = channel_info.title or f"Channel {channel_id}"
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ فشل في الوصول للقناة {channel_id}\n"
                "تأكد من:\n"
                "• صحة معرف القناة\n"
                "• إضافة البوت كمشرف في القناة\n"
                "• منح البوت الصلاحيات المطلوبة"
            )
            context.user_data.pop('waiting_for', None)
            return
        
        # Add channel to protected list if not already there
        if channel_id not in self.config["channel_settings"]["protected_channels"]:
            self.config["channel_settings"]["protected_channels"].append(channel_id)
            self.save_config()
            
            self.bot_logger.log_action(
                action="channel_added_to_protection",
                chat_id=channel_id,
                admin_id=user.id,
                admin_username=user.username
            )
            
            # Create inline keyboard with remove option
            keyboard = [
                [InlineKeyboardButton(f"🗑️ إزالة القناة {channel_title}", callback_data=f"remove_channel_{channel_id}")],
                [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ تم إضافة القناة {channel_title} إلى قائمة الحماية بنجاح!\n"
                f"🆔 معرف القناة: {channel_id}\n\n"
                "البوت الآن سيراقب أنشطة المشرفين المحددين في هذه القناة.",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(f"⚠️ القناة {channel_title} محمية بالفعل!")
            
        # Clear the waiting state
        context.user_data.pop('waiting_for', None)
    
    async def handle_admin_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_id_text: str):
        """Handle admin ID input"""
        try:
            admin_id = int(admin_id_text)
        except ValueError:
            await update.message.reply_text(
                "❌ معرف المشرف غير صحيح\n"
                "يجب أن يكون رقم صحيح مثل: 123456789"
            )
            return
        
        # Check if this is for a specific channel or general
        target_channel_id = context.user_data.get('target_channel_id')
        
        if target_channel_id:
            # Adding admin for specific channel
            await self.add_admin_to_specific_channel(update, context, admin_id, target_channel_id)
        else:
            # Old general method - check all protected channels  
            await self.add_admin_general(update, context, admin_id)
        
        # Clear the waiting state
        context.user_data.pop('waiting_for', None)
        context.user_data.pop('target_channel_id', None)
    
    async def add_admin_to_specific_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_id: int, channel_id: int):
        """Add admin for monitoring in specific channel"""
        try:
            # Get channel info for display
            channel_info = await context.bot.get_chat(channel_id)
            channel_name = channel_info.title or f"Channel {channel_id}"
            
            # Check if user is channel owner/creator to allow adding any user
            user_id = update.effective_user.id if update.effective_user else None
            if user_id:
                user_member = await context.bot.get_chat_member(channel_id, user_id)
                is_channel_owner = user_member.status == 'creator'
            else:
                is_channel_owner = False
            
            # Check target user status
            member = await context.bot.get_chat_member(channel_id, admin_id)
            status = member.status
            
            self.logger.info(f"Channel {channel_id}: User {admin_id} status = {status}")
            
            # If target is already admin, proceed directly
            if status in ['creator', 'administrator']:
                add_anyway = True
                status_note = f"✅ المستخدم مشرف فعلي في القناة (حالة: {status})"
            
            # If channel owner wants to add non-admin user, allow with warning
            elif is_channel_owner:
                add_anyway = True
                status_note = f"⚠️ المستخدم ليس مشرف حالياً (حالة: {status})\n"
                status_note += "لكن سيتم إضافته للمراقبة لأنك مالك القناة.\n"
                status_note += "💡 تذكر: سيتم مراقبته فقط إذا أصبح مشرف لاحقاً."
            
            # If not owner and target is not admin, deny
            else:
                add_anyway = False
                was_monitored = admin_id in self.config["channel_settings"]["monitored_admins"]
                
                status_message = f"❌ المعرف {admin_id} ليس مشرف في القناة {channel_name}\n\n"
                status_message += f"📋 حالة المستخدم في القناة: {status}\n\n"
                
                if was_monitored:
                    status_message += "⚠️ تحذير: هذا المستخدم كان مشرف مراقب سابقاً!\n"
                    status_message += "هذا يعني أنه فقد صلاحيات الإدارة أو تم تغيير دوره.\n\n"
                    
                    keyboard = [
                        [InlineKeyboardButton("🗑️ إزالته من قائمة المراقبة", callback_data=f"remove_admin_{admin_id}")],
                        [InlineKeyboardButton("📋 عرض المشرفين الحاليين", callback_data=f"show_channel_admins_{channel_id}")],
                        [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(status_message, reply_markup=reply_markup)
                else:
                    status_message += "💡 ملاحظة: فقط مالك القناة يمكنه إضافة أي مستخدم للمراقبة.\n"
                    status_message += "إذا كنت مالك القناة، تأكد من أن البوت يمكنه رؤية صلاحياتك.\n\n"
                    status_message += "تأكد من:\n"
                    status_message += "• أن المعرف صحيح\n"
                    status_message += "• أن الشخص مشرف فعلي في هذه القناة\n"
                    status_message += "• أن البوت يمكنه رؤية قائمة المشرفين"
                    
                    keyboard = [
                        [InlineKeyboardButton("📋 عرض المشرفين الحاليين", callback_data=f"show_channel_admins_{channel_id}")],
                        [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(status_message, reply_markup=reply_markup)
                
                return
            
            # Proceed with adding if allowed
            if add_anyway:
                # Add admin to monitored list if not already there
                if admin_id not in self.config["channel_settings"]["monitored_admins"]:
                    self.config["channel_settings"]["monitored_admins"].append(admin_id)
                    self.save_config()
                    
                    # Get user info if available
                    try:
                        user_info = await context.bot.get_chat(admin_id)
                        user_name = user_info.first_name or f"User {admin_id}"
                    except:
                        user_name = f"User {admin_id}"
                    
                    # Create success message
                    success_message = f"✅ تم إضافة {user_name} (ID: {admin_id}) لقائمة المراقبة!\n\n"
                    success_message += f"📍 القناة: {channel_name}\n"
                    success_message += f"📋 {status_note}\n\n"
                    
                    # Show which channels this admin is now monitored in
                    protected_channels = self.config["channel_settings"]["protected_channels"]
                    channel_list = []
                    for ch_id in protected_channels:
                        try:
                            ch_info = await context.bot.get_chat(ch_id)
                            channel_list.append(ch_info.title or f"Channel {ch_id}")
                        except:
                            channel_list.append(f"Channel {ch_id}")
                    
                    if len(channel_list) > 1:
                        success_message += f"📋 القنوات المحمية: {', '.join(channel_list)}\n\n"
                    
                    success_message += "البوت الآن سيراقب أنشطة هذا المستخدم."
                    
                    # Log the action
                    self.bot_logger.log_action(
                        action="admin_added_to_monitor",
                        user_id=admin_id,
                        chat_id=channel_id,
                        admin_id=update.effective_user.id if update.effective_user else None,
                        admin_username=update.effective_user.username if update.effective_user else None
                    )
                    
                    keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(success_message, reply_markup=reply_markup)
                else:
                    # Show current status for already monitored admin
                    keyboard = [
                        [InlineKeyboardButton("📋 إظهار حالة المشرفين المراقبين", callback_data=f"show_monitored_status_{channel_id}")],
                        [InlineKeyboardButton("🗑️ إزالة من المراقبة", callback_data=f"remove_admin_{admin_id}")],
                        [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"⚠️ المشرف {admin_id} مراقب بالفعل!\n\n"
                        f"📍 القناة: {channel_name}\n"
                        f"📋 حالته الحالية: {status}\n\n"
                        "💡 يمكنك إظهار حالة جميع المشرفين المراقبين أو إزالته من المراقبة.",
                        reply_markup=reply_markup
                    )
                
        except Exception as e:
            error_msg = f"❌ فشل في الوصول للقناة {channel_id} أو المشرف {admin_id}\n"
            error_msg += f"الخطأ: {str(e)}\n\n"
            error_msg += "تأكد من:\n"
            error_msg += "• صحة معرف المشرف\n"
            error_msg += "• أن البوت يمكنه الوصول للقناة\n"
            error_msg += "• أن المشرف موجود في القناة"
            
            await update.message.reply_text(error_msg)
            self.logger.warning(f"Error adding admin {admin_id} to channel {channel_id}: {e}")
    
    async def add_admin_general(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_id: int):
        """Add admin using old general method - check all protected channels"""
        protected_channels = self.config.get("channel_settings", {}).get("protected_channels", [])
        if not protected_channels:
            await update.message.reply_text("❌ لا توجد قنوات محمية. أضف قناة أولاً.")
            return
            
        # Enhanced admin verification with detailed diagnostics
        admin_status_messages = []
        is_valid_admin = False
        
        for channel_id in protected_channels:
            try:
                member = await context.bot.get_chat_member(channel_id, admin_id)
                status = member.status
                admin_status_messages.append(f"• القناة {channel_id}: الحالة = {status}")
                
                # Log detailed status
                self.logger.info(f"Channel {channel_id}: User {admin_id} status = {status}")
                
                if status in ['creator', 'administrator']:
                    is_valid_admin = True
                    
            except Exception as e:
                error_msg = f"• القناة {channel_id}: خطأ في الوصول - {str(e)}"
                admin_status_messages.append(error_msg)
                self.logger.warning(f"Channel {channel_id}: Error checking admin {admin_id}: {e}")
        
        if not is_valid_admin:
            # Create detailed error message
            diagnostics = "\n".join(admin_status_messages)
            await update.message.reply_text(
                f"❌ المعرف {admin_id} ليس مشرف في أي من القنوات المحمية\n\n"
                f"📋 تفاصيل الفحص:\n{diagnostics}\n\n"
                "تأكد من:\n"
                "• أن المعرف صحيح\n"
                "• أن الشخص مشرف فعلي في إحدى القنوات المحمية\n"
                "• أن البوت يمكنه الوصول للقناة"
            )
            return
        
        # Add admin to monitored list
        if admin_id not in self.config["channel_settings"]["monitored_admins"]:
            self.config["channel_settings"]["monitored_admins"].append(admin_id)
            self.save_config()
            
            self.bot_logger.log_action(
                action="admin_added_to_monitor",
                user_id=admin_id,
                admin_id=update.effective_user.id if update.effective_user else None,
                admin_username=update.effective_user.username if update.effective_user else None
            )
            
            # Get admin info to display
            try:
                admin_info = await context.bot.get_chat(admin_id)
                admin_name = admin_info.first_name or f"Admin {admin_id}"
            except:
                admin_name = f"Admin {admin_id}"
            
            # Show which channels the admin is valid in
            valid_channels = []
            for i, message in enumerate(admin_status_messages):
                if 'creator' in message or 'administrator' in message:
                    valid_channels.append(protected_channels[i])
            
            channel_list = ", ".join(str(ch) for ch in valid_channels)
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ تم إضافة المشرف {admin_id} إلى قائمة المراقبة بنجاح!\n\n"
                f"📋 القنوات التي يراقب فيها: {channel_list}\n\n"
                "البوت الآن سيراقب أنشطة هذا المشرف.",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(f"⚠️ المشرف {admin_id} مراقب بالفعل!")
    
    async def show_channel_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: int):
        """Show current admins in the specified channel"""
        try:
            # Get channel info
            channel_info = await context.bot.get_chat(channel_id)
            channel_name = channel_info.title or f"Channel {channel_id}"
            
            # Get administrators
            administrators = await context.bot.get_chat_administrators(channel_id)
            
            admin_list = []
            for admin in administrators:
                if admin.status == 'creator':
                    admin_list.append(f"👑 {admin.user.first_name or 'Creator'} (المالك) - ID: {admin.user.id}")
                elif admin.status == 'administrator':
                    admin_list.append(f"👤 {admin.user.first_name or 'Admin'} (مشرف) - ID: {admin.user.id}")
            
            if admin_list:
                admins_text = "\n".join(admin_list[:10])  # Show first 10 admins
                if len(admin_list) > 10:
                    admins_text += f"\n... و {len(admin_list) - 10} مشرفين آخرين"
                
                message = f"📋 المشرفين الحاليين في القناة {channel_name}:\n\n{admins_text}\n\n"
                message += "💡 يمكنك نسخ ID أي مشرف لإضافته للمراقبة."
            else:
                message = f"❌ لا يمكن الحصول على قائمة المشرفين في القناة {channel_name}"
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
            else:
                await update.message.reply_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            error_msg = f"❌ فشل في الحصول على قائمة المشرفين للقناة {channel_id}\n"
            error_msg += f"الخطأ: {str(e)}\n\n"
            error_msg += "تأكد من أن البوت لديه صلاحية رؤية المشرفين في القناة."
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(error_msg, reply_markup=reply_markup)
            else:
                await update.message.reply_text(error_msg, reply_markup=reply_markup)
            
            self.logger.warning(f"Error getting admins for channel {channel_id}: {e}")
    
    async def show_monitored_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: int):
        """Show status of all monitored admins in the channel"""
        try:
            # Get channel info
            channel_info = await context.bot.get_chat(channel_id)
            channel_name = channel_info.title or f"Channel {channel_id}"
            
            # Get monitored admins
            monitored_admins = self.config["channel_settings"]["monitored_admins"]
            
            if not monitored_admins:
                message = f"📋 لا يوجد مشرفين مراقبين في القناة {channel_name}"
            else:
                status_list = []
                for admin_id in monitored_admins:
                    try:
                        # Check current status
                        member = await context.bot.get_chat_member(channel_id, admin_id)
                        status = member.status
                        
                        # Get user info
                        try:
                            user_info = await context.bot.get_chat(admin_id)
                            user_name = user_info.first_name or f"User {admin_id}"
                        except:
                            user_name = f"User {admin_id}"
                        
                        if status == 'creator':
                            status_icon = "👑"
                            status_text = "مالك القناة"
                        elif status == 'administrator':
                            status_icon = "👤"
                            status_text = "مشرف فعال"
                        elif status == 'member':
                            status_icon = "⚠️"
                            status_text = "عضو عادي (ليس مشرف)"
                        elif status == 'left':
                            status_icon = "❌"
                            status_text = "غادر القناة"
                        elif status == 'kicked':
                            status_icon = "🚫"
                            status_text = "محظور"
                        else:
                            status_icon = "❓"
                            status_text = f"حالة غير معروفة: {status}"
                        
                        status_list.append(f"{status_icon} {user_name} (ID: {admin_id})\n   └── {status_text}")
                        
                    except Exception as e:
                        status_list.append(f"❓ User {admin_id}\n   └── خطأ في الفحص: {str(e)}")
                
                status_text = "\n\n".join(status_list)
                message = f"📋 حالة المشرفين المراقبين في القناة {channel_name}:\n\n{status_text}\n\n"
                message += "💡 المشرفين الذين ليسوا فعالين لن يتم مراقبة أنشطتهم."
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
            else:
                await update.message.reply_text(message, reply_markup=reply_markup)
                
        except Exception as e:
            error_msg = f"❌ فشل في الحصول على حالة المشرفين المراقبين للقناة {channel_id}\n"
            error_msg += f"الخطأ: {str(e)}"
            
            keyboard = [[InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(error_msg, reply_markup=reply_markup)
            else:
                await update.message.reply_text(error_msg, reply_markup=reply_markup)
            
            self.logger.warning(f"Error getting monitored status for channel {channel_id}: {e}")
