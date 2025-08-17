#!/usr/bin/env python3
"""
Deployment-friendly server entry point
Starts Flask HTTP server as primary process with Telegram bot in background
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

# Global bot application
bot_application = None

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

@app.route('/bot-status')
def bot_status():
    """Bot-specific status endpoint"""
    global bot_application
    if bot_application:
        return jsonify({
            "status": "active",
            "bot": "running",
            "handlers": "loaded"
        })
    return jsonify({
        "status": "starting",
        "bot": "initializing"
    })

def setup_telegram_bot():
    """Setup and start Telegram bot in main thread"""
    global bot_application
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create application
    bot_application = Application.builder().token(bot_token).build()
    
    # Initialize bot handler
    bot_handler = BotHandler()
    
    # Add command handlers
    bot_application.add_handler(CommandHandler("start", bot_handler.start_command))
    bot_application.add_handler(CommandHandler("help", bot_handler.help_command))
    bot_application.add_handler(CommandHandler("status", bot_handler.status_command))
    bot_application.add_handler(CommandHandler("logs", bot_handler.logs_command))
    bot_application.add_handler(CommandHandler("config", bot_handler.config_command))
    bot_application.add_handler(CommandHandler("add_admin", bot_handler.add_admin_command))
    bot_application.add_handler(CommandHandler("remove_admin", bot_handler.remove_admin_command))
    bot_application.add_handler(CommandHandler("list_admins", bot_handler.list_admins_command))
    bot_application.add_handler(CommandHandler("add_channel", bot_handler.add_channel_command))
    
    logger.info("Command handlers added: start, help, status, logs, config, add_admin, remove_admin, list_admins, add_channel")
    
    # Add callback query handler for inline buttons
    bot_application.add_handler(CallbackQueryHandler(bot_handler.button_callback))
    
    # Add message handler for text messages (for ID input)
    bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_text_message))
    
    # Add chat member handler to monitor admin changes
    bot_application.add_handler(ChatMemberHandler(bot_handler.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    
    logger.info("Telegram bot is starting...")
    
    # Start the bot
    bot_application.run_polling(allowed_updates=["message", "chat_member", "callback_query"])

def start_flask_server():
    """Start Flask server in background thread"""
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting HTTP server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

def main():
    """Main function - starts Flask server in background and Telegram bot as main process"""
    # Start Flask server in background thread
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    
    # Give Flask server a moment to start
    import time
    time.sleep(2)
    
    # Setup and run Telegram bot in main thread
    setup_telegram_bot()

if __name__ == "__main__":
    main()