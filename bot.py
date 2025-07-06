
import pytesseract
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = '7699253029:AAFuXi7SNdfl0EUFwr9TlZgl2drxVyZppdE'
OWNER_ID = 7775062794

# In-memory user access storage
user_access = {}

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_access(user_id):
        await update.message.reply_text("⛔ Access Denied.\nContact the owner to get access for 30 days.")
    else:
        await update.message.reply_text("✅ Access Granted!\nSend your CoC account screenshot to generate a title.")

# Command: /approve <user_id>
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    try:
        uid = int(context.args[0])
        user_access[uid] = datetime.now() + timedelta(days=30)
        await update.message.reply_text(f"✅ Approved user {uid} for 30 days.")
    except:
        await update.message.reply_text("❌ Invalid user ID.")

# Check if user has access
def check_access(user_id):
    if user_id not in user_access:
        return False
    return datetime.now() <= user_access[user_id]

# OCR + Caption generation
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_access(user_id):
        await update.message.reply_text("⛔ Access Denied.\nPlease contact the owner to get access.")
        return

    file = await update.message.photo[-1].get_file()
    image_data = requests.get(file.file_path).content
    image = Image.open(BytesIO(image_data))

    text = pytesseract.image_to_string(image)
    title = generate_title(text)
    await update.message.reply_text(title)

# Text title generation
def generate_title(text):
    th = "TH??"
    for level in range(16, 9, -1):
        if f"TH{level}" in text:
            th = f"TH{level}"
            break

    hero_lvls = "??-??-??-??-??"
    war_stars = "???"
    cwl = "???"

    if "War Stars Won" in text:
        war_stars = text.split("War Stars Won")[1].split()[0]
    if "League Shop" in text:
        cwl = "800"

    return (
        f"💥CRAZY DEAL 🤝 MAXED WALL {th} ACC ✨\n"
        f"🎊 EPIC EQUIPMENTS UNLOCKED 💪\n"
        f"🎖️ HERO LEVELS: {hero_lvls}\n"
        f"🎭 WAR STARS: {war_stars} ⭐ CWL MEDALS: {cwl}\n"
        f"🎉 INSTANT DELIVERY 🚚"
    )

# Run bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
