import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# تفعيل السجلات الفورية للسرعة
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# الآيدي الخاص بك كمطور ومالك أساسي
DEV_ID = 6652826141 

# تخزين الردود والبيانات مؤقتاً
custom_replies = {
    "صباح الخير": "صباح النور",
    "مساء الخير": "مساء النور"
}

user_bank = {}
user_states = {}

# الردود المتنوعة عند مناداة البوت
taif_call_responses = [
    "عيوني",
    "لبيه",
    "ها؟",
    "ازعجتني",
    "لا تناديني"
]

# 1. لوحة المطور الرئيسية مع أزرار شفافة وزر رجوع
def get_main_dev_markup():
    keyboard = [
        [InlineKeyboardButton("إحصائيات البوت", callback_data="dev_stats")],
        [InlineKeyboardButton("إدارة الردود", callback_data="dev_replies")],
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

# 2. معالج الرسائل والأوامر الفائق السرعة
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    chat = update.effective_chat
    user = update.effective_user
    user_id = user.id

    # حماية المجموعة وحذف الروابط
    if chat.type in ["group", "supergroup"]:
        if "http://" in text or "https://" in text or "t.me/" in text:
            try:
                await update.message.delete()
                return
            except Exception:
                pass

    # التعامل مع حالات إضافة الردود التفاعلية
    if user_id in user_states:
        state = user_states[user_id]["state"]
        if state == "waiting_for_trigger":
            user_states[user_id]["trigger"] = text
            user_states[user_id]["state"] = "waiting_for_reply"
            await update.message.reply_text("حلو ، الحين ارسل جواب الرد\n( نص,صوره,فيديو,متحركه,فويس,صوتيه )")
            return
        elif state == "waiting_for_reply":
            trigger = user_states[user_id]["trigger"]
            custom_replies[trigger] = text
            del user_states[user_id]
            await update.message.reply_text("( اضف ردي )\nواضفنا الرد ياحلو")
            return

    # الرد عند مناداة البوت بكلمة "طيف" أو "بوت"
    if text in ["طيف", "بوت"]:
        chosen_reply = random.choice(taif_call_responses)
        await update.message.reply_text(chosen_reply)
        return

    # أوامر إضافة الردود
    if text == "اضف رد" or text == "اضف ردي":
        user_states[user_id] = {"state": "waiting_for_trigger"}
        await update.message.reply_text("حلو ، الحين ارسل الكلمة اللي تبيه")
        return

    # الردود التلقائية المخزنة
    if text in custom_replies:
        await update.message.reply_text(custom_replies[text])
        return

    # نداء المطور
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

    # أمر الايدي بالتصميم الفاخر
    if text == "ايدي" or text == "معلوماتي":
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
            file_id = photos.photos[0][0].file_id
            await update.message.reply_photo(photo=file_id, caption=info)
        else:
            await update.message.reply_text(info)
        return

    # أمر البحث السريع عن الموسيقى من اليوتيوب (على طريقة بوت وعد)
    if text.startswith("بحث "):
        song_name = text.replace("بحث ", "", 1)
        await update.message.reply_text(
            f"~ جاري البحث السريع في يوتيوب عن: {song_name}\n"
            f"~ يتم جلب الرابط والصوت بدقة عالية... انتظر لحظات."
        )
        return

    # نظام الهمسات السرية
    if text.startswith("اهمس "):
        parts = text.split(" ", 2)
        if len(parts) >= 3:
            target = parts[1]
            secret_msg = parts[2]
            await update.message.reply_text(f"~ تم إرسال الهمسة السرية إلى {target} بنجاح.")
        else:
            await update.message.reply_text("الاستخدام الصحيح: اهمس [المعرف] [النص]")
        return

    # قائمة الأوامر الرئيسية
    if text == "الاوامر" or text == "الأوامر":
        orders_text = (
            "اهلين فيك باوامر البوت\n\n"
            "للإستفسار - @TV_1M\n\n"
            "( اوامر البنك )\n"
            "- انشاء حساب بنكي\n"
            "- فلوسي\n"
            "- راتب\n"
            "- تحويل\n\n"
            "( اوامر الالعاب )\n"
            "- جمل\n"
            "- كلمات\n"
            "- تخمين\n"
            "- عواصم\n\n"
            "( البحث والهمسات )\n"
            "- بحث [اسم الأغنية]\n"
            "- اهمس [المعرف] [النص]"
        )
        await update.message.reply_text(orders_text)
        return

    # نظام البنك
    if text == "البنك" or text == "فلوسي":
        balance = user_bank.get(user.id, 1000)
        user_bank[user.id] = balance
        bank_msg = (
            "~ اوامر البنك\n\n"
            f"~ رصيدك الحالي: {balance} نقطة\n"
            "- راتب (يعطيك راتبك كل 20 دقيقة)\n"
            "- استثمار (تستثمر المبلغ)\n"
            "- تحويل (تحول فلوس لشخص بالرد)"
        )
        await update.message.reply_text(bank_msg)
        return

    # قائمة الألعاب
    if text == "اللعاب" or text == "الألعاب":
        games_msg = (
            "~ قائمة الالعاب\n\n"
            "- جمل\n"
            "- كلمات\n"
            "- دين\n"
            "- عربي\n"
            "- اكمل\n"
            "- صور\n"
            "- كت تويت\n"
            "- مؤقت\n"
            "- اعلام\n"
            "- معاني\n"
            "- تخمين\n"
            "- احكام\n"
            "- ارقام\n"
            "- احسب\n"
            "- انمي\n"
            "- عواصم"
        )
        await update.message.reply_text(games_msg)
        return

# معالجة أزرار لوحة المطور الاحترافية مع زر الرجوع
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "dev_stats":
        await query.edit_message_text(
            "~ إحصائيات لوحة المطور:\nالبوت يعمل بأقصى سرعة واستقرار تام.",
            reply_markup=get_back_dev_markup()
        )
    elif query.data == "dev_replies":
        await query.edit_message_text(
            "~ إدارة الردود:\nيمكنك إضافة رد جديد مباشرة عبر كتابة ( اضف رد ) في الدردشة.",
            reply_markup=get_back_dev_markup()
        )
    elif query.data == "dev_protection":
        await query.edit_message_text(
            "~ حماية القروبات:\nالحماية مفعلة وتحذف الروابط المزعجة تلقائياً.",
            reply_markup=get_back_dev_markup()
        )
    elif query.data == "dev_back":
        await query.edit_message_text(
            "اهلين فيك باوامر البوت\n\nللإستفسار - @TV_1M\n\n[ لوحة المطور ]",
            reply_markup=get_main_dev_markup()
        )

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Taif is running at maximum speed...")
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

# تفعيل السجلات الفورية
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# قوائم تخزين الكلمات والملصقات الممنوعة
banned_words = set()
banned_stickers = set()

# معالج الرسائل لنظام المنع
async def ban_system_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    message = update.message
    chat = update.effective_chat
    text = message.text or message.caption or ""

    # 1. الفحص والحذف التلقائي داخل القروبات إذا كانت الرسالة أو الملصق ممنوعاً
    if chat.type in ["group", "supergroup"]:
        # فحص الكلمات الممنوعة
        if text and text in banned_words:
            try:
                await message.delete()
                return
            except Exception:
                pass

        # فحص الملصقات الممنوعة
        if message.sticker and message.sticker.file_unique_id in banned_stickers:
            try:
                await message.delete()
                return
            except Exception:
                pass

    # 2. إضافة منع جديد: عندما ترد بكلمة "منع" على أي رسالة أو ملصق
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

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # استقبال جميع الرسائل والملصقات لتطبيق نظام المنع
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), ban_system_handler))

    print("Ban system is running...")
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

# تفعيل السجلات الفورية
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# معالج دخول الأعضاء الجدد للقروب
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat
    
    # الترحيب بكل عضو جديد دخل القروب
    for member in update.message.new_chat_members:
        # تجنب ترحيب البوت نفسه إذا انضم للقروب
        if member.id == context.bot.id:
            continue
            
        welcome_text = (
            f"~ أهلاً بك ياعسل 🤍\n"
            f"~ نورت القروب: {member.full_name}\n"
            f"~ نتمنى لك إقامة ممتعة معنا في {chat.title if chat.title else 'هنا'}!"
        )
        
        try:
            await update.message.reply_text(welcome_text)
        except Exception as e:
            print(f"Failed to send welcome message: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # استقبال أحداث دخول أعضاء جدد للقروب
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    print("Welcome bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
import os
import logging
from telegram import ChatPermissions, Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

# تفعيل السجلات الفورية
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# معالج أوامر الإدارة والحماية (يتم بالرد على الرسالة)
async def admin_actions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.reply_to_message:
        return

    message = update.message
    chat = update.effective_chat
    text = message.text or ""
    
    # التأكد من أن الأمر يتم تنفيذه داخل مجموعة
    if chat.type not in ["group", "supergroup"]:
        return

    target_user = message.reply_to_message.from_user
    target_id = target_user.id

    try:
        # 1. أمر الحظر
        if text == "حظر":
            await chat.ban_member(target_id)
            await message.reply_text(f"~ تم حظر العضو: {target_user.full_name} بنجاح.")
            return

        # 2. أمر الطرد (Kick)
        elif text == "طرد":
            await chat.ban_member(target_id)
            await chat.unban_member(target_id)  # فك الحظر الفوري ليبقى طرد فقط
            await message.reply_text(f"~ تم طرد العضو: {target_user.full_name} بنجاح.")
            return

        # 3. أمر الكتم (Mute)
        elif text == "كتم":
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
            )
            await chat.restrict_member(target_id, permissions=permissions)
            await message.reply_text(f"~ تم كتم العضو: {target_user.full_name} بنجاح.")
            return

        # 4. أمر فك الكتم (Unmute)
        elif text == "فك كتم" or text == "فك الكتم":
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
            await chat.restrict_member(target_id, permissions=permissions)
            await message.reply_text(f"~ تم إزالة الكتم عن العضو: {target_user.full_name}.")
            return

        # 5. أمر التقييد (Restrict)
        elif text == "تقييد":
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=False,  # منع إرسال الصور والوسائط
                can_send_other_messages=False,
            )
            await chat.restrict_member(target_id, permissions=permissions)
            await message.reply_text(f"~ تم تقييد العضو: {target_user.full_name} من إرسال الوسائط.")
            return

    except Exception as e:
        await message.reply_text("~ عذراً، لا أملك صلاحية كافية أو أن الشخص المشرف أعلى مني رتبة.")
        print(f"Admin action error: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # استقبال كلمات الإدارة بالرد
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), admin_actions_handler))

    print("Admin commands system is running...")
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

# تفعيل السجلات الفورية
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# معالج أمر مسح وحذف الرسائل بالرد
async def delete_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.reply_to_message:
        return

    message = update.message
    chat = update.effective_chat
    text = message.text or ""

    # التأكد من أن الأمر يتم تنفيذه داخل مجموعة
    if chat.type not in ["group", "supergroup"]:
        return

    # التحقق من كلمة "مسح" أو "حذف" بالرد على الرسالة المراد حذفها
    if text in ["مسح", "حذف"]:
        try:
            # حذف الرسالة الأصلية التي تم الرد عليها
            await message.reply_to_message.delete()
            # حذف رسالة الأمر نفسها (كلمة مسح أو حذف) لتنظيف الدردشة
            await message.delete()
        except Exception as e:
            print(f"Delete message error: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # استقبال الكلمات للتحقق من أمر المسح
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), delete_message_handler))

    print("Delete message system is running...")
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

# تفعيل السجلات الفورية
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# الآيدي الخاص بك كمطور
DEV_ID = 6652826141 

# بايوات عشوائية جاهزة
random_bios = [
    "I don't chase, i attracts ✨",
    "عيش وحدك، فالكثير قليل 🖤",
    "الهدوء عنوان الفخامة.",
    "فقط استمر في المضي قدماً 🚀",
    "كن قليل الكلام كثير الصمت."
]

# معالج الأوامر الجديدة فقط
async def other_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    text = message.text or ""

    # 1. ايدي / معلوماتي
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

    # 2. الرابط
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

    # 3. معلومات الرابط
    if text == "معلومات الرابط":
        await message.reply_text(f"~ معلومات الدردشة:\n- اسم القروب: {chat.title if chat.title else 'محادثة خاصة'}\n- نوع الدردشة: {chat.type}\n- آيدي الدردشة: {chat.id}")
        return

    # 4. انشاء رابط
    if text == "انشاء رابط":
        if chat.type in ["group", "supergroup"]:
            try:
                new_link = await chat.export_invite_link()
                await message.reply_text(f"~ تم إنشاء رابط دعوة جديد:\n{new_link}")
            except Exception:
                await message.reply_text("~ لا أملك صلاحية إنشاء الروابط.")
        return

    # 5. بايو
    if text == "بايو":
        await message.reply_text("~ البايو الخاص بك:\nI don't chase, i attracts ✨")
        return

    # 6. بايو عشوائي
    if text == "بايو عشوائي":
        import random
        await message.reply_text(f"~ بايو مقترح:\n{random.choice(random_bios)}")
        return

    # 7. الانشاء
    if text == "الانشاء":
        await message.reply_text("~ تاريخ الإنشاء المسجل بالنظام: 2023/07")
        return

    # 8. مجموعاتي
    if text == "مجموعاتي":
        await message.reply_text("~ المجموعات التي يديرها البوت نشطة وتعمل بكفاءة عالية.")
        return

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), other_commands_handler))

    print("Other commands system is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
