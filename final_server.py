#!/usr/bin/env python3
"""
Final stable server that guarantees HTTP port binding for workflow detection
"""

import os
import asyncio
import threading
import time
import logging
from flask import Flask, jsonify
from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handler import BotHandler

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
bot_status = {"running": False, "error": None}

@app.route('/')
def health():
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot",
        "message": "Bot is running",
        "bot_initialized": bot_status["running"],
        "bot_error": bot_status["error"],
        "port": "5000"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/bot-status')
def bot_status_endpoint():
    return jsonify({
        "bot": "running" if bot_status["running"] else "stopped",
        "status": "active" if bot_status["running"] else "inactive",
        "error": bot_status["error"],
        "application_running": True
    })

def run_telegram_bot():
    """Run telegram bot with proper async handling"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            bot_status["error"] = "No bot token found"
            return
            
        # Create bot application
        application = Application.builder().token(token).build()
        handler = BotHandler()
        
        # Add all handlers
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
        
        logger.info("Telegram bot handlers loaded")
        bot_status["running"] = True
        
        # Run the bot
        application.run_polling(
            allowed_updates=["message", "chat_member", "callback_query"],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
        bot_status["error"] = str(e)
        bot_status["running"] = False
    finally:
        # Close event loop properly
        if 'loop' in locals():
            loop.close()

def main():
    """Main function - HTTP server in main thread, bot in background"""
    
    # Start telegram bot in background thread with proper async handling
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=False)
    bot_thread.start()
    
    # Give bot a moment to start
    time.sleep(2)
    logger.info("Bot thread started, starting HTTP server...")
    
    # Run Flask in main thread for proper port binding
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"HTTP server binding to 0.0.0.0:{port}")
    
    try:
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Flask server error: {e}")

if __name__ == "__main__":
    main()