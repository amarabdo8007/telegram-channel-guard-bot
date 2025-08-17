#!/usr/bin/env python3
"""
Telegram Channel Protection Bot
Main entry point for the bot application
"""

import os
import asyncio
import logging
import threading
from flask import Flask, jsonify
from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handler import BotHandler
from logger import setup_logging

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for deployment"""
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot",
        "message": "Bot is running"
    })

@app.route('/health')
def health():
    """Additional health endpoint"""
    return jsonify({"status": "ok"})

def run_flask_server():
    """Run Flask server in a separate thread"""
    port = int(os.environ.get("PORT", 5000))
    # Ensure the server is accessible for deployment health checks
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

def main():
    """Main function to start the bot and health check server"""
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
    application.add_handler(CommandHandler("add_channel", bot_handler.add_channel_command))
    
    logger.info("Command handlers added: start, help, status, logs, config, add_admin, remove_admin, list_admins, add_channel")
    
    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(bot_handler.button_callback))
    
    # Add message handler for text messages (for ID input)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_text_message))
    
    # Add chat member handler to monitor admin changes
    application.add_handler(ChatMemberHandler(bot_handler.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    
    logger.info("Telegram bot is starting...")
    
    # Start bot in background thread to keep main thread for Flask
    def run_bot():
        application.run_polling(allowed_updates=["message", "chat_member", "callback_query"])
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Small delay for bot to initialize
    import time
    time.sleep(3)
    logger.info("Bot started in background, starting HTTP server...")
    
    # Start Flask server in main thread (required for workflow port detection)
    run_flask_server()

if __name__ == "__main__":
    main()
