#!/usr/bin/env python3
"""Ultra-simple server that prioritizes Flask HTTP binding"""

import os
import threading
import time
import logging
from flask import Flask, jsonify
from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handler import BotHandler

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
bot_running = False

@app.route('/')
def health():
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot", 
        "message": "Bot is running",
        "bot_initialized": bot_running,
        "port": "5000"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/bot-status')  
def bot_status():
    return jsonify({
        "bot": "running" if bot_running else "stopped",
        "status": "active" if bot_running else "inactive",
        "application_running": True
    })

def start_bot():
    """Start Telegram bot"""
    global bot_running
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("No bot token found")
            return
            
        # Create bot
        app_bot = Application.builder().token(token).build()
        handler = BotHandler()
        
        # Add handlers
        app_bot.add_handler(CommandHandler("start", handler.start_command))
        app_bot.add_handler(CommandHandler("help", handler.help_command))
        app_bot.add_handler(CommandHandler("status", handler.status_command))
        app_bot.add_handler(CommandHandler("logs", handler.logs_command))
        app_bot.add_handler(CommandHandler("config", handler.config_command))
        app_bot.add_handler(CommandHandler("add_admin", handler.add_admin_command))
        app_bot.add_handler(CommandHandler("remove_admin", handler.remove_admin_command))
        app_bot.add_handler(CommandHandler("list_admins", handler.list_admins_command))
        app_bot.add_handler(CommandHandler("add_channel", handler.add_channel_command))
        app_bot.add_handler(CallbackQueryHandler(handler.button_callback))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_text_message))
        app_bot.add_handler(ChatMemberHandler(handler.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
        
        print("Starting Telegram bot...")
        bot_running = True
        
        app_bot.run_polling(
            allowed_updates=["message", "chat_member", "callback_query"],
            drop_pending_updates=True
        )
        
    except Exception as e:
        print(f"Bot error: {e}")
        bot_running = False

def main():
    # Start bot in background
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Small delay for bot startup
    time.sleep(1)
    
    # Start Flask server - this MUST run on main thread for port binding
    print("Starting HTTP server on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()