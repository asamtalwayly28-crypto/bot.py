import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# تفعيل سجلات التتبع لمتابعة الأخطاء إن وجدت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أنا بوت حماية المجموعات، عملي هو حذف الروابط تلقائياً 🛡️.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فقط قم بإضافتي مشرفاً في المجموعة وسأقوم بحذف أي رابط يتم إرساله فوراً.")

async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text
        if "http://" in text or "https://" in text or "t.me/" in text:
            try:
                await update.message.delete()
            except Exception as e:
                print(f"Could not delete message: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    # بناء التطبيق بالطريقة الرسمية والمستقرة
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), delete_links))

    print("Bot is starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
