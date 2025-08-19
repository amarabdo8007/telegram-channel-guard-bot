#!/bin/bash
# Script لتشغيل البوت تلقائياً

echo "🚀 Starting Telegram Bot..."

# Check if bot token exists
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN not found!"
    echo "Please add your bot token in Replit Secrets"
    exit 1
fi

echo "✅ Bot token found"

# Kill any existing bot processes
pkill -f "python3 run_bot.py" 2>/dev/null
pkill -f "python3 keep_alive.py" 2>/dev/null

sleep 2

# Start the bot
echo "🤖 Starting bot with keep-alive..."
python3 keep_alive.py &

echo "✅ Bot started in background"
echo "📱 Test your bot by sending /start in Telegram"
echo "📊 Check logs in the Console tab"

# Keep script running
while true; do
    sleep 60
    echo "⏰ Bot monitor check - $(date)"
done