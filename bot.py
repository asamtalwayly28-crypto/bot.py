import os
import logging
import datetime
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
                f"👤 عدد الأعضاء في الخاص: `{len(known_users)}`\n"
                f"👥 عدد المجموعات المسجلة: `{len(known_chats)}`\n"
                f"🟢 المجموعات المفعّلة: `{len(active_groups)}`\n"
                f"🤖 حالة البوت: `يعمل بكفاءة 100%`"
            )
            keyboard = [[InlineKeyboardButton("رجوع لوحة المطور", callback_data="dev_back")]]
            await query.edit_message_text(stats_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "dev_broadcast":
            broadcast_mode[user_id] = True
            text = (
                "📢 **قسم الإذاعة:**\n\n"
                "الرجاء إرسال الرسالة الآن (صورة، نص، فويس، أو فيديو) ليتم نشرها لجميع الأعضاء والمجموعات المسجلة."
            )
            keyboard = [[InlineKeyboardButton("إلغاء والعودة", callback_data="dev_back")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "dev_settings":
            text = (
                "⚙️ **إعدادات البوت والتحكم:**\n\n"
                "• يمكنك تعديل الأوامر أو الردود برمجياً من الكود مباشرة.\n"
                "• البوت متصل ومحدث بأحدث مكتبات يوتيوب وحماية المجموعات."
            )
            keyboard = [[InlineKeyboardButton("رجوع لوحة المطور", callback_data="dev_back")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "dev_refresh":
            await query.answer("✅ تم تحديث بيانات البوت والإحصائيات بنجاح!", show_alert=True)

        elif data == "dev_back":
            text = f"لوحة المطور : {DEV_USERNAME}\n\nأهلاً بك في لوحة التحكم الإدارية الخاصة بك. اختر ما تفضله من الأزرار أدناه:"
            await query.edit_message_text(text, reply_markup=get_dev_panel_markup())
        return

    if data == "menu_m1":
        text = (
            "مرحباً بك في [ م1 ] - الأوامر الشاملة:\n\n"
            "❨ أوامر البحث والصوتيات ❩\n"
            "• بحث + اسم الأغنية أو الفيديو (للبحث وجلب الصوت من يوتيوب)\n\n"
            "❨ أوامر الرفع والتنزيل ❩\n"
            "• رفع / تنزيل (مشرف، مالك اساسي، مالك، مدير، ادمن، مميز)\n\n"
            "❨ أوامر المسح ❩\n"
            "• مسح (المالكيين، المدراء، الادمنيه، المميزين، المحظورين، المكتومين، قائمة المنع)"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())

    elif data == "menu_m2":
        text = (
            "مرحباً بك في [ م2 ] - أوامر التعيين ورؤية الإعدادات:\n\n"
            "❨ أوامر التعيين ❩\n"
            "• تعيين الترحيب\n"
            "• تعيين القوانين\n"
            "• تغيير رتبه\n"
            "• تغيير امر"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())

    elif data == "menu_m3":
        text = (
            "مرحباً بك في [ م3 ] - الردود، القفل، والتفعيل:\n\n"
            "❨ أوامر الردود ❩\n"
            "• الردود، اضف رد، مسح رد، مسح الردود\n\n"
            "❨ أوامر القفل والفتح ❩\n"
            "• قفل / فتح: (الفويسات، الفيديو، الصور، الروابط، الدردشه، الــكـــل)\n\n"
            "• أمر التفعيل لإدخال البوت للعمل بالمجموعة: `تفعيل`"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())

    elif data == "menu_games":
        text = (
            "🎮 مرحباً بك في قسم الألعاب والتسلية:\n\n"
            "✽ جمل ✽ كلمات ✽ دين ✽ عربي ✽ اكمل ✽ صور\n"
            "✽ كت تويت ✽ مؤقت ✽ اعلام ✽ معاني ✽ تخمين\n"
            "❖ فلوسي ↼ عشان تشوف فلوسك"
        )
        await query.edit_message_text(text, reply_markup=get_back_markup())

    elif data == "menu_bank":
        text = (
            "✜ أوامر البنك والأموال:\n\n"
            "⌯ انشاء حساب بنكي\n"
            "⌯ تحويل\n"
            "⌯ حسابي\n"
            "⌯ فلوسي\n"
            "⌯ راتب\n"
            "⌯ بخشيش\n"
            "⌯ توب الفلوس"
        )
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
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }
    
    os.makedirs('downloads', exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch1:{query_str}"
            info = ydl.extract_info(search_query, download=True)
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                file_id = video['id']
                title = video.get('title', 'Audio')
                file_path = f"downloads/{file_id}.mp3"
                return file_path, title
    except Exception as e:
        print(f"Error downloading audio: {e}")
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
            sent_count = 0
            
            for uid in list(known_users):
                try:
                    await context.bot.copy_message(chat_id=uid, from_chat_id=chat.id, message_id=message.message_id)
                    sent_count += 1
                except:
                    pass
            for cid in list(known_chats):
                try:
                    await context.bot.copy_message(chat_id=cid, from_chat_id=chat.id, message_id=message.message_id)
                    sent_count += 1
                except:
                    pass
            
            await message.reply_text(f"✅ تمت الإذاعة بنجاح إلى `{sent_count}` وجهة (أعضاء ومجموعات).", parse_mode="Markdown")
            return

        if text in ["انشاء حساب بنكي", "إنشاء حساب بنكي"]:
            if user_id in user_balances:
                await message.reply_text("لديك حساب بنكي مسجل بالفعل! 💳")
            else:
                user_balances[user_id] = 1000
                await message.reply_text("💳 تم إنشاء حسابك البنكي بنجاح وإيداع 1,000 عملة كهدية بداية!")
            return

        elif text in ["فلوسي", "حسابي"]:
            if user_id not in user_balances:
                await message.reply_text("ليس لديك حساب بنكي! اكتب: (انشاء حساب بنكي)")
            else:
                bal = user_balances[user_id]
                await message.reply_text(f"💰 رصيدك الحالي: {bal:,} عملة.")
            return

        elif text in ["راتب", "بخشيش"]:
            if user_id not in user_balances:
                await message.reply_text("ليس لديك حساب بنكي! اكتب: (انشاء حساب بنكي)")
            else:
                user_balances[user_id] += 500
                await message.reply_text("💵 تم صرف راتب 500 عملة وإضافتها لرصيدك!")
            return

        return

    if chat.type in ["group", "supergroup"]:
        known_chats.add(chat.id)

        if text in ["تفعيل", "تشغيل"]:
            active_groups.add(chat.id)
            await message.reply_text("✅ تم تفعيل البوت في هذه المجموعة بنجاح وجاهز للعمل!")
            return

        if text in ["الاوامر", "الأوامر", "أوامر"]:
            await message.reply_text(
                "اهلين فيك باوامر البوت (طيف)\n"
                "للإستفسار - @TV_1M\n"
                "اختر القسم المطلوب من الأزرار الشفافة بالأسفل:",
                reply_markup=get_main_menu_markup()
            )
            return

        elif text.startswith("بحث "):
            query_str = text_orig.replace("بحث", "", 1).strip()
            if not query_str:
                await message.reply_text("الرجاء كتابة اسم الشيء الذي تريد البحث عنه بعد كلمة (بحث).")
                return

            wait_msg = await message.reply_text("🔍 جاري البحث والتحميل من اليوتيوب، ثواني...")
            
            file_path, title = await download_youtube_audio(query_str)
            
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as audio_file:
                        await message.reply_audio(
                            audio=audio_file,
                            title=title,
                            performer="البوت طيف",
                            caption=f"🎵 تم العثور على: {title}"
                        )
                    await wait_msg.delete()
                    os.remove(file_path)
                except Exception as e:
                    await wait_msg.edit_text("حدث خطأ أثناء إرسال الملف الصوتي.")
            else:
                await wait_msg.edit_text("عذراً، لم يتم العثور على نتائج مطابقة أو حدث خطأ في التحميل.")
            return

        elif text in ["طيف", "بوت"]:
            replies = ["عيوني", "لبيه", "ها؟", "عمري"]
            await message.reply_text(random.choice(replies))
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
            now = datetime.datetime.now().strftime("%I:%M:%S %p")
            await message.reply_text(f"⏰ الساعة الآن: {now}")
            return

        elif text == "التاريخ":
            today = datetime.datetime.now().strftime("%Y/%m/%d")
            await message.reply_text(f"📅 التاريخ اليوم: {today}")
            return

        elif text in ["انشاء حساب بنكي", "إنشاء حساب بنكي"]:
            if user_id in user_balances:
                await message.reply_text("لديك حساب بنكي مسجل بالفعل! 💳")
            else:
                user_balances[user_id] = 1000
                await message.reply_text("💳 تم إنشاء حسابك البنكي بنجاح وإيداع 1,000 عملة كهدية بداية!")
            return

        elif text in ["فلوسي", "حسابي"]:
            if user_id not in user_balances:
                await message.reply_text("ليس لديك حساب بنكي! اكتب: (انشاء حساب بنكي)")
            else:
                bal = user_balances[user_id]
                await message.reply_text(f"💰 رصيدك الحالي: {bal:,} عملة.")
            return

        elif text in ["راتب", "بخشيش"]:
            if user_id not in user_balances:
                await message.reply_text("ليس لديك حساب بنكي! اكتب: (انشاء حساب بنكي)")
            else:
                user_balances[user_id] += 500
                await message.reply_text("💵 تم صرف راتب 500 عملة وإضافتها لرصيدك!")
            return

        elif text_orig.lower().startswith("اضف رد "):
            parts = text_orig.replace("اضف رد ", "", 1).split(" ", 1)
            if len(parts) == 2:
                k, v = parts
                custom_replies[k.strip()] = v.strip()
                await message.reply_text(f"✅ تمت إضافة الرد بنجاح!")
            else:
                await message.reply_text("الاستخدام الخاطئ. اكتب: (اضف رد الكلمة الرد_المخصص)")
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

    print("Bot Taif is fully running with Dev Panel & YouTube Audio Search...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
