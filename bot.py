import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# دالة أمر /start (للترحيب بالمستخدم)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أنا بوت حماية المجموعات، عملي هو حذف الروابط تلقائياً 🛡️.")

# دالة أمر /help (لمساعدة المستخدمين)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فقط قم بإضافتي مشرفاً في المجموعة وسأقوم بحذف أي رابط يتم إرساله فوراً.")

# دالة حذف الروابط التلقائية
async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text
        # التحقق إذا كانت الرسالة تحتوي على رابط
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

    app = ApplicationBuilder().token(TOKEN).build()

    # إضافة الأوامر الجديدة
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # مراقبة الرسائل وحذف الروابط
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), delete_links))

    print("Bot is running with new commands...")
    app.run_polling()

if __name__ == "__main__":
    main()
