#!/usr/bin/env python3
"""
Deployment-friendly server entry point
Starts Flask HTTP server as primary process with Telegram bot in background
"""

import os
import asyncio
import logging
import threading
import time
import atexit
from flask import Flask, jsonify
from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handler import BotHandler
from logger import setup_logging

# Flask app for health checks
app = Flask(__name__)

# Global bot application
bot_application = None
bot_lock_file = "/tmp/telegram_bot.lock"

def create_lock_file():
    """Create a lock file to prevent multiple instances"""
    try:
        with open(bot_lock_file, 'w') as f:
            f.write(str(os.getpid()))
        atexit.register(remove_lock_file)
        return True
    except:
        return False

def remove_lock_file():
    """Remove the lock file"""
    try:
        if os.path.exists(bot_lock_file):
            os.remove(bot_lock_file)
    except:
        pass

def is_another_instance_running():
    """Check if another instance is running"""
    if not os.path.exists(bot_lock_file):
        return False
    try:
        with open(bot_lock_file, 'r') as f:
            pid = int(f.read().strip())
        # Check if process is still running
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Process doesn't exist, remove stale lock file
        remove_lock_file()
        return False

@app.route('/')
def health_check():
    """Primary health check endpoint for deployment"""
    try:
        global bot_application
        bot_running = bot_application is not None
        return jsonify({
            "status": "healthy",
            "service": "telegram-bot",
            "message": "Bot is running",
            "bot_initialized": bot_running,
            "timestamp": os.environ.get("REPL_ID", "local"),
            "port": os.environ.get("PORT", "5000")
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/health')
def health():
    """Simplified health endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/bot-status')
def bot_status():
    """Detailed bot status endpoint"""
    global bot_application
    try:
        if bot_application:
            return jsonify({
                "status": "active",
                "bot": "running", 
                "handlers": "loaded",
                "application_running": True
            }), 200
        return jsonify({
            "status": "starting",
            "bot": "initializing",
            "application_running": False
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/ping')
def ping():
    """Simple ping endpoint for basic connectivity test"""
    return "pong", 200

def setup_telegram_bot():
    """Setup and start Telegram bot in main thread"""
    global bot_application
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check if another instance is running
    if is_another_instance_running():
        logger.warning("Another bot instance is already running. Skipping bot startup.")
        return
    
    # Create lock file
    if not create_lock_file():
        logger.error("Failed to create lock file. Another instance may be running.")
        return
    
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create application with improved configuration for conflict resolution
    bot_application = Application.builder().token(bot_token).build()
    
    # Note: Webhook clearing will be handled by run_polling automatically
    
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
    
    # Simple, robust bot startup with built-in conflict resolution
    try:
        bot_application.run_polling(
            allowed_updates=["message", "chat_member", "callback_query"],
            drop_pending_updates=True  # This automatically clears webhooks and pending updates
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Bot polling error: {error_msg}")
        
        if "Conflict" in error_msg or "409" in error_msg:
            logger.error("Conflict detected: Another bot instance is running with the same token")
            logger.error("Please ensure only one instance of the bot is running")
        else:
            logger.error(f"Unexpected bot error: {error_msg}")
            raise

def start_flask_server():
    """Start Flask server in main thread"""
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting HTTP server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

def main():
    """Main function - starts Telegram bot in background and Flask server as main process"""
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=setup_telegram_bot, daemon=False)
    bot_thread.start()
    
    # Give bot a moment to start
    import time
    time.sleep(3)
    
    # Start Flask server in main thread - this ensures port is properly bound
    try:
        start_flask_server()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        remove_lock_file()

if __name__ == "__main__":
    main()