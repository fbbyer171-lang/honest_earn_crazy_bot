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
            [InlineKeyboardButton("📁 Create FB Account (Cookies Only)", callback_data="task_fb_cookies")],
            [InlineKeyboardButton("🔐 Facebook 2FA Task", callback_data="task_fb_2fa")],
            [InlineKeyboardButton("📸 Instagram Account Task", callback_data="task_instagram")],
            [InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_task")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📌 Select a task category below:", reply_markup=reply_markup)
        
    elif text == "💰 Balance":
        await update.message.reply_text("👤 Your Current Balance: $0.000\n✨ Complete tasks to earn more!")
        
    elif text == "💸 Withdraw":
        keyboard = [
            [InlineKeyboardButton("🟡 Binance (BEP20)", callback_data="withdraw_binance_bep20")],
            [InlineKeyboardButton("🇧🇩 bKash / Nagad", callback_data="withdraw_bka_nag")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "💳 **Withdrawal Section**\n\n"
            "• Minimum Withdraw: **$0.20** (20 Cents)\n"
            "• Select your preferred payout method below:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif text == "👥 Referrals":
        user_id = update.effective_user.id
        ref_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        await update.message.reply_text(f"👥 **Referral Program**\n\n🔗 Your Referral Link:\n`{ref_link}`", parse_mode="Markdown")
        
    elif text == "🏆 Leaderboard":
        await update.message.reply_text("🏆 **Top Earners Leaderboard**\n1. User_9821 - $15.500\n2. User_4312 - $12.000")
        
    elif text == "📊 Statistics":
        await update.message.reply_text("📊 **Bot Statistics**\n👥 Total Users: 1,420\n✅ Completed Tasks: 3,890")
        
    elif text == "🎧 Support":
        await update.message.reply_text("🎧 Contact Admin for support: @AdminUsername")
        
    elif text == "❓ Help":
        await update.message.reply_text("❓ Select 'Start Work', choose a category, and submit your UID & proof.")
        
    else:
        current_step = context.user_data.get('step')
        task_type = context.user_data.get('task_type', 'Task')
        
        if current_step == 'waiting_uid':
            context.user_data['submitted_uid'] = text
            context.user_data['step'] = 'waiting_proof'
            await update.message.reply_text(f"✅ UID Saved: {text}\n\n📥 Now please send your proof / data for {task_type}:")
            
        elif current_step == 'waiting_proof':
            proof_data = text
            user_uid = context.user_data.get('submitted_uid', 'N/A')
            
            await update.message.reply_text("⏳ Verifying your submission...")
            if len(proof_data) > 3:
                await update.message.reply_text(f"✅ Task Completed Successfully!\n🎉 UID: {user_uid}\nReward added.")
            else:
                await update.message.reply_text("❌ Invalid proof! Try again.")
            context.user_data.clear()
            
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
    
    if data in ["task_fb_cookies", "task_fb_2fa", "task_instagram"]:
        rand_name = f"User_{random.randint(1000, 9999)}"
        rand_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        task_names = {
            "task_fb_cookies": "Facebook Cookies",
            "task_fb_2fa": "Facebook 2FA",
            "task_instagram": "Instagram Account"
        }
        current_task_name = task_names.get(data, "Task")
        
        context.user_data['step'] = 'waiting_uid'
        context.user_data['task_type'] = current_task_name
        
        text = (
            f"📂 **{current_task_name}**\n\n"
            f"👤 **Name:** {rand_name}\n"
            f"🔑 **Pass:** {rand_pass}\n\n"
            f"👇 **এখন আপনার অ্যাকাউন্টের UID চ্যাটে লিখে পাঠান:**"
        )
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "withdraw_binance_bep20":
        context.user_data['step'] = 'waiting_bep20_address'
        await query.message.reply_text(
            "🟡 **Binance (BEP20) Withdrawal**\n\n"
            "আপনার **Binance USDT (BEP20)** ওয়ালেট অ্যাড্রেসটি চ্যাটে লিখে পাঠান:"
        )
        
    elif data == "withdraw_bka_nag":
        await query.message.reply_text("🇧🇩 bKash / Nagad withdrawal is coming soon. Please use Binance BEP20 for now.")
        
    elif data == "cancel_task":
        context.user_data.clear()
        await query.message.reply_text("❌ Process cancelled. Type /start to go back.")

def main():
    TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot is running with Binance BEP20 support...")
    application.run_polling()

if __name__ == "__main__":
    main()
