import requests
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8181761121:AAEpxUwDBiE20uyQGXH-qb-ig4uFvndXTFs"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {}
    await update.message.reply_text("ENTER YOUR NID")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}

    # STEP 1: NID
    if "nid" not in user_data[chat_id]:
        user_data[chat_id]["nid"] = text
        await update.message.reply_text("ENTER DOB (YYYY-MM-DD)")
        return

    # STEP 2: DOB
    if "dob" not in user_data[chat_id]:
        user_data[chat_id]["dob"] = text

        nid = user_data[chat_id]["nid"]
        dob = user_data[chat_id]["dob"]

        url = (
            "https://idevelopingsolutions.com/hosts/"
            "61d550e291b4bddc_nidbodtoname.php"
            f"?nid={nid}&dob={dob}"
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.5993.90 Safari/537.36"
            ),
            "Accept": "application/json, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        data = None

        # Retry 3 times
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=60)
                response.raise_for_status()
                data = response.json()
                break
            except Exception:
                if attempt < 2:
                    time.sleep(2)
                else:
                    await update.message.reply_text(
                        "⚠️ API server not responding. Try again later."
                    )
                    user_data.pop(chat_id, None)
                    return

        if data and data.get("status") == "success":
            msg = (
                "<b>✅ NID INFORMATION</b>\n\n"
                f"🆔 <b>NID:</b> <code>{data.get('nid')}</code>\n"
                f"📅 <b>DOB:</b> <code>{data.get('date_of_birth')}</code>\n"
                f"👤 <b>Name:</b> {data.get('name')}\n"
                f"📱 <b>Bank Mobile:</b> <code>{data.get('bank_mobile')}</code>\n"
                f"👑 <b>Owner:</b> @CYBER_X_OF_BANGLADESHS"
            )
        else:
            msg = "❌ Data Not Found!"

        await update.message.reply_text(msg, parse_mode="HTML")
        user_data.pop(chat_id, None)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
