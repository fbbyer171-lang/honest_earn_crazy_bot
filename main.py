import random
import string
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ১. স্টার্ট কমান্ড ও মেইন মেনু
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ২. টেক্সট মেসেজ হ্যান্ডলার
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🚀 Start Work":
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("🔑 2FA $0.050", callback_data="task_fb_2fa")],
            [InlineKeyboardButton("🍪 Cookies $0.049", callback_data="task_fb_cookies")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_task")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📁 **Create Facebook Account**\nPlease select the type of account you want to create:", reply_markup=reply_markup, parse_mode="Markdown")
        
    elif text == "💰 Balance":
        await update.message.reply_text("💰 Your Current Balance: $0.90")
        
    elif text == "💸 Withdraw":
        keyboard = [
            [InlineKeyboardButton("🟡 Binance (BEP20)", callback_data="withdraw_binance_bep20")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "💳 **Withdrawal Section**\n\n"
            "• Minimum Withdraw: **$0.20** (20 Cents)\n"
            "• Select your payment method below:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif text == "👥 Referrals":
        user_id = update.effective_user.id
        ref_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        await update.message.reply_text(
            f"👥 **Referral Program**\n\n"
            f"Invite friends and earn a 20% lifetime commission on their task earnings!\n\n"
            f"🔗 Your Referral Link:\n`{ref_link}`\n\n"
            f"📊 Total Referrals: 12\n⏳ Pending Referrals: 12\n✅ Active Referrals: 0\n💰 Total Commission Earned: $0.000",
            parse_mode="Markdown"
        )
        
    elif text == "🏆 Leaderboard":
        await update.message.reply_text(
            "🏆 **Referral Earnings Leaderboard** 🏆\n\n"
            "1. 860****92 - $118.363\n"
            "2. 847****98 - $28.282\n"
            "3. 773****32 - $28.141\n"
            "4. 849****66 - $20.714\n"
            "5. 707****78 - $15.441"
        )
        
    elif text == "📊 Statistics":
        await update.message.reply_text(
            "📊 **Your Work Statistics**\n\n"
            "📝 Total Submitted: 43\n"
            "✅ Total Success: 28\n"
            "⏳ Review Pending: 3\n"
            "❌ Admin Rejected: 12\n"
            "🤖 Bot Rejected: 12\n\n"
            "*(Note: Pending and Admin reviews will be fully integrated soon!)*",
            parse_mode="Markdown"
        )
        
    elif text == "🎧 Support":
        keyboard = [[InlineKeyboardButton("💻 Admin Support", url="https://t.me/YourAdminUsername")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🎧 **Customer Support**\n\nFor any help, issues, or inquiries, please click the button below to contact our support admin:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif text == "❓ Help":
        keyboard = [[InlineKeyboardButton("💻 Support Admin", url="https://t.me/YourAdminUsername")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🤖 **How to use this bot?**\n"
            "1. Click **Work** to start doing tasks.\n"
            "2. Complete the tasks exactly as instructed to earn rewards.\n"
            "3. Check your **Balance** and request a **Withdraw** anytime!\n\n"
            "💡 **Need Help?**\nIf you don't understand a task, have any questions, or face issues with withdrawals, please contact our Support Admin below.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    else:
        current_step = context.user_data.get('step')
        task_type = context.user_data.get('task_type', '')
        
        # --- 2FA TASK FLOW ---
        if task_type == "2FA":
            if current_step == 'waiting_uid':
                context.user_data['submitted_uid'] = text
                context.user_data['step'] = 'waiting_proof'
                await update.message.reply_text(
                    "ID Please provide the Facebook UID:",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]])
                )
            elif current_step == 'waiting_proof':
                await update.message.reply_text(
                    "✅ Facebook Account Submitted!\nThe 2FA account has been securely logged.\n⏳ An admin will review it within 2-3 hours."
                )
                context.user_data.clear()

        # --- COOKIES TASK FLOW (সংশোধিত: প্রথমে কুকিজ, তারপর ইউআইডি) ---
        elif task_type == "Cookies":
            if current_step == 'waiting_cookies':
                context.user_data['submitted_cookies'] = text
                context.user_data['step'] = 'waiting_cookies_uid'
                await update.message.reply_text(
                    "🆔 Please provide the Facebook UID for this cookie:",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]])
                )
            elif current_step == 'waiting_cookies_uid':
                await update.message.reply_text(
                    "✅ Facebook Account (Cookies) Submitted Successfully!\n⏳ An admin will review it within 2-3 hours."
                )
                context.user_data.clear()

        # --- WITHDRAW FLOW ---
        elif current_step == 'waiting_bep20_address':
            wallet_addr = text
            await update.message.reply_text(
                f"✅ **Withdrawal Request Submitted!**\n\n"
                f"Network: Binance (BEP20)\n"
                f"Wallet: `{wallet_addr}`\n\n"
                f"⏳ Your payment will be processed within 24 hours.",
                parse_mode="Markdown"
            )
            context.user_data.clear()
            
        else:
            await update.message.reply_text("💡 Please use the menu buttons or type /start.")

# ৩. ইনলাইন বাটন হ্যান্ডলার
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "task_fb_2fa":
        context.user_data['step'] = 'waiting_uid'
        context.user_data['task_type'] = "2FA"
        
        text = (
            "📁 **Create Facebook Account (2FA)**\n\n"
            "👤 **Name:** Michael Fernandez\n"
            "🔑 **Password:** JjuXqZ7jVzCv\n\n"
            "1️⃣ Create a Facebook account using these details.\n"
            "2️⃣ Enable 2FA.\n"
            "3️⃣ Click the button below to provide your details."
        )
        keyboard = [
            [InlineKeyboardButton("🆔 Submit UID ➡️", callback_data="submit_uid_prompt")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_tasks")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_task")]
        ]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "task_fb_cookies":
        context.user_data['step'] = 'waiting_cookies'
        context.user_data['task_type'] = "Cookies"
        
        text = (
            "📁 **Create Facebook Account (Cookies Only)**\n\n"
            "👤 **Name:** Michael Fernandez\n"
            "🔑 **Password:** JjuXqZ7jVzCv\n\n"
            "1️⃣ Create a Facebook account using these details.\n"
            "2️⃣ Do NOT enable 2FA.\n"
            "3️⃣ Click the button below to provide your Account Cookies."
        )
        keyboard = [
            [InlineKeyboardButton("🍪 Submit Cookies ➡️", callback_data="submit_cookies_prompt")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_tasks")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_task")]
        ]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "submit_uid_prompt":
        await query.message.reply_text(
            "🔑 Please paste your Facebook 2FA Setup Key or details below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]])
        )

    elif data == "submit_cookies_prompt":
        await query.message.reply_text(
            "🍪 Please paste your Facebook Cookies below (Formats accepted: Netscape, JSON, or String):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]])
        )
        
    elif data == "back_to_tasks":
        keyboard = [
            [InlineKeyboardButton("🔑 2FA $0.050", callback_data="task_fb_2fa")],
            [InlineKeyboardButton("🍪 Cookies $0.049", callback_data="task_fb_cookies")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_task")]
        ]
        await query.message.reply_text("📁 **Create Facebook Account**\nPlease select the type of account you want to create:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "withdraw_binance_bep20":
        context.user_data['step'] = 'waiting_bep20_address'
        await query.message.reply_text(
            "🟡 **Binance (BEP20) Withdrawal**\n\n"
            "لطفاً আপনার **Binance USDT (BEP20)** ওয়ালেট অ্যাড্রেসটি চ্যাটে লিখে পাঠান:"
        )
        
    elif data == "cancel_task":
        context.user_data.clear()
        await query.message.reply_text("❌ Process Cancelled. Use the keyboard below to continue.")

def main():
    TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot is running perfectly...")
    application.run_polling()

if __name__ == "__main__":
    main()
