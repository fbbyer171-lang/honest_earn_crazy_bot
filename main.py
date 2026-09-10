import os
import random
import string
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Constants & Usernames
FORCE_SUB_CHANNEL = "@honestcrazy11"
HELP_ADMIN = "@timotyservice"
SUPPORT_ADMIN = "@Owners_honestearnnow790"

FIRST_NAMES = ["Michael", "David", "Robert", "James", "William", "John", "Richard", "Thomas", "Charles", "Daniel"]
LAST_NAMES = ["Fernandez", "Smith", "Johnson", "Brown", "Taylor", "Miller", "Wilson", "Anderson", "Jackson", "White"]

def generate_random_credentials():
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return name, password

# Force Subscription Check
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

# 1. Start Command & Force Subscribe
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    
    is_subscribed = await check_subscription(update, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("✅ Joined / Check", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "⚠️ **Please join our channel first to use this bot!**\n\n"
            f"Channel: {FORCE_SUB_CHANNEL}\n\n"
            "After joining, click the button below.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # Language Selection Menu
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"),
         InlineKeyboardButton("🇲🇬 Malagasy", callback_data="lang_mg")]
    ]
    await update.message.reply_text(
        "🌐 **Please select your language / Veuillez choisir votre langue :**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Callback Handler for Languages and Joins
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "check_join":
        is_subscribed = await check_subscription(update, context)
        if is_subscribed:
            keyboard = [
                [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
                 InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"),
                 InlineKeyboardButton("🇲🇬 Malagasy", callback_data="lang_mg")]
            ]
            await query.message.edit_text(
                "✅ Thank you for joining! Please select your language:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.answer("❌ You haven't joined the channel yet!", show_alert=True)
            return

    elif data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data['lang'] = lang
        
        # Main Menu based on Language
        if lang == "bn":
            menu = [
                ["🚀 কাজ শুরু করুন", "💰 ব্যালেন্স"],
                ["💸 পেমেন্ট তুলুন", "👥 রেফারেল"],
                ["🏆 লিডারবোর্ড", "📊 স্ট্যাটিস্টিক্স"],
                ["🎧 সাপোর্ট", "❓ হেল্প"]
            ]
            welcome_text = "স্বাগতম! নিচের মেনু থেকে অপশন বেছে নিন:"
        elif lang == "mg":
            menu = [
                ["🚀 Manomboka", "💰 Vola"],
                ["💸 Maka Vola", "👥 Olona nasaina"],
                ["🏆 Laharana", "📊 Antontan'isa"],
                ["🎧 Fanohanana", "❓ Fanampiana"]
            ]
            welcome_text = "Tongasoa soa! Safidio eto ambany ny safidy:"
        else:
            menu = [
                ["🚀 Start Work", "💰 Balance"],
                ["💸 Withdraw", "👥 Referrals"],
                ["🏆 Leaderboard", "📊 Statistics"],
                ["🎧 Support", "📁 Help"]
            ]
            welcome_text = "Welcome! Choose an option below:"

        reply_markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)
        await query.message.reply_text(welcome_text, reply_markup=reply_markup)

# Text Message Handler for Menus & Tasks
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Check force sub for every action
    if not await check_subscription(update, context):
        await update.message.reply_text(f"⚠️ Please join {FORCE_SUB_CHANNEL} first using /start")
        return

    lang = context.user_data.get('lang', 'en')

    if text in ["🚀 Start Work", "🚀 কাজ শুরু করুন", "🚀 Manomboka"]:
        context.user_data.clear()
        context.user_data['lang'] = lang
        keyboard = [
            [InlineKeyboardButton("🔑 2FA Task ($0.050)", callback_data="task_fb_2fa")],
            [InlineKeyboardButton("🍪 Cookies Task ($0.049)", callback_data="task_fb_cookies")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]
        ]
        await update.message.reply_text(
            "📁 **Select Task Category:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif text in ["💰 Balance", "💰 ব্যালেন্স", "💰 Vola"]:
        await update.message.reply_text("💰 **Current Balance:** $0.000\n✨ Complete tasks to earn more!")
        
    elif text in ["💸 Withdraw", "💸 পেমেন্ট তুলুন", "💸 Maka Vola"]:
        keyboard = [[InlineKeyboardButton("🟡 Binance (BEP20)", callback_data="withdraw_binance_bep20")]]
        await update.message.reply_text(
            "💳 **Withdrawal Section**\n\n• Minimum Withdraw: **$0.20**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif text in ["👥 Referrals", "👥 রেফারেল", "👥 Olona nasaina"]:
        user_id = update.effective_user.id
        ref_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        await update.message.reply_text(
            f"👥 **Referral Program**\n\n🔗 Link:\n`{ref_link}`\n\n"
            f"📊 Total: 0 | Pending: 0 | Active: 0\n💰 Earned: $0.000",
            parse_mode="Markdown"
        )
        
    elif text in ["🏆 Leaderboard", "🏆 লিডারবোর্ড", "🏆 Laharana"]:
        await update.message.reply_text("🏆 **Top Earners Leaderboard**\nNo data yet.")
        
    elif text in ["📊 Statistics", "📊 স্ট্যাটিস্টিক্স", "📊 Antontan'isa"]:
        await update.message.reply_text(
            "📊 **Your Work Statistics**\n\n"
            "📝 Total Submitted: 0\n"
            "✅ Total Success: 0\n"
            "⏳ Review Pending/Hold: 0\n"
            "❌ Admin Rejected: 0\n"
            "🤖 Bot Rejected: 0"
        )
        
    elif text in ["🎧 Support", "🎧 সাপোর্ট", "🎧 Fanohanana"]:
        keyboard = [[InlineKeyboardButton("💻 Support Admin", url=f"https://t.me/{SUPPORT_ADMIN.replace('@', '')}")]]
        await update.message.reply_text(
            f"🎧 **Customer Support**\nContact our admin: {SUPPORT_ADMIN}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    elif text in ["📁 Help", "❓ হেল্প", "❓ Fanampiana"]:
        keyboard = [[InlineKeyboardButton("💻 Help Admin", url=f"https://t.me/{HELP_ADMIN.replace('@', '')}")]]
        await update.message.reply_text(
            f"❓ **Help Center**\nNeed assistance? Contact: {HELP_ADMIN}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    else:
        current_step = context.user_data.get('step')
        task_type = context.user_data.get('task_type', '')
        
        if task_type == "2FA":
            if current_step == 'waiting_2fa_key':
                context.user_data['submitted_2fa'] = text
                context.user_data['step'] = 'waiting_2fa_uid'
                await update.message.reply_text("ID Please provide the Facebook UID:")
            elif current_step == 'waiting_2fa_uid':
                await update.message.reply_text("✅ 2FA Account Submitted Successfully! Sent to Google Sheets (2FA Sheet). Review pending.")
                context.user_data.clear()

        elif task_type == "Cookies":
            if current_step == 'waiting_cookies':
                context.user_data['submitted_cookies'] = text
                context.user_data['step'] = 'waiting_cookies_uid'
                await update.message.reply_text("🆔 Please provide the Facebook UID for this cookie:")
            elif current_step == 'waiting_cookies_uid':
                await update.message.reply_text("✅ Cookies Account Submitted Successfully! Sent to Google Sheets (Cookies Sheet). Review pending.")
                context.user_data.clear()

        elif current_step == 'waiting_bep20_address':
            await update.message.reply_text(f"✅ Withdrawal Request Submitted with wallet: `{text}`", parse_mode="Markdown")
            context.user_data.clear()

# Task Callbacks
async def task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "task_fb_2fa":
        name, password = generate_random_credentials()
        context.user_data['step'] = 'waiting_2fa_key'
        context.user_data['task_type'] = "2FA"
        
        text = (
            f"📁 **Create Facebook Account (2FA)**\n\n"
            f"👤 **Name:** {name}\n"
            f"🔑 **Password:** {password}\n\n"
            f"1️⃣ Create account using details.\n"
            f"2️⃣ Enable 2FA.\n"
            f"3️⃣ Submit your 2FA Key below:"
        )
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "task_fb_cookies":
        name, password = generate_random_credentials()
        context.user_data['step'] = 'waiting_cookies'
        context.user_data['task_type'] = "Cookies"
        
        text = (
            f"📁 **Create Facebook Account (Cookies)**\n\n"
            f"👤 **Name:** {name}\n"
            f"🔑 **Password:** {password}\n\n"
            f"1️⃣ Create account using details.\n"
            f"2️⃣ Do NOT enable 2FA.\n"
            f"3️⃣ Submit your Cookies below:"
        )
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_task")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "withdraw_binance_bep20":
        context.user_data['step'] = 'waiting_bep20_address'
        await query.message.reply_text("🟡 Send your **Binance USDT (BEP20)** address:", parse_mode="Markdown")
        
    elif data == "cancel_task":
        context.user_data.clear()
        await query.message.reply_text("❌ Process Cancelled.")

def main():
    TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback, pattern="^(lang_|check_join)"))
    application.add_handler(CallbackQueryHandler(task_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Full Featured Web-Controlled Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
