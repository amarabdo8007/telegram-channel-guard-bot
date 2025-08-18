#!/usr/bin/env python3
"""
Final solution: Run Telegram bot with immediate HTTP server binding for Replit workflow
Uses HTTP server for health checks and runs Telegram bot manually without conflicts
"""

import os
import sys
import asyncio
import logging
import threading
import time
from flask import Flask, jsonify

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for status tracking
bot_status = {
    "initialized": False,
    "running": False,
    "error": None,
    "last_update": None
}

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot",
        "message": "Server running",
        "bot_initialized": bot_status["initialized"],
        "bot_running": bot_status["running"],
        "bot_error": bot_status["error"],
        "port": "5000"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/bot-status')
def bot_status_endpoint():
    return jsonify(bot_status)

def setup_and_run_telegram_bot():
    """Setup and run Telegram bot in separate thread with proper async loop"""
    try:
        # Create and set new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
        from bot_handler import BotHandler
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            bot_status["error"] = "No TELEGRAM_BOT_TOKEN found"
            logger.error("No TELEGRAM_BOT_TOKEN found in environment")
            return
        
        logger.info("Initializing Telegram bot...")
        bot_status["initialized"] = True
        
        # Create application
        application = Application.builder().token(token).build()
        handler = BotHandler()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", handler.start_command))
        application.add_handler(CommandHandler("help", handler.help_command))
        application.add_handler(CommandHandler("status", handler.status_command))
        application.add_handler(CommandHandler("logs", handler.logs_command))
        application.add_handler(CommandHandler("config", handler.config_command))
        application.add_handler(CommandHandler("add_admin", handler.add_admin_command))
        application.add_handler(CommandHandler("remove_admin", handler.remove_admin_command))
        application.add_handler(CommandHandler("list_admins", handler.list_admins_command))
        application.add_handler(CommandHandler("add_channel", handler.add_channel_command))
        
        # Add other handlers
        application.add_handler(CallbackQueryHandler(handler.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_text_message))
        application.add_handler(ChatMemberHandler(handler.chat_member_update, ChatMemberHandler.CHAT_MEMBER))
        
        logger.info("Bot handlers configured, starting polling...")
        bot_status["running"] = True
        bot_status["last_update"] = time.time()
        
        # Run polling
        application.run_polling(
            allowed_updates=["message", "chat_member", "callback_query"],
            drop_pending_updates=True
        )
        
    except Exception as e:
        error_msg = f"Bot error: {str(e)}"
        logger.error(error_msg)
        bot_status["error"] = error_msg
        bot_status["running"] = False
    finally:
        # Clean up event loop
        try:
            if 'loop' in locals() and not loop.is_closed():
                loop.close()
        except Exception as e:
            logger.error(f"Error closing event loop: {e}")

def main():
    """Main function - starts HTTP server immediately and bot in background"""
    
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting application on port {port}")
    
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=setup_and_run_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("Telegram bot thread started")
    
    # Small delay to let bot initialize
    time.sleep(1)
    
    # Start Flask HTTP server in main thread (required for workflow port detection)
    logger.info(f"Starting HTTP server on 0.0.0.0:{port}")
    try:
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"HTTP server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()