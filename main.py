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
        # এখানে একাধিক টাস্ক ক্যাটাগরির বাটনগুলো তৈরি করা হয়েছে
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
        await update.message.reply_text("💳 Minimum withdraw is $1.00.\nPlease select your payment method (bKash/Nagad).")
        
    else:
        current_step = context.user_data.get('step')
        task_type = context.user_data.get('task_type', 'Task')
        
        if current_step == 'waiting_uid':
            context.user_data['submitted_uid'] = text
            context.user_data['step'] = 'waiting_proof'
            
            if "Cookies" in task_type:
                await update.message.reply_text("✅ UID Saved.\n\n🍪 Now please paste the Facebook Cookies:")
            elif "2FA" in task_type:
                await update.message.reply_text("✅ UID Saved.\n\n🔑 Now please send the 2FA Secret Key:")
            else:
                await update.message.reply_text("✅ UID Saved.\n\n📌 Now please send your account link or proof:")
            
        elif current_step == 'waiting_proof':
            proof_data = text
            user_uid = context.user_data.get('submitted_uid', 'N/A')
            
            await update.message.reply_text("⏳ Verifying your submission... Please wait.")
            
            if len(proof_data) > 5:  
                await update.message.reply_text(f"✅ {task_type} Verified Successfully!\n🎉 UID: {user_uid}\nReward added to your pending balance.")
            else:
                await update.message.reply_text("❌ Invalid data provided! Task rejected.")
                
            context.user_data.clear()
        else:
            await update.message.reply_text("💡 Please use the menu buttons below or type /start.")

# ৩. ইনলাইন বাটন হ্যান্ডলার (ক্যাটাগরি হ্যান্ডেল করার জন্য)
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data in ["task_fb_cookies", "task_fb_2fa", "task_instagram"]:
        rand_name = f"User_{random.randint(1000, 9999)}"
        rand_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        task_names = {
            "task_fb_cookies": "Facebook Cookies",
            "task_fb_2fa": "Facebook 2FA",
            "task_instagram": "Instagram Account"
        }
        
        current_task_name = task_names.get(data, "Task")
        
        context.user_data['step'] = 'waiting_uid'
        context.user_data['task_type'] = current_task_name
        context.user_data['temp_name'] = rand_name
        context.user_data['temp_pass'] = rand_pass
        
        text = (
            f"📂 **{current_task_name} Task**\n\n"
            f"👤 **Details / Name:** {rand_name}\n"
            f"🔑 **Password:** {rand_pass}\n\n"
            f"1️⃣ Complete the task using these details.\n"
            f"2️⃣ Send your account UID in chat right now."
        )
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "cancel_task":
        context.user_data.clear()
        await query.message.edit_text("❌ Task process cancelled. Click /start to go back.")

def main():
    TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot is running with multi-category task support...")
    application.run_polling()

if __name__ == "__main__":
    main()
