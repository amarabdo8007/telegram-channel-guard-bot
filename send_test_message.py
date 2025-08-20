#!/usr/bin/env python3
"""
Send test message to verify bot works
"""

import os
import asyncio
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_test():
    """Send test message to check bot functionality"""
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found")
        return
    
    # Your user ID (from the logs I saw earlier: 6854864464)
    test_user_id = 6854864464
    
    try:
        bot = Bot(token=token)
        
        # Send test message
        message = """🤖 اختبار البوت

البوت يعمل بشكل صحيح!

الميزات المتاحة:
• /start - بدء التفاعل مع البوت
• /help - عرض المساعدة  
• /status - حالة البوت
• /add_channel - إضافة قناة للمراقبة

البوت جاهز للاستخدام! ✅"""

        logger.info(f"Sending test message to user {test_user_id}")
        
        await bot.send_message(
            chat_id=test_user_id,
            text=message
        )
        
        logger.info("✅ Test message sent successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to send test message: {e}")

if __name__ == "__main__":
    asyncio.run(send_test())