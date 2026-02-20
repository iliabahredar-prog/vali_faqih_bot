import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# --- اطلاعات حساس ---
TOKEN = "7575731084:AAF81FrFiT3wX5NtpMY2IumKhZ2Djq_7ajk"  # توکن جدید
GOOGLE_API_KEY = "AIzaSyBXDBwM4EsrLDR2MpXR4-qHByGD5Oddxes"
CREATOR_ID = 1843464942  # حتماً بعداً این را به آیدی خودت تغییر بده

# تنظیمات هوش مصنوعی
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# حافظه برای ادمین‌ها و جو گروه
admins = {CREATOR_ID}
history = []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    if not text: return
    bot_info = await context.bot.get_me()

    # ذخیره در حافظه فعال
    history.append(f"{user.first_name}: {text}")
    if len(history) > 15: history.pop(0)

    # شروط پاسخگویی
    is_admin = user.id in admins
    is_tagged = f"@{bot_info.username}" in text
    is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == bot_info.id

    if is_admin or is_tagged or is_reply:
        prompt = (
            f"نام تو 'ولی فقیه' است. سازنده تو شخصی با آیدی {CREATOR_ID} است. "
            f"در ابتدا رسمی باش، اما کم‌کم با توجه به این چت‌ها لحنت را شبیه گروه کن: {' | '.join(history)}. "
            f"همیشه حقیقت را بگو و به سازنده وفادار باش. به این پیام پاسخ بده: {text}"
        )
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)

async def set_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == CREATOR_ID:
        if update.message.reply_to_message:
            new_id = update.message.reply_to_message.from_user.id
            admins.add(new_id)
            await update.message.reply_text(f"✅ کاربر {new_id} به عنوان مدیر تایید شد.")
        else:
            await update.message.reply_text("❌ روی پیام طرف ریپلای کن.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("set_admin", set_admin))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
