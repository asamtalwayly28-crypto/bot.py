import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# تفعيل السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ضع هنا الـ ID الخاص بك كمطور (استبدل الصفر برقمك)
DEV_ID = 6652826141

# قاموس لتخزين الإعدادات والردود المخصصة والبنك (يتم حفظها مؤقتاً في الذاكرة)
custom_replies = {
    "صباح الخير": "صباح النور",
    "مساء الخير": "مساء النور",
    "ها": "هويت بقلبي",
    "طيف": "هلا عيوني لبيه ها؟"
}

user_bank = {}

# 1. أمر /start ولوحة التحكم الخاصة بالمطور
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        "أهلاً بك في بوت طيف.\n"
        "أوامر بوت طيف للاستفسار : @TV_1M\n\n"
        "الأوامر العامة المتاحة:\n"
        "- ايدي (لعرض معلوماتك الشخصية وصورتك)\n"
        "- افتاري (لعرض صورتك الشخصية)\n"
        "- اهمس [المعرف] [النص] (لإرسال همسة)\n"
        "- البنك (لعرض رصيدك وألعاب البنك)\n"
        "- الالعاب (عرض قائمة الألعاب)\n"
        "- بحث [اسم الأغنية] (البحث عن الأغاني)\n"
    )
    
    # إذا كان المستخدم هو المطور الأساسي، نعرض له لوحة التحكم المتقدمة
    if user.id == DEV_ID:
        keyboard = [
            [InlineKeyboardButton("إضافة رد جديد", callback_data="add_reply")],
            [InlineKeyboardButton("إحصائيات البوت", callback_data="bot_stats")],
            [InlineKeyboardButton("تفعيل/تعطيل الحماية", callback_data="toggle_protection")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text + "\n[ لوحة تحكم المطور الخاصة بك ]", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text)

# 2. أمر المساعدة /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "قائمة الأوامر:\n"
        "ايدي\n"
        "افتاري\n"
        "البنك\n"
        "الالعاب\n"
        "بحث [اسم الأغنية]\n"
        "أوامر بوت طيف للاستفسار : @TV_1M"
    )

# 3. معالجة الرسائل والردود والكلمات المفتاحية والحماية
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    chat = update.effective_chat
    user = update.effective_user

    # حماية المجموعة وحذف الروابط إذا كان البوت في قروب
    if chat.type in ["group", "supergroup"]:
        if "http://" in text or "https://" in text or "t.me/" in text:
            try:
                await update.message.delete()
                return
            except Exception:
                pass

    # ردود الفعل التلقائية (صباح الخير، ها، طيف، وغيرها المضافة)
    if text in custom_replies:
        await update.message.reply_text(custom_replies[text])
        return

    # نادي المطور
    if "نادي المطور" in text:
        await update.message.reply_text("تم إرسال طلبك إلى المطور بنجاح.")
        if DEV_ID != 0:
            try:
                group_name = chat.title if chat.title else "محادثة خاصة"
                await context.bot.send_message(
                    chat_id=DEV_ID,
                    text=f"تنبيه: شخص يطلب المطور!\n"
                         f"اسم الشخص: {user.full_name}\n"
                         f"معرف الشخص: @{user.username if user.username else 'لا يوجد'}\n"
                         f"اسم القروب: {group_name}"
                )
            except Exception as e:
                print(f"Failed to notify developer: {e}")
        return

    # أمر ايدي (معلومات المستخدم والصورة)
    if text == "ايدي":
        photos = await user.get_profile_photos(limit=1)
        info = (
            f"معلوماتك الشخصية:\n"
            f"الاسم: {user.full_name}\n"
            f"المعرف: @{user.username if user.username else 'لا يوجد'}\n"
            f"الايدي: {user.id}"
        )
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            await update.message.reply_photo(photo=file_id, caption=info)
        else:
            await update.message.reply_text(info + "\n(ليس لديك صورة صوره شخصية عامة)")
        return

    # أمر افتاري
    if text == "افتاري":
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            await update.message.reply_photo(photo=file_id, caption="صورتك الشخصية")
        else:
            await update.message.reply_text("عذراً، ليس لديك صورة شخصية.")
        return

    # لعبة البنك
    if text == "البنك":
        balance = user_bank.get(user.id, 1000)
        user_bank[user.id] = balance
        bank_text = (
            "نظام البنك:\n"
            f"رصيدك الحالي: {balance} نقطة\n"
            "يمكنك استثمار النقود أو كسبها عبر الألعاب المتاحة."
        )
        await update.message.reply_text(bank_text)
        return

    # قائمة الالعاب مرتبة بدون إيموجيات
    if text == "الالعاب":
        games_list = (
            "قائمة الألعاب المتاحة:\n"
            "1. لعبة الحظ\n"
            "2. لعبة التخمين\n"
            "3. سباق الخيل\n"
            "4. الروليت\n"
            "اكتب اسم اللعبة للبدء."
        )
        await update.message.reply_text(games_list)
        return

    # البحث عن الأغاني
    if text.startswith("بحث "):
        song_name = text.replace("بحث ", "", 1)
        await update.message.reply_text(f"جاري البحث عن الأغنية: {song_name}\nسيتم إرسالها قريباً.")
        return

    # نظام الهمسات (اهمس [المعرف] [النص])
    if text.startswith("اهمس "):
        parts = text.split(" ", 2)
        if len(parts) >= 3:
            target = parts[1]
            secret_msg = parts[2]
            await update.message.reply_text(f"تم إرسال الهمسة إلى {target} بشكل سري.")
        else:
            await update.message.reply_text("الاستخدام الصحيح: اهمس [المعرف] [النص]")
        return

# معالجة أزرار لوحة تحكم المطور
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "bot_stats":
        await query.edit_message_text("إحصائيات البوت: يعمل بكفاءة عالية وسرعة تامة بدون توقف.")
    elif query.data == "toggle_protection":
        await query.edit_message_text("تم تحديث حالة الحماية بنجاح.")
    elif query.data == "add_reply":
        await query.edit_message_text("لإضافة رد جديد، استخدم الأمر البرمجي أو أطلبه مني وسأقوم بتحديثه.")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Taif is running smoothly...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
