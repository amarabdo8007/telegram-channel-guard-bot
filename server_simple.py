#!/usr/bin/env python3
"""
Simple, reliable server entry point that prioritizes HTTP binding
"""

import os
import logging
import threading
import time
from flask import Flask, jsonify
from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handler import BotHandler
from logger import setup_logging

# Setup logging first
try:
    logger = setup_logging()
except:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Flask app for health checks
app = Flask(__name__)

# Global bot application status
bot_status = {"running": False, "initialized": False}

@app.route('/')
def health_check():
    """Primary health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot",
        "message": "Bot is running",
        "bot_initialized": bot_status["initialized"],
        "bot_running": bot_status["running"],
        "timestamp": os.environ.get("REPL_ID", "local"),
        "port": "5000"
    }), 200

@app.route('/health')
def health():
    """Alternative health endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/bot-status')
def bot_status_endpoint():
    """Detailed bot status"""
    return jsonify({
        "bot": "running" if bot_status["running"] else "stopped",
        "handlers": "loaded" if bot_status["initialized"] else "not loaded",
        "status": "active" if bot_status["running"] else "inactive",
        "application_running": True
    }), 200

@app.route('/ping')
def ping():
    """Simple connectivity test"""
    return "pong", 200

def run_bot():
    """Run Telegram bot in background thread"""
    try:
        # Get bot token
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
            return
        
        # Create application
        application = Application.builder().token(bot_token).build()
        bot_status["initialized"] = True
        
        # Initialize bot handler
        bot_handler = BotHandler()
        
        # Add handlers
        application.add_handler(CommandHandler("start", bot_handler.start_command))
        application.add_handler(CommandHandler("help", bot_handler.help_command))
        application.add_handler(CommandHandler("status", bot_handler.status_command))
        application.add_handler(CommandHandler("logs", bot_handler.logs_command))
        application.add_handler(CommandHandler("config", bot_handler.config_command))
        application.add_handler(CommandHandler("add_admin", bot_handler.add_admin_command))
        application.add_handler(CommandHandler("remove_admin", bot_handler.remove_admin_command))
        application.add_handler(CommandHandler("list_admins", bot_handler.list_admins_command))
        application.add_handler(CommandHandler("add_channel", bot_handler.add_channel_command))
        application.add_handler(CallbackQueryHandler(bot_handler.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_text_message))
        application.add_handler(ChatMemberHandler(bot_handler.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
        
        logger.info("Command handlers added: start, help, status, logs, config, add_admin, remove_admin, list_admins, add_channel")
        logger.info("Telegram bot is starting...")
        
        bot_status["running"] = True
        
        # Run bot
        application.run_polling(
            allowed_updates=["message", "chat_member", "callback_query"],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
        bot_status["running"] = False
    finally:
        bot_status["running"] = False

def main():
    """Main function"""
    # Start bot in background thread immediately
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Give bot a moment to initialize
    time.sleep(2)
    
    # Start Flask server on main thread (required for workflow port detection)
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting HTTP server on 0.0.0.0:{port}")
    
    try:
        app.run(
            host="0.0.0.0", 
            port=port, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()