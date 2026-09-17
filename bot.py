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

# تفعيل السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# الآيدي الخاص بك كمطور أساسي
DEV_ID = 6652826141 

# قواعد البيانات المؤقتة
all_users = set()     # المستخدمين في الخاص
custom_replies = {"صباح الخير": "صباح النور"} 
command_aliases = {"اا": "افتاري", "اة": "افاتاري"} 
banned_words = set()

ktweet_list = [
    "موقف مستحيل تنساه بحياتك؟",
    "لو خيروك بين العيش لوحدك أو مع شخص مزعج طوال العمر؟",
    "كلمة تقولها لشخص غيّر حياتك للأفضل؟",
    "أكثر صفه تكرهها بالناس؟",
    "شيء تسويه إذا طفشت؟"
]

sara7a_list = [
    "هل جربت شعور الخيانة من شخص غالي؟",
    "متى آخر مرة بكيت وليه؟",
    "هل تخفي أسرار عن أقرب الناس لك؟",
    "لو رجع فيك الزمن لوراء، وش الشي اللي بتغيره؟",
    "هل تشوف نفسك شخص عادل بالحكم على الآخرين؟"
]

islamic_questions = [
    "من هو الصحابي الذي لقب بـ (سيف الله المسلول)؟ (خالد بن الوليد)",
    "كم عدد السور المدنية في القرآن الكريم؟ (28 سورة)",
    "ما هي السورة التي تسمى بروح القرآن؟ (سورة يس)",
    "من هو النبي الذي ألقي في النار فجعلها الله برداً وسلاماً؟ (إبراهيم عليه السلام)"
]

capital_games = [
    "ما هي عاصمة دولة فرنسا؟ (باريس)",
    "ما هي عاصمة دولة اليابان؟ (طوكيو)",
    "ما هي عاصمة المملكة العربية السعودية؟ (الرياض)",
    "ما هي عاصمة دولة مصر؟ (القاهرة)",
    "ما هي عاصمة دولة الإمارات؟ (أبوظبي)"
]

random_bios = [
    "I don't chase, i attracts",
    "عيش وحدك، فالكثير قليل",
    "الهدوء عنوان الفخامة.",
    "فقط استمر في المضي قدماً",
    "كن قليل الكلام كثير الصمت."
]

async def get_user_rank(update: Update, user_id: int) -> str:
    if user_id == DEV_ID:
        return "مطور أساسي"
    
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        try:
            member = await chat.get_member(user_id)
            if member.status == "creator":
                return "منشئ القروب"
            elif member.status == "administrator":
                return "مدير / مشرف"
        except Exception:
            pass
            
    return "عضو مميز"

# --- لوحات أزرار بوت وعد الشفافة ---
def get_main_menu_markup():
    keyboard = [
        [InlineKeyboardButton("م1 (الأوامر العامة)", callback_data="menu_m1"), InlineKeyboardButton("م2 (الإدارة والحماية)", callback_data="menu_m2")],
        [InlineKeyboardButton("م3 (الأعضاء والرفاهية)", callback_data="menu_m3")],
        [InlineKeyboardButton("الألعاب والتفاعل", callback_data="menu_games"), InlineKeyboardButton("اليوتيوب والتحميل", callback_data="menu_youtube")],
        [InlineKeyboardButton("قناة المطور", url="https://t.me/TV_1M")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_markup():
    keyboard = [[InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="menu_back")]]
    return InlineKeyboardMarkup(keyboard)

def get_start_private_markup(bot_username: str, is_dev: bool = False):
    keyboard = [
        [InlineKeyboardButton("ضِفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=true")]
    ]
    if is_dev:
        keyboard.append([InlineKeyboardButton("لوحة المطور : @TV_1M", url="https://t.me/TV_1M")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    bot_username = context.bot.username
    user_id = user.id if user else 0

    if user:
        all_users.add(user_id)

    if chat.type == "private":
        text = (
            "اهلين انا طيف\n\n"
            "- اختصاصي ادارة المجموعات من السبام واللخ...\n"
            "- كت تويت, يوتيوب, ساوند , واشياء كثير..\n"
            "- اشتغل على طول بدون تعقيد!"
        )
        is_developer = (user_id == DEV_ID)
        await update.message.reply_text(text, reply_markup=get_start_private_markup(bot_username, is_dev=is_developer))
        return

    # في المجموعات، يرسل لوحة الأوامر الشفافة فوراً
    text = (
        "اهلين فيك باوامر البوت (طيف)\n\n"
        "للإستفسار - @TV_1M\n\n"
        "اختر القسم المطلوب من الأزرار بالأسفل:"
    )
    await update.message.reply_text(text, reply_markup=get_main_menu_markup())

# معالجة الأزرار الشفافة
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_m1":
        text = (
            "[ قسم الأوامر العامة - م1 ]\n\n"
            "- ايدي / معلوماتي / رتبتي: لعرض معلوماتك ورتبتك.\n"
            "- الرابط: لجلب رابط القروب.\n"
            "- بايو / بايو عشوائي: لعرض البايو.\n"
            "- الانشاء: تاريخ إنشاء الحساب.\n"
            "- افتاري أو (اا): لعرض صورتك وعدد أفتاراتك."
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_m2":
        text = (
            "[ قسم الإدارة والحماية - م2 ]\n\n"
            "- منشن / @all / تنزيل (لعمل منشن جماعي)\n"
            "- اضافة امر [الكلمة] [الرد] (لإضافة رد مخصص)\n"
            "- اضافة اختصار [الاختصار] [الأمر الأصلي]\n"
            "- بالرد (حظر / طرد / كتم / تقييد / فك كتم)\n"
            "- تثبيت / إلغاء التثبيت ومسح الرسائل."
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_m3":
        text = (
            "[ قسم الأعضاء والرفاهية - م3 ]\n\n"
            "- مناداة البوت بكلمة (طيف) أو (بوت)\n"
            "- الترحيب التلقائي بالأعضاء الجدد."
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_games":
        text = (
            "[ قسم الألعاب والتفاعل ]\n\n"
            "- كت: سؤال كت تويت عشوائي.\n"
            "- صراحة: سؤال صراحة عشوائي.\n"
            "- سؤالي: سؤال إسلامي وثقافي.\n"
            "- عواصم: لعبة تخمين العواصم العالمية."
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_youtube":
        text = "[ قسم يوتيوب والتحميل ]\n\nاكتب مباشرة في الشات:\nبحث [اسم الأغنية] لتحميلها صوتياً."
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_back":
        text = (
            "اهلين فيك باوامر البوت (طيف)\n\n"
            "للإستفسار - @TV_1M\n\n"
            "اختر القسم المطلوب من الأزرار بالأسفل:"
        )
        await query.edit_message_text(text, reply_markup=get_main_menu_markup())

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    user_id = user.id if user else 0
    text = message.text or message.caption or ""

    if user:
        all_users.add(user_id)

    # أوامر المطور في الخاص
    if chat.type == "private":
        if user_id == DEV_ID:
            if text == "احصائيات البوت":
                active_count = 1  # افتراضي
                await message.reply_text(f"احصائيات البوت:\n- عدد المستخدمين بالخاص: {len(all_users)}")
                return
            elif text.startswith("إذاعة "):
                broadcast_text = text.replace("إذاعة ", "", 1)
                await message.reply_text(f"تم استقبال الإذاعة بنجاح.")
                return
        return

    # الترحيب بالأعضاء الجدد
    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.id == context.bot.id:
                continue
            try:
                await message.reply_text(f"أهلاً بك ياعسل\nنورت القروب: {member.full_name}")
            except Exception:
                pass
        return

    # --- المنشن الجماعي ---
    if text in ["منشن", "@all", "تنزيل"]:
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                sender_name = user.first_name if user.first_name else "عضو"
                sender_mention = f"[{sender_name}](tg://user?id={user_id})"
                output_text = f"وجـه\n\n{sender_mention} ، {user.full_name}"
                await message.reply_text(output_text, parse_mode="Markdown")
            else:
                await message.reply_text("أمر المنشن الجماعي للمشرفين فقط.")
        except Exception:
            await message.reply_text("عذراً، حدث خطأ أثناء تنفيذ المنشن.")
        return

    # --- إضافة أو حذف الأوامر المخصصة ---
    if text.startswith("اضافة امر "):
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                parts = text.replace("اضافة امر ", "", 1).split(" ", 1)
                if len(parts) == 2:
                    cmd_key, cmd_val = parts[0].strip(), parts[1].strip()
                    custom_replies[cmd_key] = cmd_val
                    await message.reply_text(f"تم إضافة/تعديل الأمر ({cmd_key}) بنجاح.")
                else:
                    await message.reply_text("الصيغة:\nاضافة امر [الكلمة] [الرد]")
            else:
                await message.reply_text("للمشرفين فقط.")
        except Exception:
            pass
        return

    if text.startswith("حذف امر "):
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                cmd_key = text.replace("حذف امر ", "", 1).strip()
                if cmd_key in custom_replies:
                    del custom_replies[cmd_key]
                    await message.reply_text(f"تم حذف الأمر ({cmd_key}) بنجاح.")
                else:
                    await message.reply_text("الأمر غير موجود.")
            else:
                await message.reply_text("للمشرفين فقط.")
        except Exception:
            pass
        return

    # --- إضافة واختصار الأوامر ---
    if text.startswith("اضافة اختصار "):
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                parts = text.replace("اضافة اختصار ", "", 1).split(" ", 1)
                if len(parts) == 2:
                    short_cmd, orig_cmd = parts[0].strip(), parts[1].strip()
                    command_aliases[short_cmd] = orig_cmd
                    await message.reply_text(f"تم إضافة الاختصار ({short_cmd}) للأمر ({orig_cmd}).")
                else:
                    await message.reply_text("الصيغة:\nاضافة اختصار [الاختصار] [الأمر الأصلي]")
            else:
                await message.reply_text("للمشرفين فقط.")
        except Exception:
            pass
        return

    if text.startswith("حذف اختصار "):
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                short_cmd = text.replace("حذف اختصار ", "", 1).strip()
                if short_cmd in command_aliases:
                    del command_aliases[short_cmd]
                    await message.reply_text(f"تم حذف الاختصار ({short_cmd}).")
                else:
                    await message.reply_text("الاختصار غير موجود.")
            else:
                await message.reply_text("للمشرفين فقط.")
        except Exception:
            pass
        return

    # تحويل الاختصار لأصله
    if text in command_aliases:
        text = command_aliases[text]

    if text in custom_replies:
        await message.reply_text(custom_replies[text])
        return

    # الحماية والمنع
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

    if text == "منع" and message.reply_to_message:
        replied = message.reply_to_message
        if replied.text:
            banned_words.add(replied.text)
            await message.reply_text("تم إضافة الكلمة لقائمة المنع.")
            return

    if text in ["مسح", "حذف"] and message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception:
            pass
        return

    if text == "تثبيت" and message.reply_to_message:
        try:
            await context.bot.pin_chat_message(chat_id=chat.id, message_id=message.reply_to_message.message_id)
            await message.reply_text("تم تثبيت الرسالة بنجاح.")
        except Exception:
            await message.reply_text("لا أملك صلاحية تثبيت الرسائل.")
        return

    if text == "إلغاء التثبيت" and message.reply_to_message:
        try:
            await context.bot.unpin_chat_message(chat_id=chat.id, message_id=message.reply_to_message.message_id)
            await message.reply_text("تم إلغاء تثبيت الرسالة.")
        except Exception:
            pass
        return

    # أوامر الإدارة بالرد
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        try:
            if text == "حظر":
                await chat.ban_member(target.id)
                await message.reply_text(f"تم حظر: {target.full_name}")
                return
            elif text == "طرد":
                await chat.ban_member(target.id)
                await chat.unban_member(target.id)
                await message.reply_text(f"تم طرد: {target.full_name}")
                return
            elif text == "كتم":
                await chat.restrict_member(target.id, permissions=ChatPermissions(can_send_messages=False))
                await message.reply_text(f"تم كتم: {target.full_name}")
                return
            elif text.startswith("تقييد "):
                parts = text.split()
                minutes = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
                await chat.restrict_member(target.id, permissions=ChatPermissions(can_send_messages=False))
                await message.reply_text(f"تم تقييد {target.full_name} لمدة {minutes} دقائق.")
                return
            elif text in ["فك كتم", "فك الكتم"]:
                await chat.restrict_member(target.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True))
                await message.reply_text(f"تم إزالة الكتم عن: {target.full_name}")
                return
        except Exception:
            await message.reply_text("لا أملك صلاحية كافية أو العضو مشرف.")
            return

    # التفاعل والمناداة
    if text in ["طيف", "بوت"]:
        await message.reply_text(random.choice(["عيوني", "لبيه", "ها؟", "أمزح معك"]))
        return

    # الألعاب والتفاعل
    if text == "كت":
        await message.reply_text(f"[ كت تويت ]\n\n{random.choice(ktweet_list)}")
        return

    if text == "صراحة":
        await message.reply_text(f"[ سؤال صراحة ]\n\n{random.choice(sara7a_list)}")
        return

    if text == "سؤالي":
        await message.reply_text(f"[ سؤال إسلامي وثقافي ]\n\n{random.choice(islamic_questions)}")
        return

    if text == "عواصم":
        await message.reply_text(f"[ لعبة العواصم ]\n\n{random.choice(capital_games)}")
        return

    # قائمة الأوامر بالأزرار
    if text in ["الاوامر", "الأوامر", "اوامر"]:
        await message.reply_text(
            "اهلين فيك باوامر البوت (طيف)\n\n"
            "للإستفسار - @TV_1M\n\n"
            "اختر القسم المطلوب من الأزرار بالأسفل:",
            reply_markup=get_main_menu_markup()
        )
        return

    # أمر افاتاري / افتاري (أو الاختصار اا)
    if text in ["افاتاري", "افتاري"]:
        photos = await user.get_profile_photos(limit=100)
        total_photos = photos.total_count
        caption_text = (
            f"اسمك: {user.full_name}\n"
            f"معرفك: @{user.username if user.username else 'لا يوجد'}\n"
            f"عدد صور أفتاراتك المسجلة: {total_photos}"
        )
        if total_photos > 0:
            await message.reply_photo(photo=photos.photos[0][0].file_id, caption=caption_text)
        else:
            await message.reply_text(f"ليس لديك صورة بروفايل.\n{caption_text}")
        return

    # أمر ايدي / معلوماتي / رتبتي
    if text in ["ايدي", "معلوماتي", "رتبتي"]:
        user_rank = await get_user_rank(update, user_id)
        photos = await user.get_profile_photos(limit=1)
        username_str = f"@{user.username}" if user.username else "@TV_1M"
        
        info = (
            f"الاسم: {user.full_name}\n"
            f"المعرف: {username_str}\n"
            f"الرتبة: {user_rank}\n"
            f"الآيدي: {user_id}\n"
            f"تاريخ التسجيل: 2023/07"
        )
        if photos.total_count > 0:
            await message.reply_photo(photo=photos.photos[0][0].file_id, caption=info)
        else:
            await message.reply_text(info)
        return

    # تحميل اليوتيوب
    if text.startswith("بحث "):
        query_song = text.replace("بحث ", "", 1).strip()
        if not query_song:
            await message.reply_text("يرجى كتابة اسم الأغنية بعد كلمة بحث.")
            return
            
        processing_msg = await message.reply_text(f"جاري البحث والتحميل للصوت: {query_song}...")
        file_path = f"audio_{user_id}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"audio_{user_id}.%(ext)s",
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'noplaylist': True,
            'quiet': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query_song}", download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                title = info.get('title', query_song)
            
            with open(file_path, 'rb') as audio_file:
                await message.reply_audio(audio=audio_file, caption=f"تم التحميل بنجاح: {title}")
            await processing_msg.delete()
        except Exception:
            await processing_msg.edit_text("عذراً، لم أتمكن من التحميل.")
            
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return

    if text == "الرابط":
        if chat.type in ["group", "supergroup"]:
            try:
                link = await chat.export_invite_link()
                await message.reply_text(f"رابط القروب:\n{link}")
            except Exception:
                await message.reply_text("لا أملك صلاحية جلب الرابط.")
        return

    if text == "بايو":
        await message.reply_text("البايو الخاص بك:\nI don't chase, i attracts")
        return

    if text == "بايو عشوائي":
        await message.reply_text(f"بايو مقترح:\n{random.choice(random_bios)}")
        return

    if text == "الانشاء":
        await message.reply_text("تاريخ الإنشاء المسجل: 2023/07")
        return

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_messages))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Taif is running instantly without activation...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
