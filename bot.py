import os
import json
import asyncio
import random
import string
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATA_FILE = "posts.json"

app = Flask(__name__)
tg_app = Application.builder().token(BOT_TOKEN).build()

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def gen_code(n=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        code = context.args[0]
        data = load_data()
        if code not in data:
            await update.message.reply_text("❌ Invalid link.")
            return

        post = data[code]
        msg = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=post["chat_id"],
            message_id=post["message_id"],
        )
        await update.message.reply_text("⏳ This post will delete in 5 minutes.")
        await asyncio.sleep(300)
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
            )
        except:
            pass
    else:
        await update.message.reply_text(
            "👋 Welcome!\n\nLink se post milegi.\nPost 5 minutes me delete ho jaayegi ⏳"
        )

tg_app.add_handler(CommandHandler("start", start))

# Listen posts from private group/channel
@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    tg_app.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running 🚀"

async def main():
    await tg_app.initialize()
    await tg_app.start()

if __name__ == "__main__":
    asyncio.run(main())
