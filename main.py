import os
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context) -> None:
    await update.message.reply_text("Welcome to Honest Crazy Earn Bot!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
