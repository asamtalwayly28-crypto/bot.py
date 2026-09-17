import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text
        if "http://" in text or "https://" in text or "t.me/" in text:
            try:
                await update.message.delete()
            except Exception as e:
                print(e)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), delete_links))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
