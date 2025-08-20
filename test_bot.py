#!/usr/bin/env python3
"""
Test script to verify bot functionality
"""

import os
import asyncio
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot():
    """Test bot connectivity and basic functionality"""
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found")
        return
    
    try:
        bot = Bot(token=token)
        
        # Test bot connection
        logger.info("Testing bot connection...")
        me = await bot.get_me()
        logger.info(f"Bot connected: @{me.username} ({me.first_name})")
        
        # Test bot status
        logger.info("Bot details:")
        logger.info(f"- ID: {me.id}")
        logger.info(f"- Username: {me.username}")
        logger.info(f"- Name: {me.first_name}")
        logger.info(f"- Can read messages: {not me.can_read_all_group_messages}")
        
        # Get updates to see if bot is receiving messages
        logger.info("Checking for recent updates...")
        updates = await bot.get_updates(limit=5)
        logger.info(f"Recent updates count: {len(updates)}")
        
        if updates:
            logger.info("Recent messages:")
            for update in updates[-3:]:  # Show last 3
                if update.message:
                    msg = update.message
                    logger.info(f"- From {msg.from_user.first_name}: {msg.text}")
        
        logger.info("✅ Bot test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Bot test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())