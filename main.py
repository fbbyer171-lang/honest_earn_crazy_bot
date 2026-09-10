import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['🚀 Start Work'],
        ['💰 Balance', '💸 Withdraw'],
        ['👥 Referrals', '🏆 Leaderboard'],
        ['📊 Statistics', '🎧 Support'],
        ['❓ Help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Welcome to Honest Crazy Earn Bot!", reply_markup=reply_markup)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if name == 'main':
    main()
