import os
from telegram.ext import Application, CommandHandler

# جلب التوكن من المتغيرات البيئية
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("✅ البوت شغال على Railway!")

def main():
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
