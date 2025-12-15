import os
import uuid
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PRIVATE_GROUP_ID = int(os.getenv("PRIVATE_GROUP_ID"))

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# store post_id -> message_id
POSTS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "👋 Welcome!\n\nLink se aaye ho to post milegi."
        )
        return

    code = args[0]
    if code not in POSTS:
        await update.message.reply_text("❌ Link expired ya invalid.")
        return

    msg_id = POSTS[code]
    sent = await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=PRIVATE_GROUP_ID,
        message_id=msg_id
    )

    await update.message.reply_text("⏳ Ye post 5 minute baad delete ho jayegi.")

    await asyncio.sleep(300)
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=sent.message_id
        )
    except:
        pass


async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != PRIVATE_GROUP_ID:
        return

    code = str(uuid.uuid4())[:8]
    POSTS[code] = update.message.message_id

    link = f"https://t.me/{context.bot.username}?start={code}"
    await context.bot.send_message(
        chat_id=PRIVATE_GROUP_ID,
        text=f"🔗 Link generated:\n{link}"
    )


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"


@app.route("/")
def home():
    return "Bot is running"


async def main():
    await application.initialize()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CommandHandler("post", handle_post)
    )
    await application.start()

if __name__ == "__main__":
    asyncio.run(main())
