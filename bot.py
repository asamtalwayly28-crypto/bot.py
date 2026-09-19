import os
import logging
import random
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

# متغيرات لحفظ جلسات الألعاب الجماعية لكل قروب
active_games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت طيف 🌟\nالبوت شغال وجاهز لإدارة القروب والألعاب الجماعية.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    text_orig = message.text.strip()
    text = text_orig.lower()

    if chat.type in ["group", "supergroup"]:
        chat_id = chat.id

        # 1. أوامر الحماية (كتم، طرد، حظر) مع رد بالاسم
        if text in ["كتم", "صم", "تقييد"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.restrict_member(target_user.id, permissions=ChatPermissions(can_send_messages=False))
                    await message.reply_text(f"🔇 تم كتم العضو ({target_user.first_name}) من المجموعة بنجاح.")
                except Exception:
                    await message.reply_text("❌ تأكد أن البوت مشرف ولديه صلاحية تقييد الأعضاء.")
            else:
                await message.reply_text("⚠️ بالرد على رسالة الشخص واكتب: كتم")
            return

        elif text in ["فك كتم", "فك الكتم", "فتح"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.restrict_member(target_user.id, permissions=ChatPermissions(
                        can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True
                    ))
                    await message.reply_text(f"🔊 تم فك الكتم عن العضو ({target_user.first_name}).")
                except Exception:
                    await message.reply_text("❌ تأكد من صلاحيات البوت.")
            else:
                await message.reply_text("⚠️ بالرد على رسالة الشخص واكتب: فك كتم")
            return

        elif text in ["طرد", "برا"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.ban_member(target_user.id)
                    await chat.unban_member(target_user.id)
                    await message.reply_text(f"👢 تم طرد العضو ({target_user.first_name}) من المجموعة.")
                except Exception:
                    await message.reply_text("❌ لا أمتلك صلاحية طرد هذا الشخص.")
            else:
                await message.reply_text("⚠️ بالرد على رسالة الشخص واكتب: طرد")
            return

        elif text in ["حظر", "بان"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.ban_member(target_user.id)
                    await message.reply_text(f"🚫 تم حظر العضو ({target_user.first_name}) نهائياً.")
                except Exception:
                    await message.reply_text("❌ لا أمتلك صلاحية حظر هذا الشخص.")
            return

        # 2. نظام لعبة (احكام / عقاب) الجماعية بالتسجيل والقرعة العشوائية
        if text in ["احكام", "عقاب"]:
            active_games[chat_id] = {
                "game_name": text_orig,
                "players": [],
                "status": "registering"
            }
            await message.reply_text(
                f"• تم بدأ لعبة ({text_orig}) وتم تسجيلك كمنشئ للعبة 🎮\n"
                "• اللي بيلعب يرسل كلمة ( انا ) ."
            )
            return

        # إذا كانت اللعبة في مرحلة تسجيل اللاعبين
        if chat_id in active_games and active_games[chat_id]["status"] == "registering":
            if text == "انا":
                if user.id not in [p["id"] for p in active_games[chat_id]["players"]]:
                    active_games[chat_id]["players"].append({"id": user.id, "name": user.first_name})
                    await message.reply_text(f"✅ تم انضمامك للعبة ({user.first_name}), العدد الحالي: {len(active_games[chat_id]['players'])}")
                return
            
            # إذا كتب المنشئ أو أي شخص كلمة "نعم" لإيقاف التسجيل وبدء القرعة
            elif text == "نعم":
                game_data = active_games[chat_id]
                players = game_data["players"]
                
                if len(players) < 2:
                    await message.reply_text("⚠️ عذراً، لا يوجد لاعبون كفاية لبدء القرعة (يجب أن يكون هناك شخصين على الأقل يرسلون 'انا').")
                    return
                
                # اختيار الحاكم والمحكوم عليه عشوائياً
                ruler = random.choice(players)
                remaining_players = [p for p in players if p["id"] != ruler["id"]]
                target = random.choice(remaining_players) if remaining_players else ruler

                # إرسال النتيجة بالشكل المطلوب
                result_text = (
                    f"🎲 **نتائج قرعة لعبة {game_data['game_name']}:**\n\n"
                    f"• اخترت الشخص ↤︎ ( {target['name']} ) ليتم الحكم عليه 🪄\n"
                    f"• الحاكم ↤︎ ( {ruler['name']} ) 👑"
                )
                await message.reply_text(result_text, parse_mode="Markdown")
                
                # إنهاء الجلسة الحالية للقروب
                del active_games[chat_id]
                return

        # الردود السريعة
        elif text in ["طيف", "بوت"]:
            await message.reply_text("عيوني 🤍")
        elif text == "السلام عليكم":
            await message.reply_text("وعليكم السلام ورحمة الله وبركاته ✨")

def main():
    if not TOKEN:
        logger.error("خطأ: لم يتم العثور على التوكن!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("جاري تشغيل بوت طيف...")
    application.run_polling()

if __name__ == "__main__":
    main()
import os
import logging
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت طيف 🌟\nالبوت شغال وجاهز لإدارة القروب.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    message = update.message
    chat = update.effective_chat
    text_orig = message.text.strip()
    text = text_orig.lower()

    if chat.type in ["group", "supergroup"]:
        # 1. أوامر الكتم (بالرد أو بكتابة الاسم)
        if text in ["كتم", "صم", "تقييد"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.restrict_member(target_user.id, permissions=ChatPermissions(can_send_messages=False))
                    await message.reply_text(f"🔇 تم كتم العضو ({target_user.first_name}) من المجموعة بنجاح.")
                except Exception:
                    await message.reply_text("❌ تأكد أن البوت مشرف ولديه صلاحية تقييد الأعضاء.")
            else:
                await message.reply_text("⚠️ يا أسامة، استخدم الكتم بالرد على رسالة العضو المطلوب.")
            return

        # 2. فك الكتم
        elif text in ["فك كتم", "فك الكتم", "فتح"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.restrict_member(target_user.id, permissions=ChatPermissions(
                        can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True
                    ))
                    await message.reply_text(f"🔊 تم فك الكتم عن العضو ({target_user.first_name}).")
                except Exception:
                    await message.reply_text("❌ تأكد من صلاحيات البوت الإدارية.")
            else:
                await message.reply_text("⚠️ بالرد على رسالة الشخص واكتب: فك كتم")
            return

        # 3. طرد العضو
        elif text in ["طرد", "برا"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.ban_member(target_user.id)
                    await chat.unban_member(target_user.id)
                    await message.reply_text(f"👢 تم طرد العضو ({target_user.first_name}) من المجموعة.")
                except Exception:
                    await message.reply_text("❌ لا أمتلك صلاحية طرد هذا الشخص (قد يكون مشرفاً مثلك).")
            else:
                await message.reply_text("⚠️ بالرد على رسالة الشخص واكتب: طرد")
            return

        # 4. حظر العضو
        elif text in ["حظر", "بان"]:
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                try:
                    await chat.ban_member(target_user.id)
                    await message.reply_text(f"🚫 تم حظر العضو ({target_user.first_name}) نهائياً.")
                except Exception:
                    await message.reply_text("❌ لا أمتلك صلاحية حظر هذا الشخص.")
            return

        # الردود السريعة
        elif text in ["طيف", "بوت"]:
            await message.reply_text("عيوني 🤍")
        elif text == "السلام عليكم":
            await message.reply_text("وعليكم السلام ورحمة الله وبركاته ✨")

def main():
    if not TOKEN:
        logger.error("خطأ: لم يتم العثور على التوكن!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("جاري تشغيل بوت طيف...")
    application.run_polling()

if __name__ == "__main__":
    main()
