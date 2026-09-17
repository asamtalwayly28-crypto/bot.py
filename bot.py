import os
import logging
import random
import yt_dlp
from telegram import ChatPermissions, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# تفعيل السجلات الفورية
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# الآيدي الخاص بك كمطور ومالك أساسي
DEV_ID = 6652826141 

# تخزين البيانات والردود وقوائم المنع مؤقتاً
custom_replies = {
    "صباح الخير": "صباح النور",
    "مساء الخير": "مساء النور"
}

user_bank = {}
user_states = {}
banned_words = set()
banned_stickers = set()

# الردود المتنوعة عند مناداة البوت
taif_call_responses = [
    "عيوني",
    "لبيه",
    "ها؟",
    "ازعجتني",
    "لا تناديني"
]

# بايوات عشوائية جاهزة
random_bios = [
    "I don't chase, i attracts ✨",
    "عيش وحدك، فالكثير قليل 🖤",
    "الهدوء عنوان الفخامة.",
    "فقط استمر في المضي قدماً 🚀",
    "كن قليل الكلام كثير الصمت."
]

# لوحة المطور الاحترافية مع أزرار شفافة وزر رجوع
def get_main_dev_markup():
    keyboard = [
        [InlineKeyboardButton("إحصائيات البوت", callback_data="dev_stats")],
        [InlineKeyboardButton("إدارة الردود", callback_data="dev_replies")],
        [InlineKeyboardButton("قائمة المنع", callback_data="dev_banned")],
        [InlineKeyboardButton("حماية القروبات", callback_data="dev_protection")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_dev_markup():
    keyboard = [
        [InlineKeyboardButton("رجوع", callback_data="dev_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        "اهلين فيك باوامر البوت\n\n"
        "للإستفسار - @TV_1M\n\n"
        "اكتب ( الاوامر ) لعرض قائمة الأوامر الكاملة."
    )
    
    if user.id == DEV_ID:
        await update.message.reply_text(
            text + "\n\n[ لوحة المطور ]", 
            reply_markup=get_main_dev_markup()
        )
    else:
        await update.message.reply_text(text)

# معالج الرسائل والأوامر الشامل
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    user_id = user.id
    text = message.text or message.caption or ""

    # 1. ترحيب الأعضاء الجدد
    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.id == context.bot.id:
                continue
            welcome_text = (
                f"~ أهلاً بك ياعسل 🤍\n"
                f"~ نورت القروب: {member.full_name}\n"
                f"~ نتمنى لك إقامة ممتعة معنا في {chat.title if chat.title else 'هنا'}!"
            )
            try:
                await message.reply_text(welcome_text)
            except Exception:
                pass
        return

    # 2. نظام المنع والحماية في المجموعات
    if chat.type in ["group", "supergroup"]:
        if "http://" in text or "https://" in text or "t.me/" in text:
            try:
                await message.delete()
                return
            except Exception:
                pass
        
        if text and text in banned_words:
            try:
                await message.delete()
                return
            except Exception:
                pass

        if message.sticker and message.sticker.file_unique_id in banned_stickers:
            try:
                await message.delete()
                return
            except Exception:
                pass

    # 3. أمر الرد بـ "منع"
    if text == "منع" and message.reply_to_message:
        replied_msg = message.reply_to_message
        if replied_msg.text:
            banned_words.add(replied_msg.text)
            await message.reply_text("~ تم إضافه الكلمة إلى قائمة المنع بنجاح.")
            return
        elif replied_msg.sticker:
            banned_stickers.add(replied_msg.sticker.file_unique_id)
            await message.reply_text("~ تم إضافه الملصق إلى قائمة المنع بنجاح.")
            return

    # 4. أمر مسح أو حذف الرسائل بالرد
    if text in ["مسح", "حذف"] and message.reply_to_message:
        if chat.type in ["group", "supergroup"]:
            try:
                await message.reply_to_message.delete()
                await message.delete()
            except Exception:
                pass
        return

    # 5. أوامر الإدارة والحماية بالرد (حظر، طرد، كتم، فك كتم، تقييد)
    if message.reply_to_message and chat.type in ["group", "supergroup"]:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        try:
            if text == "حظر":
                await chat.ban_member(target_id)
                await message.reply_text(f"~ تم حظر العضو: {target_user.full_name} بنجاح.")
                return
            elif text == "طرد":
                await chat.ban_member(target_id)
                await chat.unban_member(target_id)
                await message.reply_text(f"~ تم طرد العضو: {target_user.full_name} بنجاح.")
                return
            elif text == "كتم":
                perms = ChatPermissions(can_send_messages=False, can_send_media_messages=False)
                await chat.restrict_member(target_id, permissions=perms)
                await message.reply_text(f"~ تم كتم العضو: {target_user.full_name} بنجاح.")
                return
            elif text in ["فك كتم", "فك الكتم"]:
                perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
                await chat.restrict_member(target_id, permissions=perms)
                await message.reply_text(f"~ تم إزالة الكتم عن العضو: {target_user.full_name}.")
                return
            elif text == "تقييد":
                perms = ChatPermissions(can_send_messages=True, can_send_media_messages=False, can_send_other_messages=False)
                await chat.restrict_member(target_id, permissions=perms)
                await message.reply_text(f"~ تم تقييد العضو: {target_user.full_name} من إرسال الوسائط.")
                return
        except Exception:
            await message.reply_text("~ عذراً، لا أملك صلاحية كافية أو أن الشخص المشرف أعلى مني رتبة.")
            return

    # 6. الرد عند مناداة البوت بكلمة "طيف" أو "بوت"
    if text in ["طيف", "بوت"]:
        chosen_reply = random.choice(taif_call_responses)
        await message.reply_text(chosen_reply)
        return

    # --- البحث والتحميل الصوتي الحقيقي من يوتيوب ---
    if text.startswith("بحث "):
        query_song = text.replace("بحث ", "", 1).strip()
        if not query_song:
            await message.reply_text("~ يرجى كتابة اسم الأغنية بعد كلمة بحث.")
            return
            
        processing_msg = await message.reply_text(f"~ جاري البحث والتحميل للصوت: {query_song} 🎵...")
        
        file_path = f"audio_{user_id}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"audio_{user_id}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True
        }
        
        try:
            # البحث والتحميل باستخدام yt-dlp
            search_query = f"ytsearch1:{query_song}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                title = info.get('title', query_song)
            
            # رفع الملف الصوتي للدردشة
            with open(file_path, 'rb') as audio_file:
                await message.reply_audio(audio=audio_file, caption=f"~ تم التحميل بنجاح: {title}")
                
            await processing_msg.delete()
        except Exception as e:
            await processing_msg.edit_text("~ عذراً، لم أتمكن من العثور على المقطع أو تحميله حالياً.")
        
        # تنظيف الملف من السيرفر بعد الإرسال
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return

    # --- الأوامر الشخصية وأوامر الرابط ---
    if text in ["ايدي", "معلوماتي"]:
        photos = await user.get_profile_photos(limit=1)
        rank = "مالك اساسي" if user.id == DEV_ID else "عضو مميز"
        username_str = f"@{user.username}" if user.username else "@TV_1M"
        info = (
            f"~ NAM = {user.full_name}\n"
            f"~ USE = {username_str}\n"
            f"~ STA = {rank}\n"
            f"~ ID = {user.id}\n"
            f"~ CR = 2023/07\n"
            f"I don't chase, i attracts"
        )
        if photos.total_count > 0:
            await message.reply_photo(photo=photos.photos[0][0].file_id, caption=info)
        else:
            await message.reply_text(info)
        return

    if text == "الرابط":
        if chat.type in ["group", "supergroup"]:
            try:
                invite_link = await chat.export_invite_link()
                await message.reply_text(f"~ رابط القروب:\n{invite_link}")
            except Exception:
                await message.reply_text("~ عذراً، لا أملك صلاحية جلب الرابط.")
        else:
            await message.reply_text(f"~ رابط حسابك الشخصي: t.me/{user.username}" if user.username else "~ لا يوجد معرف لحسابك.")
        return

    if text == "معلومات الرابط":
        await message.reply_text(f"~ معلومات الدردشة:\n- اسم القروب: {chat.title if chat.title else 'محادثة خاصة'}\n- نوع الدردشة: {chat.type}\n- آيدي الدردشة: {chat.id}")
        return

    if text == "انشاء رابط":
        if chat.type in ["group", "supergroup"]:
            try:
                new_link = await chat.export_invite_link()
                await message.reply_text(f"~ تم إنشاء رابط دعوة جديد:\n{new_link}")
            except Exception:
                await message.reply_text("~ لا أملك صلاحية إنشاء الروابط.")
        return

    if text == "بايو":
        await message.reply_text("~ البايو الخاص بك:\nI don't chase, i attracts ✨")
        return

    if text == "بايو عشوائي":
        await message.reply_text(f"~ بايو مقترح:\n{random.choice(random_bios)}")
        return

    if text == "الانشاء":
        await message.reply_text("~ تاريخ الإنشاء المسجل بالنظام: 2023/07")
        return

    if text == "مجموعاتي":
        await message.reply_text("~ المجموعات التي يديرها البوت نشطة وتعمل بكفاءة عالية.")
        return

    # الأوامر العامة الرئيسية
    if text in ["الاوامر", "الأوامر"]:
        orders_text = (
            "اهلين فيك باوامر البوت\n\n"
            "للإستفسار - @TV_1M\n\n"
            "( الأوامر العامة والأخرى )\n"
            "- الرابط / معلومات الرابط / انشاء رابط\n"
            "- بايو / بايو عشوائي / ايدي / الانشاء / مجموعاتي\n\n"
            "( اوامر التحميل والترفيه )\n"
            "- بحث [اسم الأغنية] (لتحميل وإرسال الصوت)\n\n"
            "( اوامر الإدارة والمنع )\n"
            "- رد بـ ( منع ) لحظر رسالة أو ملصق\n"
            "- رد بـ ( مسح / حذف ) لحذف رسالة\n"
            "- حظر / طرد / كتم / تقييد (بالرد)"
        )
        await message.reply_text(orders_text)
        return

# معالجة أزرار لوحة المطور
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "dev_stats":
        await query.edit_message_text("~ إحصائيات لوحة المطور: البوت يعمل بكفاءة.", reply_markup=get_back_dev_markup())
    elif query.data == "dev_replies":
        await query.edit_message_text("~ إدارة الردود نشطة.", reply_markup=get_back_dev_markup())
    elif query.data == "dev_banned":
        await query.edit_message_text(f"~ قائمة المنع الحالية:\n- الكلمات: {len(banned_words)}\n- الملصقات: {len(banned_stickers)}", reply_markup=get_back_dev_markup())
    elif query.data == "dev_protection":
        await query.edit_message_text("~ حماية القروبات مفعلة بالكامل.", reply_markup=get_back_dev_markup())
    elif query.data == "dev_back":
        await query.edit_message_text("اهلين فيك باوامر البوت\n\nللإستفسار - @TV_1M\n\n[ لوحة المطور ]", reply_markup=get_main_dev_markup())

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_messages))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Taif is running with YouTube downloader...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
