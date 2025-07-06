
import pytesseract
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
OWNER_ID = 7775062794

user_access = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_access(user_id):
        await update.message.reply_text("⛔ Access Denied.\nContact the owner to get 30-day access.")
    else:
        await update.message.reply_text("✅ Access Granted! Send a CoC image to generate a cool title.")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized to approve users.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    try:
        uid = int(context.args[0])
        user_access[uid] = datetime.now() + timedelta(days=30)
        await update.message.reply_text(f"✅ Approved user {uid} for 30 days.")
    except:
        await update.message.reply_text("❌ Invalid user ID format.")

def check_access(user_id):
    if user_id == OWNER_ID:
        return True
    expiry = user_access.get(user_id)
    return expiry and datetime.now() <= expiry

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_access(user_id):
        await update.message.reply_text("⛔ Access Denied.\nPlease contact the owner to get access.")
        return

    file = await update.message.photo[-1].get_file()
    image_data = requests.get(file.file_path).content
    image = Image.open(BytesIO(image_data))

    text = pytesseract.image_to_string(image)
    print(f"\nExtracted OCR Text:\n{text}\n")

    title = generate_title(text)
    await update.message.reply_text(title)

def generate_title(text):
    th = "TH??"
    for level in range(16, 9, -1):
        if f"TH{level}" in text:
            th = f"TH{level}"
            break

    hero_lvls = "54-59-43-28-25"
    war_stars = "900" if "War Stars" in text else "???"
    cwl = "800" if "League Shop" in text else "???"

    return (
        f"💥CRAZY DEAL 🤝 MAXED WALL {th} ACC ✨\n"
        f"🎊 SEVEN EPIC EQUIPMENTS 💪\n"
        f"🎖️ HERO LEVELS: {hero_lvls}\n"
        f"🎭 WAR STARS: {war_stars} ⭐ CWL MEDALS: {cwl}\n"
        f"🎉 INSTANT DELIVERY 🚚"
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
