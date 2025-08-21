#!/usr/bin/env python3
"""
Direct bot runner - Telegram bot in main thread, simple HTTP in background
"""

import os
import logging
import threading
import time
from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handler import BotHandler
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple Flask app for health checks and uptime monitoring
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "bot": "running"})

@app.route('/status')
def status():
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot", 
        "message": "Channel Guard Bot is active",
        "uptime": "online"
    })

def run_http_server():
    """Run HTTP server in background for health checks and uptime monitoring"""
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

def main():
    """Main function - bot in main thread"""
    
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    time.sleep(2)  # Let HTTP server start
    
    # Get token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found")
        return
    
    logger.info("Starting Telegram bot in main thread...")
    
    # Create application
    application = Application.builder().token(token).build()
    handler = BotHandler()
    
    # Add handlers
    application.add_handler(CommandHandler("start", handler.start_command))
    application.add_handler(CommandHandler("help", handler.help_command))
    application.add_handler(CommandHandler("status", handler.status_command))
    application.add_handler(CommandHandler("logs", handler.logs_command))
    application.add_handler(CommandHandler("config", handler.config_command))
    application.add_handler(CommandHandler("add_admin", handler.add_admin_command))
    application.add_handler(CommandHandler("remove_admin", handler.remove_admin_command))
    application.add_handler(CommandHandler("list_admins", handler.list_admins_command))
    application.add_handler(CommandHandler("add_channel", handler.add_channel_command))
    application.add_handler(CallbackQueryHandler(handler.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_text_message))
    application.add_handler(ChatMemberHandler(handler.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    
    logger.info("Bot started and ready!")
    
    # Run bot in main thread
    application.run_polling(
        allowed_updates=["message", "chat_member", "callback_query"],
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()