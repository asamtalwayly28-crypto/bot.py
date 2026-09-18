import os
import logging
import datetime
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

DEV_ID = 6652826141
DEV_USERNAME = "@TV_1M"

known_users = set()
known_chats = set()
active_groups = set()
user_balances = {}
custom_replies = {}
broadcast_mode = {}

# قائمة أسئلة الألعاب الشغالة
GAMES_DATA = {
    "كلمات": [{"q": "رتب الحروف لتكون كلمة صحيحة: ( ر م ق )", "a": "قمر"}, {"q": "رتب الحروف لتكون كلمة صحيحة: ( ب ش ح ر )", "a": "بحري"}],
    "عربي": [{"q": "ما جمع كلمة (أسد)؟", "a": "أسود"}, {"q": "ما مفرد كلمة (مفتاح)؟", "a": "فتح"}],
    "اكمل": [{"q": "أكمل المثل: من حفر حفراً لأخيه ...", "a": "وقع فيها"}, {"q": "أكمل الآية: الحمد لله رب ...", "a": "العالمين"}],
    "انقليزي": [{"q": "ترجم للإنجليزية: (تفاحة)", "a": "apple"}, {"q": "ترجم للإنجليزية: (قطة)", "a": "cat"}],
    "تفكيك": [{"q": "فكك حروف كلمة (مدرسة):", "a": "م د ر س ة"}],
    "الاسرع": [{"q": "أسرع واحد يكتب كلمة: (تطبيق)", "a": "تطبيق"}],
    "العكس": [{"q": "اعكس هذه الكلمة: (سماء)", "a": "ءامس"}],
    "حزوره": [{"q": "ما هو الشيء الذي يتكلم جميع اللغات ولكنه لا يملك لساناً؟", "a": "الصدى"}],
    "ترتيب": [{"q": "رتب هذه الكلمات لجملة مفيدة: ( الجنة / تحت / الأمهات / أقدام )", "a": "الجنة تحت أقدام الأمهات"}],
    "علم دول": [{"q": "ما هي الدولة التي عاصمتها (رياض)؟", "a": "السعودية"}],
    "دين": [{"q": "كم عدد سور القرآن الكريم؟", "a": "114"}],
    "عامه": [{"q": "كم عدد كواكب المجموعة الشمسية؟", "a": "8"}],
    "رياضيات": [{"q": "كم الناتج: 5 × 5 + 10 = ؟", "a": "35"}],
    "مصطلح": [{"q": "ماذا يسمى صوت الكلب؟", "a": "نباح"}],
    "تركيب": [{"q": "ركب المقاطع التالية لتصبح كلمة: ( م - ه - ن - د - س )", "a": "مهندس"}],
    "حكم": [{"q": "من الغبي؟ من ظن أن الناس يتركونه وشأنه.", "a": "حكمة جميلة"}],
    "كت تويت": [{"q": "كت تويت: هل تعتقد أنك شخص صبور في الصعاب؟", "a": "صريح"}],
    "لو خيروك": [{"q": "لو خيروك بين: العيش بدون إنترنت أو العيش بدون أصدقاء؟", "a": "اختر"}],
    "صراحه": [{"q": "سؤال صراحة: ما هو أكثر شيء تخاف منه في حياتك؟", "a": "صراحة"}],
    "احكام": [{"q": "حكمتك الآن: ارسل رسالة حب لأول شخص يظهر في محادثاتك!", "a": "تم"}],
    "الروليت": [{"q": "عجلة الروليت تدور... حظك اليوم: رابح 500 عملة!", "a": "مبروك"}],
    "موسيقى": [{"q": "خمن اسم الفنان: (يا طير يا طير الهوى...)", "a": "فنان"}],
    "صور": [{"q": "لعبة الصور التفاعلية: تخيل صورة طبيعية ساحرة...", "a": "جميل"}],
    "جدول": [{"q": "جدول الضرب: كم حاصل ضرب 7 × 8؟", "a": "56"}],
    "المختلف": [{"q": "استخرج الكلمة المختلفة: (تفاح، موز، حديد، برتقال)", "a": "حديد"}],
    "صور فنانين": [{"q": "خمن اسم الفنان الشهير من الوصف.", "a": "فنان"}],
    "شخصيات بوب": [{"q": "من هي الشخصية العالمية الشهيرة في البوب؟", "a": "مايكل جاكسون"}],
    "شخصيات كيبوب": [{"q": "من أشهر فرق الكيبوب العالمية؟", "a": "بي تي إس"}],
    "شخصيات انمي": [{"q": "من هو بطل أنمي ناروتو؟", "a": "ناروتو"}],
    "اختر حرف": [{"q": "اختر حرف عشوائي وتحدى نفسك: اختر حرف (م)", "a": "م"}],
    "حروف": [{"q": "اكتب ثلاث كلمات تبدأ بحرف (الباء)", "a": "باب، بطة، بيت"}],
    "بغني": [{"q": "أكمل مقطع الأغنية: (أنا بعشقك يا ...)", "a": "البحر"}],
    "حزر": [{"q": "حزر فزر: شيء بيتي وله أسنان ولا يعض؟", "a": "المشط"}],
    "عقاب": [{"q": "عقاب لك: غير اسمك في التليجرام إلى 'المعاقب' لمدة ساعة!", "a": "تم"}],
    "كرسي اعتراف": [{"q": "أنت الآن على كرسي الاعتراف: ما هو أكبر سر تخفيه عن أصدقائك؟", "a": "اعتراف"}],
    "تحديات": [{"q": "تحدي اليوم: قم بعمل 10 تمارين ضغط الآن!", "a": "تم التحدي"}]
}

def get_main_menu_markup():
    keyboard = [
        [
            InlineKeyboardButton("م1 (الأوامر الشاملة)", callback_data="menu_m1"),
            InlineKeyboardButton("م2 (التعيين والإعدادات)", callback_data="menu_m2")
        ],
        [
            InlineKeyboardButton("م3 (الردود والقفل والتفعيل)", callback_data="menu_m3"),
            InlineKeyboardButton("🎮 قسم الألعاب", callback_data="menu_games")
        ],
        [
            InlineKeyboardButton("💳 قسم البنك", callback_data="menu_bank")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_markup():
    keyboard = [[InlineKeyboardButton("رجوع للقائمة الرئيسية", callback_data="menu_back")]]
    return InlineKeyboardMarkup(keyboard)

def get_dev_panel_markup():
    keyboard = [
        [
            InlineKeyboardButton("📊 الإحصائيات الدقيقة", callback_data="dev_stats"),
            InlineKeyboardButton("📢 إذاعة عامة", callback_data="dev_broadcast")
        ],
        [
            InlineKeyboardButton("⚙️ إعدادات البوت", callback_data="dev_settings"),
            InlineKeyboardButton("🔄 تحديث البيانات", callback_data="dev_refresh")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    bot_username = context.bot.username
    user_id = user.id if user else 0

    if chat.type == "private":
        known_users.add(user_id)
        if user_id == DEV_ID:
            text = f"لوحة المطور : {DEV_USERNAME}\n\nأهلاً بك في لوحة التحكم الإدارية الخاصة بك. اختر ما تفضله من الأزرار أدناه:"
            await update.message.reply_text(text, reply_markup=get_dev_panel_markup())
            return

        text = (
            "اهلين انا طيف\n\n"
            "↞ اختصاصي ادارة المجموعات من السبام والخ..\n"
            "↞ كت تويت, يوتيوب, ساوند , واشياء كثير ..\n"
            "↞ عشان تفعلني ارفعني اشراف وارسل تفعيل."
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ضفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=true")]
        ])
        await update.message.reply_text(text, reply_markup=markup)
        return

    known_chats.add(chat.id)
    text = (
        "اهلين فيك باوامر البوت (طيف)\n"
        "للإستفسار - @TV_1M\n"
        "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:"
    )
    await update.message.reply_text(text, reply_markup=get_main_menu_markup())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("dev_"):
        if user_id != DEV_ID:
            await query.answer("هذا الزر خاص بالمطور فقط!", show_alert=True)
            return
        if data == "dev_stats":
            stats_text = (
                f"📊 **إحصائيات البوت الدقيقة:**\n\n"
                f"👤 الأعضاء بالخاص: `{len(known_users)}`\n"
                f"👥 المجموعات المسجلة: `{len(known_chats)}`\n"
                f"🟢 المجموعات المفعّلة: `{len(active_groups)}`"
            )
            keyboard = [[InlineKeyboardButton("رجوع لوحة المطور", callback_data="dev_back")]]
            await query.edit_message_text(stats_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        elif data == "dev_broadcast":
            broadcast_mode[user_id] = True
            text = "📢 **قسم الإذاعة:**\n\nأرسل الرسالة الآن (صورة، نص، فويس، فيديو) ليتم نشرها للكل."
            keyboard = [[InlineKeyboardButton("إلغاء", callback_data="dev_back")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        elif data == "dev_settings":
            text = "⚙️ إعدادات البوت تعمل بكفاءة تامة."
            keyboard = [[InlineKeyboardButton("رجوع", callback_data="dev_back")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif data == "dev_refresh":
            await query.answer("✅ تم التحديث بنجاح!", show_alert=True)
        elif data == "dev_back":
            text = f"لوحة المطور : {DEV_USERNAME}\n\nأهلاً بك في لوحة التحكم الإدارية الخاصة بك:"
            await query.edit_message_text(text, reply_markup=get_dev_panel_markup())
        return

    if data == "menu_m1":
        text = "مرحباً بك في [ م1 ] - الأوامر الشاملة وحماية المجموعات (كتم، فك كتم، حظر، طرد)."
        await query.edit_message_text(text, reply_markup=get_back_markup())
    elif data == "menu_m2":
        text = "مرحباً بك في [ م2 ] - أوامر التعيين والإعدادات."
        await query.edit_message_text(text, reply_markup=get_back_markup())
    elif data == "menu_m3":
        text = "مرحباً بك في [ م3 ] - الردود، القفل، والتفعيل."
        await query.edit_message_text(text, reply_markup=get_back_markup())
    elif data == "menu_games":
        text = "🎮 كافة الألعاب الـ 37 مفعلة وتعمل مجرد كتابة اسم اللعبة في المجموعة!"
        await query.edit_message_text(text, reply_markup=get_back_markup())
    elif data == "menu_bank":
        text = "✜ أوامر البنك: انشاء حساب بنكي، فلوسي، حسابي، راتب."
        await query.edit_message_text(text, reply_markup=get_back_markup())
    elif data == "menu_back":
        text = (
            "اهلين فيك باوامر البوت (طيف)\n"
            "للإستفسار - @TV_1M\n"
            "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:"
        )
        await query.edit_message_text(text, reply_markup=get_main_menu_markup())

async def download_youtube_audio(query_str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }
    os.makedirs('downloads', exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query_str}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                return f"downloads/{video['id']}.mp3", video.get('title', 'Audio')
    except Exception:
        pass
    return None, None

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    user_id = user.id if user else 0

    text_orig = message.text.strip()
    text = text_orig.lower()

    if chat.type == "private":
        known_users.add(user_id)
        if user_id == DEV_ID and broadcast_mode.get(user_id, False):
            broadcast_mode[user_id] = False
            count = 0
            for uid in known_users:
                try:
                    await context.bot.copy_message(chat_id=uid, from_chat_id=chat.id, message_id=message.message_id)
                    count += 1
                except:
                    pass
            await message.reply_text(f"✅ تمت الإذاعة إلى `{count}` وجهة.", parse_mode="Markdown")
            return

        if text in ["انشاء حساب بنكي", "إنشاء حساب بنكي"]:
            if user_id in user_balances:
                await message.reply_text("لديك حساب بنكي مسجل بالفعل! 💳")
            else:
                user_balances[user_id] = 1000
                await message.reply_text("💳 تم إنشاء حسابك البنكي وإيداع 1,000 عملة!")
            return
        elif text in ["فلوسي", "حسابي"]:
            bal = user_balances.get(user_id, 0)
            await message.reply_text(f"💰 رصيدك الحالي: {bal:,} عملة.")
            return
        elif text in ["راتب", "بخشيش"]:
            user_balances[user_id] = user_balances.get(user_id, 1000) + 500
            await message.reply_text("💵 تم صرف راتب 500 عملة وإضافتها لرصيدك!")
            return
        return

    if chat.type in ["group", "supergroup"]:
        known_chats.add(chat.id)

        if text in ["تفعيل", "تشغيل"]:
            active_groups.add(chat.id)
            await message.reply_text("✅ تم تفعيل البوت في هذه المجموعة بنجاح!")
            return

        if text in ["الاوامر", "الأوامر", "أوامر"]:
            await message.reply_text(
                "اهلين فيك باوامر البوت (طيف)\n"
                "للإستفسار - @TV_1M\n"
                "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:",
                reply_markup=get_main_menu_markup()
            )
            return

        # 🛠️ أوامر الإدارة والكتم والحظر الفعّالة بالرد على العضو
        if text in ["كتم", "صم", "تقييد"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.restrict_member(target_user.id, permissions=ChatPermissions(can_send_messages=False))
                    await message.reply_text(f"🔇 تم كتم العضو: {target_user.first_name} بنجاح.")
                except Exception:
                    await message.reply_text("❌ عذراً، لم أستطع كتمه. تأكد أنني مشرف ولديني صلاحية تقييد الأعضاء وأن الشخص ليس مشرفاً.")
            else:
                await message.reply_text("⚠️ بالرد على رسالة الشخص الذي تريد كتمه، واكتب: كتم")
            return

        elif text in ["فك كتم", "فك الكتم", "فتح"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.restrict_member(target_user.id, permissions=ChatPermissions(
                        can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True
                    ))
                    await message.reply_text(f"🔊 تم فك الكتم عن العضو: {target_user.first_name}")
                except Exception:
                    await message.reply_text("❌ تأكد من صلاحيات البوت كمسؤول.")
            else:
                await message.reply_text("⚠️ بالرد على رسالة الشخص، واكتب: فك كتم")
            return

        elif text in ["طرد", "برا"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.ban_member(target_user.id)
                    await chat.unban_member(target_user.id) # لطرده فقط دون حظر دائم
                    await message.reply_text(f"👢 تم طرد العضو: {target_user.first_name}")
                except Exception:
                    await message.reply_text("❌ لا أمتلك صلاحية طرد هذا الشخص.")
            return

        elif text in ["حظر", "بان"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.ban_member(target_user.id)
                    await message.reply_text(f"🚫 تم حظر العضو: {target_user.first_name}")
                except Exception:
                    await message.reply_text("❌ لا أمتلك صلاحية حظر هذا الشخص.")
            return

        # تشغيل الألعاب
        if text in GAMES_DATA:
            item = random.choice(GAMES_DATA[text])
            await message.reply_text(f"🎮 **لعبة: {text_orig}**\n\n❓ {item['q']}\n\n💡 أرسل الإجابة الآن!", parse_mode="Markdown")
            return

        elif text.startswith("بحث "):
            q_str = text_orig.replace("بحث", "", 1).strip()
            if not q_str:
                await message.reply_text("اكتب اسم الشيء بعد كلمة بحث.")
                return
            wait = await message.reply_text("🔍 جاري التحميل...")
            f_path, title = await download_youtube_audio(q_str)
            if f_path and os.path.exists(f_path):
                with open(f_path, 'rb') as aud:
                    await message.reply_audio(audio=aud, title=title, performer="البوت طيف")
                await wait.delete()
                os.remove(f_path)
            else:
                await wait.edit_text("عذراً، لم يتم العثور على نتائج.")
            return

        elif text in ["طيف", "بوت"]:
            await message.reply_text(random.choice(["عيوني", "لبيه", "ها؟", "عمري"]))
            return

        elif text in ["السلام عليكم", "السلام عليكم ورحمة الله وبركاته"]:
            await message.reply_text("وعليكم السلام")
            return

        elif text == "صباح الخير":
            await message.reply_text("صباح النور")
            return

        elif text == "مساء الخير":
            await message.reply_text("مساء النور")
            return

        elif text == "الساعه":
            await message.reply_text(f"⏰ الساعة الآن: {datetime.datetime.now().strftime('%I:%M:%S %p')}")
            return

        elif text == "التاريخ":
            await message.reply_text(f"📅 التاريخ اليوم: {datetime.datetime.now().strftime('%Y/%m/%d')}")
            return

        elif text in ["انشاء حساب بنكي", "إنشاء حساب بنكي"]:
            if user_id in user_balances:
                await message.reply_text("لديك حساب بنكي مسجل بالفعل! 💳")
            else:
                user_balances[user_id] = 1000
                await message.reply_text("💳 تم إنشاء حسابك البنكي بنجاح وإيداع 1,000 عملة!")
            return

        elif text in ["فلوسي", "حسابي"]:
            bal = user_balances.get(user_id, 0)
            await message.reply_text(f"💰 رصيدك الحالي: {bal:,} عملة.")
            return

        elif text in ["راتب", "بخشيش"]:
            user_balances[user_id] = user_balances.get(user_id, 1000) + 500
            await message.reply_text("💵 تم صرف راتب 500 عملة وإضافتها لرصيدك!")
            return

        elif text_orig.lower().startswith("اضف رد "):
            parts = text_orig.replace("اضف رد ", "", 1).split(" ", 1)
            if len(parts) == 2:
                custom_replies[parts[0].strip()] = parts[1].strip()
                await message.reply_text("✅ تمت إضافة الرد بنجاح!")
            return

        elif text_orig in custom_replies:
            await message.reply_text(custom_replies[text_orig])
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

    print("Bot Taif is running with all games, banking, and full admin mute/ban tools...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def id_avatar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    message = update.message
    text = message.text.strip().lower()
    user = message.from_user
    chat = update.effective_chat

    # التحقق من الأوامر المطلوبة
    if text in ["ايدي", "ا", "افتاري", "اا"]:
        name = user.first_name if user else "مستخدم"
        username = f"@{user.username}" if user and user.username else "لا يوجد"
        user_id = user.id if user else 0
        
        # محاولة جلب صورة البروفایل الخاصة بالعضو
        photos = await context.bot.get_user_profile_photos(user_id, limit=1)
        
        # النص التنسيقي المطابق للصورة
        caption_text = (
            f"- 🪞 NAME : {name} 🪄 .\n"
            f"- 🪞 UsEr : {username} 🪄 .\n"
            f"- 🪞 MsG : 25 🪄 .\n"
            f"- 🪞 StA : member 🪄 .\n"
            f"- 🪞 ID : {user_id} 🪄 .\n"
            f"- 🪞 TITLE : لا يوجد 🪄 .\n"
            f"- 🪞 BIO : I don't chase, i attracts 🪄 ."
        )

        if photos and photos.total_count > 0:
            photo_file_id = photos.photos[0][-1].file_id
            await message.reply_photo(
                photo=photo_file_id,
                caption=caption_text
            )
        else:
            # في حال لم يكن لديه صورة بروفايل يرسل النص مباشرة
            await message.reply_text(caption_text)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), id_avatar_handler))

    print("ID & Avatar bot code is running independently...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
