from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚀 Start Work", "💰 Balance"],
        ["💸 Withdraw", "👥 Referrals"],
        ["🏆 Leaderboard", "📊 Statistics"],
        ["🎧 Support", "❓ Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    user_name = update.effective_user.first_name
    welcome_text = f"Hello, {user_name}! 👋\n\nWelcome back to the Task Bot. 🌟\nPlease choose an option from the menu below:"
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🚀 Start Work":
        keyboard = [
            [InlineKeyboardButton("📁 Create FB Account ($0.050)", callback_data="fb_normal")],
            [InlineKeyboardButton("📁 Create FB With Gmail ($0.090)", callback_data="fb_gmail")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📌 Select an account type to create:", reply_markup=reply_markup)
        
    elif text == "💰 Balance":
        await update.message.reply_text("👤 Your Current Balance: $0.000\n✨ Complete tasks to earn more!")
        
    elif text == "💸 Withdraw":
        await update.message.reply_text("💳 Minimum withdraw is $1.00.\nلطفا your payment method select koro (e.g., bKash/Nagad).")

def main():
    TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
