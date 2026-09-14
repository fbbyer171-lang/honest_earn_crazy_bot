import os
import telebot
from telebot import types
import random

TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# আপনার টেলিগ্রাম চ্যাট আইডি এখানে সেট করা হলো
ADMIN_CHAT_ID = 8856278248

# User Data Storage
user_data = {}

def get_user(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {
            "balance": 0.00,
            "total_submitted": 0,
            "total_success": 0,
            "review_pending": 0,
            "admin_rejected": 0,
            "bot_rejected": 0,
            "referrals": 0,
            "ref_earnings": 0.00,
            "state": None,
            "sub_state": None,
            "task_data": {},
            "withdraw_method": None
        }
    return user_data[chat_id]

# Random Generator Helpers
FIRST_NAMES = ["Michael", "David", "John", "Robert", "William", "James", "Alex", "Daniel", "Chris", "Thomas"]
LAST_NAMES = ["Fernandez", "Smith", "Johnson", "Brown", "Taylor", "Miller", "Wilson", "Anderson", "Thomas", "Jackson"]

def generate_random_credentials():
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
    password = "".join(random.choice(chars) for _ in range(12))
    return name, password

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    get_user(chat_id)
    
    welcome_text = (
        f"স্বাগতম, *{user_name}*! 🎉\n\n"
        "আমাদের ইানিং ও অ্যাকাউন্ট বাইয়িং বটে আপনাকে স্বাগতম। নিচে দেওয়া অপশনগুলো থেকে আপনার পছন্দের সেবাটি বেছে নিন:"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_earn = types.KeyboardButton("🚀 Start Work")
    btn_balance = types.KeyboardButton("💰 Balance")
    btn_withdraw = types.KeyboardButton("💸 Withdraw")
    btn_ref = types.KeyboardButton("👥 Referrals")
    btn_leaderboard = types.KeyboardButton("🏆 Leaderboard")
    btn_stats = types.KeyboardButton("📊 Statistics")
    btn_support = types.KeyboardButton("🎧 Support")
    btn_help = types.KeyboardButton("📁 Help")
    
    markup.add(btn_earn, btn_balance, btn_withdraw, btn_ref, btn_leaderboard, btn_stats, btn_support, btn_help)
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    chat_id = message.chat.id
    if ADMIN_CHAT_ID and chat_id != ADMIN_CHAT_ID:
        bot.send_message(chat_id, "❌ আপনি এই কমান্ড ব্যবহার করার জন্য অনুমোদিত নন।")
        return
    
    admin_text = (
        "🛠 *Admin Panel*\n\n"
        "স্বাগতম অ্যাডমিন! ইউজারদের সমস্ত টাস্ক সাবমিশন ও উইথড্র রিকুয়েস্ট এই চ্যাটে রিয়েল-টাইমে চলে আসবে।"
    )
    bot.send_message(chat_id, admin_text)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    user = get_user(chat_id)
    state = user.get("state")
    
    # 1. Facebook 2FA Task Flow (2FA Key -> UID)
    if state == "waiting_for_fb_2fa_key":
        user["task_data"]["2fa_key"] = text
        user["state"] = "waiting_for_fb_2fa_uid"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_process"))
        bot.send_message(chat_id, "🆔 Please provide your Facebook UID (Report Time: 30 minutes):", reply_markup=markup)
        return
        
    elif state == "waiting_for_fb_2fa_uid":
        user["task_data"]["uid"] = text
        user["state"] = None
        user["total_submitted"] += 1
        user["review_pending"] += 1
        user["balance"] += 0.05
        
        # Notify Admin
        if ADMIN_CHAT_ID:
            admin_msg = (
                f"🔔 *New Facebook 2FA Task Submitted!*\n\n"
                f"👤 User ID: `{chat_id}`\n"
                f"🔑 2FA Key: `{user['task_data'].get('2fa_key')}`\n"
                f"🆔 UID: `{text}`"
            )
            bot.send_message(ADMIN_CHAT_ID, admin_msg)

        bot.send_message(chat_id, "✅ *Facebook 2FA Task Submitted Successfully!*\n⏳ Report time: within 30 minutes.")
        return

    # 2. Facebook Cookies Task Flow (UID -> Cookies String)
    elif state == "waiting_for_fb_cookies_uid":
        user["task_data"]["uid"] = text
        user["state"] = "waiting_for_fb_cookies_string"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_process"))
        bot.send_message(chat_id, "🍪 Please paste your Facebook Cookies string/JSON (Report Time: 30 minutes):", reply_markup=markup)
        return

    elif state == "waiting_for_fb_cookies_string":
        user["task_data"]["cookies"] = text
        user["state"] = None
        user["total_submitted"] += 1
        user["review_pending"] += 1
        user["balance"] += 0.049
        
        # Notify Admin
        if ADMIN_CHAT_ID:
            admin_msg = (
                f"🔔 *New Facebook Cookies Task Submitted!*\n\n"
                f"👤 User ID: `{chat_id}`\n"
                f"🆔 UID: `{user['task_data'].get('uid')}`\n"
                f"🍪 Cookies: `{text}`"
            )
            bot.send_message(ADMIN_CHAT_ID, admin_msg)

        bot.send_message(chat_id, "✅ *Facebook Cookies Task Submitted Successfully!*\n⏳ Report time: within 30 minutes.")
        return

    # 3. Instagram 2FA Task Flow
    elif state == "waiting_for_ig_2fa":
        user["task_data"]["ig_2fa"] = text
        user["state"] = None
        user["total_submitted"] += 1
        user["review_pending"] += 1
        user["balance"] += 0.045
        
        # Notify Admin
        if ADMIN_CHAT_ID:
            admin_msg = (
                f"🔔 *New Instagram 2FA Task Submitted!*\n\n"
                f"👤 User ID: `{chat_id}`\n"
                f"🔑 IG 2FA Key: `{text}`"
            )
            bot.send_message(ADMIN_CHAT_ID, admin_msg)

        bot.send_message(chat_id, "✅ *Instagram 2FA Task Submitted Successfully!*\n⏳ Report time: within 30 minutes.")
        return

    # 4. Withdraw Details Input Flow
    elif state == "waiting_for_withdraw_details":
        method = user.get("withdraw_method", "Unknown")
        amount = user["balance"]
        user["state"] = None
        user["balance"] = 0.0  # Balance reset after withdrawal request
        
        # Notify Admin
        if ADMIN_CHAT_ID:
            admin_msg = (
                f"💸 *New Withdrawal Request!*\n\n"
                f"👤 User ID: `{chat_id}`\n"
                f"💳 Method: `{method}`\n"
                f"💰 Amount: `${amount:.2f}`\n"
                f"📋 Account Details: `{text}`"
            )
            bot.send_message(ADMIN_CHAT_ID, admin_msg)

        bot.send_message(chat_id, f"✅ আপনার পেমেন্ট রিকুয়েস্ট সফলভাবে সাবমিট হয়েছে! খুব শীঘ্রই পেমেন্ট পাঠিয়ে দেওয়া হবে।")
        return

    # Normal Menu Handling
    if text == "💰 Balance":
        bot.send_message(chat_id, f"💰 Your Current Balance: *${user['balance']:.2f}*")
        
    elif text == "🚀 Start Work":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_fb = types.InlineKeyboardButton("📘 1. Facebook Task", callback_data="task_facebook_menu")
        btn_ig = types.InlineKeyboardButton("📸 2. Instagram Task", callback_data="task_instagram_menu")
        btn_gmail = types.InlineKeyboardButton("✉️ 3. Gmail Task", callback_data="task_gmail_menu")
        markup.add(btn_fb, btn_ig, btn_gmail)
        bot.send_message(chat_id, "🚀 *Select a Category to Start Working:*", reply_markup=markup)
        
    elif text == "💸 Withdraw":
        if user["balance"] < 0.20:
            bot.send_message(chat_id, "⚠️ উইথড্র করার জন্য আপনার পর্যাপ্ত ব্যালেন্স নেই। ন্যূনতম ব্যালেন্স হতে হবে **$0.20 (20 সেন্ট)**।")
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("💳 Bkash", callback_data="withdraw_bkash"),
                types.InlineKeyboardButton("🟡 Binance", callback_data="withdraw_binance"),
                types.InlineKeyboardButton("🔗 BEP20 Address", callback_data="withdraw_bep20"),
                types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")
            )
            bot.send_message(chat_id, f"💸 *Withdrawal Menu*\nYour Balance: *${user['balance']:.2f}*\nPlease select your payout method:", reply_markup=markup)
        
    elif text == "👥 Referrals":
        ref_link = f"https://t.me/YourBotUsername?start={message.from_user.id}"
        ref_text = (
            "👥 *Referral Program*\n\n"
            "Invite friends and earn a **20% lifetime commission** on their task earnings!\n\n"
            f"🔗 *Your Referral Link:*\n`{ref_link}`\n\n"
            f"📊 Total Referrals: {user['referrals']}\n"
            f"💰 Total Commission Earned: ${user['ref_earnings']:.3f}"
        )
        bot.send_message(chat_id, ref_text)
        
    elif text == "🏆 Leaderboard":
        lb_text = (
            "🏆 *Referral Earnings Leaderboard* 🏆\n\n"
            "কোনো রেফারাল ডাটা পাওয়া যায়নি।"
        )
        bot.send_message(chat_id, lb_text)
        
    elif text == "📊 Statistics":
        stats_text = (
            "📊 *Your Work Statistics*\n\n"
            f"📝 Total Submitted: {user['total_submitted']}\n"
            f"✅ Total Success: {user['total_success']}\n"
            f"⏳ Review Pending: {user['review_pending']}\n"
            f"❌ Admin Rejected: {user['admin_rejected']}\n"
            f"🤖 Bot Rejected: {user['bot_rejected']}\n\n"
            "_Note: Report time for tasks is within 30 minutes._"
        )
        bot.send_message(chat_id, stats_text)
        
    elif text == "🎧 Support":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🧑‍💻 Admin Support", url="https://t.me/sacrifice_no"))
        support_text = (
            "🎧 *Customer Support*\n\n"
            "For any help, issues, or inquiries, please click the button below to contact our support admin:"
        )
        bot.send_message(chat_id, support_text, reply_markup=markup)
        
    elif text == "📁 Help":
        help_text = "🤖 বট ব্যবহার করতে নিচের মেনু অপশনগুলো ব্যবহার করুন।"
        bot.send_message(chat_id, help_text)
    else:
        bot.send_message(chat_id, "দয়া করে নিচের মেনু থেকে একটি অপশন বেছে নিন।")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    
    if call.data == "task_facebook_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔑 Fb 2FA Task", callback_data="task_fb_2fa"),
            types.InlineKeyboardButton("🍪 Fb Cookies Task", callback_data="task_fb_cookies"),
            types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_work")
        )
        bot.edit_message_text("📘 *Facebook Task Options:*", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "task_instagram_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📸 Instagram 2FA Task", callback_data="task_ig_2fa"),
            types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_work")
        )
        bot.edit_message_text("📸 *Instagram Task Options:*", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "task_gmail_menu":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_work"))
        bot.edit_message_text("✉️ *Gmail Task*\n\nGmail option is active. New tasks will be added soon!", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "task_fb_2fa":
        name, password = generate_random_credentials()
        user["state"] = "waiting_for_fb_2fa_key"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_process"))
        
        task_info = (
            "🔑 *Facebook 2FA Task*\n\n"
            f"👤 Name: `{name}`\n"
            f"🔑 Password: `{password}`\n\n"
            "1️⃣ Create a Facebook account using these details.\n"
            "2️⃣ Enable 2FA and get the setup key.\n"
            "⚠️ *Report Time: 30 minutes*\n\n"
            "👉 Please paste your 2FA Setup Key:"
        )
        bot.send_message(chat_id, task_info, reply_markup=markup)
        bot.answer_callback_query(call.id)

    elif call.data == "task_fb_cookies":
        name, password = generate_random_credentials()
        user["state"] = "waiting_for_fb_cookies_uid"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_process"))
        
        task_info = (
            "🍪 *Facebook Cookies Task*\n\n"
            f"👤 Name: `{name}`\n"
            f"🔑 Password: `{password}`\n\n"
            "1️⃣ Create a Facebook account using these details.\n"
            "⚠️ *Report Time: 30 minutes*\n\n"
            "👉 First, please provide your Facebook UID:"
        )
        bot.send_message(chat_id, task_info, reply_markup=markup)
        bot.answer_callback_query(call.id)

    elif call.data == "task_ig_2fa":
        username = f"user_{random.randint(10000, 99999)}"
        _, password = generate_random_credentials()
        user["state"] = "waiting_for_ig_2fa"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_process"))
        
        task_info = (
            "📸 *Instagram 2FA Task*\n\n"
            f"👤 Username: `{username}`\n"
            f"🔑 Password: `{password}`\n\n"
            "1️⃣ Create an Instagram account using these details.\n"
            "⚠️ *Report Time: 30 minutes*\n\n"
            "👉 Please provide your 2FA Key:"
        )
        bot.send_message(chat_id, task_info, reply_markup=markup)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("withdraw_"):
        method = call.data.split("_")[1].upper()
        user["withdraw_method"] = method
        user["state"] = "waiting_for_withdraw_details"
        bot.answer_callback_query(call.id, f"Selected {method}")
        bot.send_message(chat_id, f"✅ You selected *{method}* for withdrawal.\nلطفاً আপনার পেমেন্ট অ্যাকাউন্ট ডিটেইলস (নম্বর বা ওয়ালেট অ্যাড্রেস) সেন্ড করুন:")

    elif call.data == "cancel_process":
        user["state"] = None
        bot.answer_callback_query(call.id, "Process Cancelled")
        bot.send_message(chat_id, "❌ Process Cancelled. Use the keyboard below to continue.")
        
    elif call.data == "back_to_work":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📘 1. Facebook Task", callback_data="task_facebook_menu"),
            types.InlineKeyboardButton("📸 2. Instagram Task", callback_data="task_instagram_menu"),
            types.InlineKeyboardButton("✉️ 3. Gmail Task", callback_data="task_gmail_menu")
        )
        bot.edit_message_text("🚀 *Select a Category to Start Working:*", chat_id, call.message.message_id, reply_markup=markup)

if __name__ == '__main__':
    print("Bot is starting up cleanly with Admin notifications...")
    bot.infinity_polling()
