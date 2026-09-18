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

# قواعد البيانات المؤقتة والنظام الشامل
all_users = set()
active_groups = set()
custom_replies = {"صباح الخير": "صباح النور"} 
command_aliases = {"اا": "افتاري", "اة": "افاتاري"} 
user_balances = {} 
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
    "لو رجع فيك الزمن لوراء، وش الشي اللي بتغيره؟"
]

games_list = [
    "اعلام", "معاني", "تخمين", "احكام", "ارقام", "احسب", "خواتم", 
    "انجليزي", "ترتيب", "انمي", "تركيب", "تفكيك", "عواصم", "روليت", 
    "سيارات", "ايموجي", "حجره", "ديمون", "جمل", "كلمات", "دين", "عربي", "اكمل", "صور"
]

async def get_user_rank(update: Update, user_id: int) -> str:
    if user_id == DEV_ID:
        return "مطور أساسي 👑"
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        try:
            member = await chat.get_member(user_id)
            if member.status == "creator":
                return "منشئ القروب"
            elif member.status == "administrator":
                return "مشرف"
        except Exception:
            pass
    return "عضو"

# --- لوحات الأزرار الشفافة ---
def get_main_menu_markup():
    keyboard = [
        [InlineKeyboardButton("م1 (الأوامر العامة)", callback_data="menu_m1"), InlineKeyboardButton("م2 (الإدارة والحماية)", callback_data="menu_m2")],
        [InlineKeyboardButton("م3 (التفعيل والتعطيل)", callback_data="menu_m3")],
        [InlineKeyboardButton("أوامر الرفع والمسح", callback_data="menu_ranks_clear"), InlineKeyboardButton("البنك والأموال", callback_data="menu_bank")],
        [InlineKeyboardButton("الألعاب والتفاعل", callback_data="menu_games"), InlineKeyboardButton("اليوتيوب والتحميل", callback_data="menu_youtube")],
        [InlineKeyboardButton("قفل وفتح", callback_data="menu_locks"), InlineKeyboardButton("قناة المطور", url="https://t.me/TV_1M")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_markup():
    keyboard = [[InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="menu_back")]]
    return InlineKeyboardMarkup(keyboard)

def get_developer_panel_markup():
    keyboard = [
        [InlineKeyboardButton("📊 إحصائيات البوت", callback_data="dev_stats")],
        [InlineKeyboardButton("📢 طريقة الإذاعة", callback_data="dev_broadcast_info")],
        [InlineKeyboardButton("قناة المطور الأساسية", url="https://t.me/TV_1M")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_dev_back_markup():
    keyboard = [[InlineKeyboardButton("رجوع لوحة المطور", callback_data="dev_back_main")]]
    return InlineKeyboardMarkup(keyboard)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    bot_username = context.bot.username
    user_id = user.id if user else 0

    if user:
        all_users.add(user_id)

    if chat.type == "private" and user_id == DEV_ID:
        text = (
            "أهلاً بك يا أسامة (المطور الأساسي) 🛠️✨\n\n"
            "- تم التعرف عليك بصفتك مطور البوت.\n"
            "- إليك لوحة التحكم الشفافة الخاصة بالمطور أدناه:"
        )
        await update.message.reply_text(text, reply_markup=get_developer_panel_markup())
        return

    if chat.type == "private":
        text = (
            "اهلين انا طيف\n\n"
            "- اختصاصي ادارة المجموعات والحماية والألعاب والبانك...\n"
            "- اضغط الزر أدناه لإضافتي لمجموعتك."
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ضِفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=true")]
        ])
        await update.message.reply_text(text, reply_markup=markup)
        return

    text = (
        "اهلين فيك باوامر البوت (طيف)\n\n"
        "للإستفسار - @TV_1M\n\n"
        "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:"
    )
    await update.message.reply_text(text, reply_markup=get_main_menu_markup())

# معالجة الأزرار الشفافة
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data == "dev_stats":
        if user_id != DEV_ID:
            await query.answer("هذه اللوحة خاصة بالمطور فقط!", show_alert=True)
            return
        stats_text = (
            "📊 [ لوحة إحصائيات البوت ]\n\n"
            f"- عدد المستخدمين بالخاص: {len(all_users)}\n"
            f"- عدد المجموعات: {len(active_groups)}\n"
            "- حالة البوت: يعمل بكفاءة 🟢"
        )
        await query.edit_message_text(stats_text, reply_markup=get_dev_back_markup())
        
    elif data == "dev_broadcast_info":
        if user_id != DEV_ID:
            return
        bc_text = (
            "📢 [ نظام الإذاعة للمطور ]\n\n"
            "لإرسال رسالة لكل المجموعات، اكتب في الخاص:\n"
            "إذاعة [النص الخاص بك]"
        )
        await query.edit_message_text(bc_text, reply_markup=get_dev_back_markup())
        
    elif data == "dev_back_main":
        if user_id != DEV_ID:
            return
        text = (
            "أهلاً بك يا أسامة (المطور الأساسي) 🛠️✨\n\n"
            "- تم التعرف عليك بصفتك مطور البوت.\n"
            "- إليك لوحة التحكم الشفافة الخاصة بالمطور أدناه:"
        )
        await query.edit_message_text(text, reply_markup=get_developer_panel_markup())

    elif data == "menu_m1":
        text = (
            "[ قسم الأوامر العامة - م1 ]\n\n"
            "- ايدي / معلوماتي / رتبتي\n"
            "- الرابط / بايو / الانشاء\n"
            "- افتاري أو (اا)"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_m2":
        text = (
            "[ قسم الإدارة والحماية - م2 ]\n\n"
            "- حظر / طرد / كتم / تقييد (بالرد أو الآيدي)\n"
            "- الغاء الحظر / الغاء الكتم / رفع القيود\n"
            "- منع الكلمة / الغاء منع الكلمة\n"
            "- طرد البوتات / كشف البوتات"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_m3":
        text = (
            "[ قسم التفعيل والتعطيل - م3 ]\n\n"
            "- تفعيل / تعطيل (الترحيب، الردود، الايدي، الرابط، الحماية، المنشن، التحقق)\n"
            "- تعيين الترحيب / تعيين القوانين\n"
            "- تغيير رتبه / تغيير امر"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())

    elif data == "menu_ranks_clear":
        text = (
            "[ أوامر الرفع والمسح الشاملة ]\n\n"
            "⭐ [ أوامر الرفع والتنزيل ]:\n"
            "- رفع مشرف / تنزيل مشرف\n"
            "- رفع مالك اساسي / تنزيل مالك اساسي\n"
            "- رفع مالك / تنزيل مالك\n"
            "- رفع مدير / تنزيل مدير\n"
            "- رفع ادمين / تنزيل ادمين\n"
            "- رفع مميز / تنزيل مميز\n"
            "- تنزيل الكل (بالرد أو بدون رد لتنزيل كل رتب المجموعة)\n\n"
            "🗑️ [ أوامر المسح ]:\n"
            "- مسح المالكين / المدراء / الادمنيه / المميزين\n"
            "- مسح المحظورين / المكتومين / قائمة المنع\n"
            "- مسح رتبه / مسح الرتب / مسح الردود / مسح الاوامر\n"
            "- مسح + العدد / مسح بالرد / مسح الترحيب / مسح قائمة التثبيت"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_games":
        text = (
            "[ قسم الألعاب والتفاعل ]\n\n"
            "- كت تويت، صراحة\n"
            "- الألعاب: (اعلام، معاني، تخمين، احكام، ارقام، احسب، خواتم، انجليزي، ترتيب، انمي، تركيب، تفكيك، عواصم، روليت، سيارات، ايموجي، حجره، ديمون، جمل، كلمات، دين، عربي، اكمل، صور)"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())

    elif data == "menu_bank":
        text = (
            "[ قسم أوامر البنك والأموال ]\n\n"
            "- انشاء حساب بنكي / مسح حساب بنكي\n"
            "- تحويل / حسابي / فلوسي\n"
            "- راتب (كل 20 دقيقة)\n"
            "- بخيش / زرف (كل 10 دقائق)\n"
            "- استثمار / حظ / مضاربه\n"
            "- توب الفلوس / توب الحراميه"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_youtube":
        text = "[ قسم يوتيوب والتحميل ]\n\n- بحث [اسم الأغنية]\n- وش يقول؟ (بالرد على فويس)"
        await query.edit_message_text(text, reply_markup=get_back_markup())

    elif data == "menu_locks":
        text = (
            "[ أوامر القفل والفتح والمسح ]\n\n"
            "- قفل / فتح (التعديل، الفويس، الفيديو، الصور، الملصقات، الدخول، الرابط، الهشتاج، البوتات، اليوزرات، الاشعارات، الكلام الكثير، التكرار، التوجيه، الانلاين، الجهات، الكلم، السب، الاضافه، الصوت، القنوات)"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())
        
    elif data == "menu_back":
        text = (
            "اهلين فيك باوامر البوت (طيف)\n\n"
            "للإستفسار - @TV_1M\n\n"
            "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:"
        )
        await query.edit_message_text(text, reply_markup=get_main_menu_markup())

# معالجة الرسائل
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
    if chat.type in ["group", "supergroup"]:
        active_groups.add(chat.id)

    if chat.type == "private":
        if user_id == DEV_ID:
            if text == "احصائيات البوت":
                await message.reply_text(f"📊 إحصائيات البوت:\n- المستخدمين: {len(all_users)}\n- المجموعات: {len(active_groups)}")
                return
            elif text.startswith("إذاعة "):
                broadcast_text = text.replace("إذاعة ", "", 1)
                sent_count = 0
                for g_id in active_groups:
                    try:
                        await context.bot.send_message(chat_id=g_id, text=f"📢 [إذاعة من المطور]\n\n{broadcast_text}")
                        sent_count += 1
                    except Exception:
                        pass
                await message.reply_text(f"تم إرسال الإذاعة إلى {sent_count} مجموعة.")
                return
        return

    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.id == context.bot.id:
                continue
            try:
                await message.reply_text(f"أهلاً بك ياعسل\nنورت القروب: {member.full_name}")
            except Exception:
                pass
        return

    # الأوامر البنكية
    if text == "انشاء حساب بنكي":
        if user_id in user_balances:
            await message.reply_text("لديك حساب بنكي بالفعل!")
        else:
            user_balances[user_id] = 1000
            await message.reply_text("تم إنشاء حسابك البنكي بنجاح وإيداع 1000 عملة! 💳")
        return

    if text in ["فلوسي", "حسابي"]:
        balance = user_balances.get(user_id, 0)
        await message.reply_text(f"رصيدك الحالي: {balance} عملة 💰\nرقم حسابك: `ACC-{user_id}`", parse_mode="Markdown")
        return

    if text == "راتب":
        if user_id not in user_balances:
            user_balances[user_id] = 0
        user_balances[user_id] += 500
        await message.reply_text("تم صرف راتبك بنجاح! +500 عملة 💵")
        return

    if text in command_aliases:
        text = command_aliases[text]
    if text in custom_replies:
        await message.reply_text(custom_replies[text])
        return

    if text in ["كت تويت", "كت"]:
        await message.reply_text(f"[ كت تويت ]\n\n{random.choice(ktweet_list)}")
        return

    if text == "صراحة":
        await message.reply_text(f"[ سؤال صراحة ]\n\n{random.choice(sara7a_list)}")
        return

    if text in games_list:
        await message.reply_text(f"🎮 لعبة ({text}) بدأت!\nالسؤال أو التحدي قيد التشغيل...")
        return

    if text in ["الاوامر", "الأوامر"]:
        await message.reply_text(
            "اهلين فيك باوامر البوت (طيف)\n\n"
            "للإستفسار - @TV_1M\n\n"
            "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:",
            reply_markup=get_main_menu_markup()
        )
        return

    if text in ["افاتاري", "افتاري"]:
        photos = await user.get_profile_photos(limit=100)
        total_photos = photos.total_count
        caption_text = f"اسمك: {user.full_name}\nمعرفك: @{user.username if user.username else 'لا يوجد'}\nعدد أفتاراتك: {total_photos}"
        if total_photos > 0:
            await message.reply_photo(photo=photos.photos[0][0].file_id, caption=caption_text)
        else:
            await message.reply_text(caption_text)
        return

    if text in ["ايدي", "معلوماتي", "رتبتي"]:
        user_rank = await get_user_rank(update, user_id)
        photos = await user.get_profile_photos(limit=1)
        info = f"الاسم: {user.full_name}\nالمعرف: @{user.username if user.username else 'لا يوجد'}\nالرتبة: {user_rank}\nالآيدي: {user_id}"
        if photos.total_count > 0:
            await message.reply_photo(photo=photos.photos[0][0].file_id, caption=info)
        else:
            await message.reply_text(info)
        return

    if text.startswith("بحث "):
        query_song = text.replace("بحث ", "", 1).strip()
        if not query_song:
            await message.reply_text("يرجى كتابة اسم الأغنية بعد بحث.")
            return
        processing_msg = await message.reply_text(f"جاري التحميل: {query_song}...")
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
                pass
        return

    if text == "بايو":
        await message.reply_text("البايو الخاص بك:\nI don't chase, i attracts")
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

    print("Bot Taif is running with all lists, ranks, and clear commands...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
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
all_users = set()
active_groups = set()
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
    "لو رجع فيك الزمن لوراء، وش الشي اللي بتغيره؟"
]

async def get_user_rank(update: Update, user_id: int) -> str:
    if user_id == DEV_ID:
        return "مطور أساسي 👑"
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        try:
            member = await chat.get_member(user_id)
            if member.status == "creator":
                return "منشئ القروب"
            elif member.status == "administrator":
                return "مشرف"
        except Exception:
            pass
    return "عضو"

# --- لوحات الأزرار الشفافة ---
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

# لوحة المطور بالأزرار الشفافة بالكامل
def get_developer_panel_markup():
    keyboard = [
        [InlineKeyboardButton("📊 إحصائيات البوت", callback_data="dev_stats")],
        [InlineKeyboardButton("📢 طريقة الإذاعة", callback_data="dev_broadcast_info")],
        [InlineKeyboardButton("قناة المطور الأساسية", url="https://t.me/TV_1M")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_dev_back_markup():
    keyboard = [[InlineKeyboardButton("رجوع لوحة المطور", callback_data="dev_back_main")]]
    return InlineKeyboardMarkup(keyboard)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    bot_username = context.bot.username
    user_id = user.id if user else 0

    if user:
        all_users.add(user_id)

    # لوحة المطور الشفافة الخاصة بك في الخاص
    if chat.type == "private" and user_id == DEV_ID:
        text = (
            "أهلاً بك يا أسامة (المطور الأساسي) 🛠️✨\n\n"
            "- تم التعرف عليك بصفتك مطور البوت.\n"
            "- إليك لوحة التحكم الشفافة الخاصة بالمطور أدناه:"
        )
        await update.message.reply_text(text, reply_markup=get_developer_panel_markup())
        return

    # الأعضاء العاديين في الخاص
    if chat.type == "private":
        text = (
            "اهلين انا طيف\n\n"
            "- اختصاصي ادارة المجموعات من السبام واللخ...\n"
            "- كت تويت, يوتيوب, ساوند , واشياء كثير.."
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ضِفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=true")]
        ])
        await update.message.reply_text(text, reply_markup=markup)
        return

    # في المجموعات
    text = (
        "اهلين فيك باوامر البوت (طيف)\n\n"
        "للإستفسار - @TV_1M\n\n"
        "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:"
    )
    await update.message.reply_text(text, reply_markup=get_main_menu_markup())

# معالجة الأزرار الشفافة
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    # أقسام المطور (أزرار شفافة بالكامل)
    if data == "dev_stats":
        if user_id != DEV_ID:
            await query.answer("هذه اللوحة خاصة بالمطور فقط!", show_alert=True)
            return
        stats_text = (
            "📊 [ لوحة إحصائيات البوت ]\n\n"
            f"- عدد المستخدمين المسجلين بالخاص: {len(all_users)}\n"
            f"- عدد المجموعات المتفاعل بها: {len(active_groups)}\n"
            "- حالة البوت: يعمل بكفاءة 🟢"
        )
        await query.edit_message_text(stats_text, reply_markup=get_dev_back_markup())
        
    elif data == "dev_broadcast_info":
        if user_id != DEV_ID:
            return
        bc_text = (
            "📢 [ نظام الإذاعة للمطور ]\n\n"
            "لإرسال رسالة لجميع المجموعات، اكتب في الخاص:\n"
            "إذاعة [النص الخاص بك]\n\n"
            "مثال:\n"
            "إذاعة السلام عليكم يا شباب"
        )
        await query.edit_message_text(bc_text, reply_markup=get_dev_back_markup())
        
    elif data == "dev_back_main":
        if user_id != DEV_ID:
            return
        text = (
            "أهلاً بك يا أسامة (المطور الأساسي) 🛠️✨\n\n"
            "- تم التعرف عليك بصفتك مطور البوت.\n"
            "- إليك لوحة التحكم الشفافة الخاصة بالمطور أدناه:"
        )
        await query.edit_message_text(text, reply_markup=get_developer_panel_markup())

    # الأقسام العامة للأوامر
    elif data == "menu_m1":
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
    if chat.type in ["group", "supergroup"]:
        active_groups.add(chat.id)

    # أوامر المطور في الخاص
    if chat.type == "private":
        if user_id == DEV_ID:
            if text == "احصائيات البوت":
                await message.reply_text(f"📊 إحصائيات البوت:\n- عدد المستخدمين: {len(all_users)}\n- عدد المجموعات: {len(active_groups)}")
                return
            elif text.startswith("إذاعة "):
                broadcast_text = text.replace("إذاعة ", "", 1)
                sent_count = 0
                for g_id in active_groups:
                    try:
                        await context.bot.send_message(chat_id=g_id, text=f"📢 [إذاعة من المطور]\n\n{broadcast_text}")
                        sent_count += 1
                    except Exception:
                        pass
                await message.reply_text(f"تم إرسال الإذاعة إلى {sent_count} مجموعة بنجاح.")
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

    # المنشن الجماعي
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
            pass
        return

    if text in command_aliases:
        text = command_aliases[text]
    if text in custom_replies:
        await message.reply_text(custom_replies[text])
        return

    if "http://" in text or "https://" in text or "t.me/" in text:
        try:
            member = await chat.get_member(user_id)
            if member.status not in ["creator", "administrator"] and user_id != DEV_ID:
                await message.delete()
                return
        except Exception:
            pass

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        try:
            exec_member = await chat.get_member(user_id)
            is_admin = (exec_member.status in ["creator", "administrator"] or user_id == DEV_ID)
            if is_admin:
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
                elif text in ["فك كتم", "فك الكتم"]:
                    await chat.restrict_member(target.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True))
                    await message.reply_text(f"تم إفك الكتم عن: {target.full_name}")
                    return
        except Exception:
            pass

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
            pass
        return

    if text in ["طيف", "بوت"]:
        await message.reply_text(random.choice(["عيوني", "لبيه", "ها؟", "أمزح معك"]))
        return

    if text == "كت":
        await message.reply_text(f"[ كت تويت ]\n\n{random.choice(ktweet_list)}")
        return

    if text == "صراحة":
        await message.reply_text(f"[ سؤال صراحة ]\n\n{random.choice(sara7a_list)}")
        return

    if text in ["الاوامر", "الأوامر"]:
        await message.reply_text(
            "اهلين فيك باوامر البوت (طيف)\n\n"
            "للإستفسار - @TV_1M\n\n"
            "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:",
            reply_markup=get_main_menu_markup()
        )
        return

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

    if text in ["ايدي", "معلوماتي", "رتبتي"]:
        user_rank = await get_user_rank(update, user_id)
        photos = await user.get_profile_photos(limit=1)
        info = (
            f"الاسم: {user.full_name}\n"
            f"المعرف: @{user.username if user.username else 'لا يوجد'}\n"
            f"الرتبة: {user_rank}\n"
            f"الآيدي: {user_id}\n"
            f"تاريخ التسجيل: 2023/07"
        )
        if photos.total_count > 0:
            await message.reply_photo(photo=photos.photos[0][0].file_id, caption=info)
        else:
            await message.reply_text(info)
        return

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
                pass
        return

    if text == "بايو":
        await message.reply_text("البايو الخاص بك:\nI don't chase, i attracts")
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

    print("Bot Taif is running with transparent buttons...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
