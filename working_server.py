#!/usr/bin/env python3
"""
Working server that binds HTTP port immediately for workflow detection
"""

import os
import logging
from flask import Flask, jsonify

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot",
        "message": "HTTP server is running - Bot loading...",
        "port": "5000"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/bot-status')
def bot_status():
    return jsonify({
        "status": "starting",
        "message": "Bot initialization in progress"
    })

def setup_telegram_bot():
    """Setup telegram bot after HTTP server is running"""
    try:
        from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackQueryHandler, MessageHandler, filters
        from bot_handler import BotHandler
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("No TELEGRAM_BOT_TOKEN found")
            return
            
        logger.info("Setting up Telegram bot...")
        
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
        
        logger.info("Starting Telegram bot polling...")
        
        # Start bot polling in a simple way
        application.run_polling(
            allowed_updates=["message", "chat_member", "callback_query"],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Bot setup error: {e}")

# Add bot startup to Flask's before_first_request equivalent
@app.before_request
def setup_bot():
    """Setup bot on first request"""
    if not hasattr(setup_bot, 'done'):
        setup_bot.done = True
        import threading
        bot_thread = threading.Thread(target=setup_telegram_bot, daemon=True)
        bot_thread.start()

def main():
    """Main function"""
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting HTTP server on 0.0.0.0:{port}")
    
    # Start Flask immediately - this ensures port binding for workflow
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )

if __name__ == "__main__":
    main()