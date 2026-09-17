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
active_groups = set() # المجموعات المفعلة
all_users = set()     # المستخدمين بالخاص
custom_replies = {"صباح الخير": "صباح النور"} # الردود المخصصة
command_aliases = {"اا": "افتاري", "اة": "افاتاري"} # اختصارات الأوامر (يمكن تعديلها أو إضافتها)
banned_words = set()

# قوائم الألعاب والتفاعل
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

# دالة تحديد الرتبة الاحترافية
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

# --- لوحات الأزرار الشفافة ---
def get_main_menu_markup():
    keyboard = [
        [InlineKeyboardButton("م1 (الأوامر العامة)", callback_data="menu_m1"), InlineKeyboardButton("م2 (الإدارة والحماية)", callback_data="menu_m2")],
        [InlineKeyboardButton("م3 (الأعضاء والرفاهية)", callback_data="menu_m3")],
        [InlineKeyboardButton("الألعاب والتفاعل", callback_data="menu_games"), InlineKeyboardButton("البنك", callback_data="menu_bank")],
        [InlineKeyboardButton("اليوتيوب والتحميل", callback_data="menu_youtube")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_markup():
    keyboard = [[InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="menu_back")]]
    return InlineKeyboardMarkup(keyboard)

def get_start_private_markup(bot_username: str):
    keyboard = [[InlineKeyboardButton("ضِفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=true")]]
    return InlineKeyboardMarkup(keyboard)

def get_dev_markup():
    keyboard = [[InlineKeyboardButton("لوحة المطور : @TV_1M", url="https://t.me/TV_1M")]]
    return InlineKeyboardMarkup(keyboard)

# أمر /start الخاص
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    bot_username = context.bot.username

    if user:
        all_users.add(user.id)

    if chat.type == "private":
        text = (
            "اهلين انا طيف\n\n"
            "- اختصاصي ادارة المجموعات من السبام واللخ...\n"
            "- كت تويت, يوتيوب, ساوند , واشياء كثير..\n"
            "- عشان تفعلني ارفعني اشراف وارسل تفعيل."
        )
        await update.message.reply_text(text, reply_markup=get_start_private_markup(bot_username))
        return

    text = (
        "اهلين فيك باوامر البوت\n\n"
        "للإستفسار - @TV_1M\n\n"
        "اكتب ( الاوامر ) لعرض قائمة الأوامر الكاملة."
    )
    
    if user.id == DEV_ID:
        await update.message.reply_text(text + "\n\n[ لوحة المطور ]", reply_markup=get_dev_markup())
    else:
        await update.message.reply_text(text, reply_markup=get_main_menu_markup())

# معالجة الأزرار الشفافة
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_m1":
        text = (
            "[ قسم الأوامر العامة - م1 ]\n\n"
            "- ايدي / معلوماتي: لعرض معلوماتك ورتبتك.\n"
            "- الرابط: لجلب رابط القروب.\n"
            "- بايو / بايو عشوائي: لعرض البايو.\n"
            "- الانشاء: تاريخ إنشاء الحساب.\n"
            "- افتاري (أو الاختصار اا): لعرض صورتك وعدد أفتاراتك."
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_m2":
        text = (
            "[ قسم الإدارة والحماية - م2 ]\n\n"
            "- تفعيل / إلغاء تفعيل (لعمل البوت بالقروب)\n"
            "- اضافة امر [الكلمة] [الرد] (لإضافة رد مخصص)\n"
            "- اضافة اختصار [الاختصار] [الأمر الأصلي] (لاختصار الأوامر مثل اا لـ افتاري)\n"
            "- حذف امر [الكلمة] / حذف اختصار [الاختصار]\n"
            "- بالرد (حظر / طرد / كتم / تقييد / فك كتم)\n"
            "- تثبيت / إلغاء التثبيت بالرد\n"
            "- رد بـ (منع) لحظر الكلمة ومسح الرسائل."
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
        
    elif data == "menu_bank":
        text = "[ قسم البنك والفلوس ]\n\nنظام الحسابات والبنك قيد التطوير لتجميع الأرباح."
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_youtube":
        text = "[ قسم يوتيوب والتحميل ]\n\nاكتب مباشرة في الشات:\nبحث [اسم الأغنية] لتحميلها صوتياً."
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_back":
        text = "اهلين فيك باوامر البوت\n\nللإستفسار - @TV_1M\n\nاختر القسم المناسب:"
        await query.edit_message_text(text, reply_markup=get_main_menu_markup())

# معالج الرسائل والأوامر
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

    if chat.type == "private":
        if user_id == DEV_ID:
            if text == "احصائيات البوت":
                await message.reply_text(f"احصائيات البوت:\n- عدد المجموعات المفعلة: {len(active_groups)}\n- عدد المستخدمين بالخاص: {len(all_users)}")
                return
            elif text.startswith("إذاعة "):
                broadcast_text = text.replace("إذاعة ", "", 1)
                sent_count = 0
                for g_id in active_groups:
                    try:
                        await context.bot.send_message(chat_id=g_id, text=f"[إذاعة من المطور]\n\n{broadcast_text}")
                        sent_count += 1
                    except Exception:
                        pass
                await message.reply_text(f"تم إرسال الإذاعة إلى {sent_count} مجموعة بنجاح.")
                return
        return

    # الترحيب
    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.id == context.bot.id:
                continue
            if chat.id in active_groups:
                try:
                    await message.reply_text(f"أهلاً بك ياعسل\nنورت القروب: {member.full_name}")
                except Exception:
                    pass
        return

    # تفعيل وإلغاء تفعيل البوت
    if text == "تفعيل":
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                active_groups.add(chat.id)
                await message.reply_text("تم تفعيل البوت في هذه المجموعة بنجاح.")
            else:
                await message.reply_text("هذا الأمر للمشرفين فقط.")
        except Exception:
            pass
        return

    if text == "إلغاء تفعيل":
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                if chat.id in active_groups:
                    active_groups.remove(chat.id)
                await message.reply_text("تم إلغاء تفعيل البوت في هذه المجموعة.")
        except Exception:
            pass
        return

    if chat.id not in active_groups and text not in ["الاوامر", "الأوامر", "اوامر"]:
        return

    # --- نظام إضافة أو تعديل أمر مخصص ---
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
                await message.reply_text("هذا الأمر للمشرفين والمطور فقط.")
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

    # --- نظام إضافة اختصارات الأوامر (مثل: اا لـ افتاري) ---
    if text.startswith("اضافة اختصار "):
        try:
            member = await chat.get_member(user_id)
            if member.status in ["creator", "administrator"] or user_id == DEV_ID:
                parts = text.replace("اضافة اختصار ", "", 1).split(" ", 1)
                if len(parts) == 2:
                    short_cmd, orig_cmd = parts[0].strip(), parts[1].strip()
                    command_aliases[short_cmd] = orig_cmd
                    await message.reply_text(f"تم إضافة الاختصار ({short_cmd}) للأمر ({orig_cmd}) بنجاح.")
                else:
                    await message.reply_text("الصيغة:\nاضافة اختصار [الاختصار] [الأمر الأصلي]\nمثال: اضافة اختصار اا افتاري")
            else:
                await message.reply_text("للمشرفين والمطور فقط.")
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
                    await message.reply_text(f"تم حذف الاختصار ({short_cmd}) بنجاح.")
                else:
                    await message.reply_text("الاختصار غير موجود.")
            else:
                await message.reply_text("للمشرفين فقط.")
        except Exception:
            pass
        return

    # تحويل الاختصار إلى الأمر الأصلي تلقائياً
    if text in command_aliases:
        text = command_aliases[text]

    # فحص الردود المخصصة
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
            await message.reply_text("عذراً، لا أملك صلاحية تثبيت الرسائل.")
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
            await message.reply_text("عذراً، لا أملك صلاحية كافية أو العضو مشرف.")
            return

    # التفاعل والمناداة
    if text in ["طيف", "بوت"]:
        await message.reply_text(random.choice(["عيوني", "لبيه", "ها؟", "أمزح معك"]))
        return

    # الألعاب والاختصارات
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

    # قائمة الأوامر
    if text in ["الاوامر", "الأوامر", "اوامر"]:
        full_text = (
            "اهلين فيك باوامر البوت\n\n"
            "للإستفسار - @TV_1M\n\n"
            "( الأوامر العامة والأخرى )\n"
            "- تفعيل / إلغاء تفعيل\n"
            "- اضافة امر [الكلمة] [الرد]\n"
            "- اضافة اختصار [الاختصار] [الأمر الأصلي] (مثل: اضافة اختصار اا افتاري)\n"
            "- الرابط / بايو / ايدي / الانشاء\n\n"
            "( الألعاب والتفاعل )\n"
            "- كت | صراحة | سؤالي | عواصم\n\n"
            "( اوامر التحميل والترفيه )\n"
            "- بحث [اسم الأغنية] (لتحميل الصوت)\n\n"
            "( اوامر الإدارة والحماية )\n"
            "- تثبيت / إلغاء التثبيت (بالرد)\n"
            "- رد بـ ( منع ) لحظر رسالة\n"
            "- رد بـ ( مسح / حذف ) لحذف رسالة\n"
            "- حظر / طرد / كتم / تقييد [دقائق] (بالرد)"
        )
        if user_id == DEV_ID:
            await message.reply_text(full_text + "\n\n[ لوحة المطور ]", reply_markup=get_dev_markup())
        else:
            await message.reply_text(full_text, reply_markup=get_main_menu_markup())
        return

    # أمر افاتاري / افتاري
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

    # أمر ايدي
    if text in ["ايدي", "معلوماتي"]:
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

    print("Bot Taif is running with custom command aliases...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main"></main>
