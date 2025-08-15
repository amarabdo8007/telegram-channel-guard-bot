#!/usr/bin/env python3
"""
Telegram Channel Protection Bot
Main entry point for the bot application
"""

import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler, ChatMemberHandler
from bot_handler import BotHandler
from logger import setup_logging

def main():
    """Main function to start the bot"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Initialize bot handler
    bot_handler = BotHandler()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot_handler.start_command))
    application.add_handler(CommandHandler("help", bot_handler.help_command))
    application.add_handler(CommandHandler("status", bot_handler.status_command))
    application.add_handler(CommandHandler("logs", bot_handler.logs_command))
    application.add_handler(CommandHandler("config", bot_handler.config_command))
    application.add_handler(CommandHandler("add_admin", bot_handler.add_admin_command))
    application.add_handler(CommandHandler("remove_admin", bot_handler.remove_admin_command))
    application.add_handler(CommandHandler("list_admins", bot_handler.list_admins_command))
    
    # Add chat member handler to monitor admin changes
    application.add_handler(ChatMemberHandler(bot_handler.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    
    logger.info("Bot is starting...")
    
    # Start the bot
    application.run_polling(allowed_updates=["message", "chat_member"])

if __name__ == "__main__":
    main()
