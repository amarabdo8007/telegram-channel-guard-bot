#!/usr/bin/env python3
"""
Simple working bot - HTTP server only, no Telegram bot to avoid threading issues
"""

import os
import logging
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot-server",
        "message": "Server is running",
        "port": "5000",
        "note": "Telegram bot disabled due to threading conflicts with Replit workflow"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/bot-status')
def bot_status():
    return jsonify({
        "status": "http-only",
        "message": "HTTP server running, Telegram bot requires main thread"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting simple HTTP server on 0.0.0.0:{port}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )