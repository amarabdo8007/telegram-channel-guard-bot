#!/usr/bin/env python3
"""
Keep-alive script to ensure bot stays running
"""

import os
import time
import subprocess
import logging
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def keep_bot_alive():
    """Keep the bot running and restart if it stops"""
    while True:
        try:
            logger.info("Starting Telegram bot...")
            # Run the bot
            process = subprocess.Popen(["python3", "run_bot.py"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            # Wait for process to complete
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Bot stopped with error: {stderr.decode()}")
            else:
                logger.info("Bot stopped normally")
                
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        
        # Wait before restarting
        logger.info("Waiting 10 seconds before restart...")
        time.sleep(10)

def run_health_server():
    """Simple health check server"""
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def health():
        return jsonify({"status": "alive", "service": "telegram-bot"})
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "ok"})
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start health server in background
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Keep bot alive in main thread
    keep_bot_alive()