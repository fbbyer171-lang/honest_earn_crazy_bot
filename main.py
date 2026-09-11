import os
import threading
from flask import Flask, render_template, request, redirect, url_for, flash
import telebot
from telebot import types

# Configuration & Branding: HONEST CRAZY EARN BOT
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "honest_crazy_secret_key")

# Pricing Specs & Global State
settings = {
    "cookie_rate": 0.065,
    "fa_rate": 0.06,
    "timer_minutes": 45
}

# In-memory storage for database-free execution on Replit
submissions_db = []
withdrawals_db = []
users_db = {}

# --- TELEGRAM BOT LOGIC ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    users_db[user_id] = {"uid": user_id, "username": username, "balance": 0.0}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_start_work = types.KeyboardButton("🚀 Start Work")
    btn_balance = types.KeyboardButton("💰 Balance")
    btn_withdraw = types.KeyboardButton("💸 Withdraw")
    btn_referrals = types.KeyboardButton("👥 Referrals")
    btn_leaderboard = types.KeyboardButton("🏆 Leaderboard")
    btn_stats = types.KeyboardButton("📊 Statistics")
    markup.add(btn_start_work, btn_balance, btn_withdraw, btn_referrals, btn_leaderboard, btn_stats)

    welcome_text = (
        "🤖 *Welcome to HONEST CRAZY EARN BOT* 🤖\n\n"
        "Earn real rewards securely by completing verified Facebook & Instagram tasks.\n"
        f"• Cookies Task Rate: `${settings['cookie_rate']}`\n"
        f"• 2FA Task Rate: `${settings['fa_rate']}`\n"
        f"• Report Time Limit: `{settings['timer_minutes']} Minutes`\n\n"
        "Choose an option below to get started:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🚀 Start Work")
def start_work(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_fa = types.InlineKeyboardButton(f"🔑 2FA Task (${settings['fa_rate']})", callback_data="task_2fa")
    btn_cookies = types.InlineKeyboardButton(f"🍪 Cookies Task (${settings['cookie_rate']})", callback_data="task_cookies")
    btn_cancel = types.InlineKeyboardButton("❌ Cancel", callback_data="task_cancel")
    markup.add(btn_fa, btn_cookies, btn_cancel)
    bot.send_message(message.chat.id, "📁 *Select Task Category:*", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def task_callback(call):
    chat_id = call.message.chat.id
    if call.data == "task_2fa":
        text = (
            "📁 *Create Facebook Account (2FA)*\n\n"
            "👤 Name: James Taylor\n"
            "🔑 Password: 6JsoG2CpAy\n\n"
            "1️⃣ Create account using details.\n"
            "2️⃣ Enable 2FA.\n"
            "3️⃣ Submit your 2FA Key below within 45 minutes:"
        )
        bot.edit_message_text(text, chat_id, call.message.message_id)
        bot.register_next_step_handler(call.message, process_2fa_submission)
    elif call.data == "task_cookies":
        text = (
            "📁 *Facebook Cookies Task*\n\n"
            "1️⃣ Login securely to the provided browser profile.\n"
            "2️⃣ Export your active session JSON/Cookies.\n"
            "3️⃣ Submit your raw Cookies string below within 45 minutes:"
        )
        bot.edit_message_text(text, chat_id, call.message.message_id)
        bot.register_next_step_handler(call.message, process_cookies_submission)
    elif call.data == "task_cancel":
        bot.edit_message_text("❌ Task cancelled.", chat_id, call.message.message_id)

def process_2fa_submission(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    fa_key = message.text

    submission = {
        "id": len(submissions_db) + 1,
        "username": f"@{username}",
        "uid": str(user_id),
        "task_type": "2FA Task",
        "two_fa": fa_key,
        "cookies": "Not Provided",
        "status": "Pending",
        "reward": settings['fa_rate']
    }
    submissions_db.append(submission)
    bot.send_message(message.chat.id, "✅ *2FA Key Submitted Successfully!* Waiting for admin verification.")

def process_cookies_submission(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    cookies_data = message.text

    submission = {
        "id": len(submissions_db) + 1,
        "username": f"@{username}",
        "uid": str(user_id),
        "task_type": "Cookies Task",
        "two_fa": "Not Provided",
        "cookies": cookies_data,
        "status": "Pending",
        "reward": settings['cookie_rate']
    }
    submissions_db.append(submission)
    bot.send_message(message.chat.id, "✅ *Cookies Submitted Successfully!* Waiting for admin verification.")

@bot.message_handler(func=lambda message: message.text == "💰 Balance")
def check_balance(message):
    user_id = message.from_user.id
    bal = users_db.get(user_id, {}).get("balance", 0.0)
    bot.send_message(message.chat.id, f"💰 *Your Current Balance:* `${bal:.3f}`")

@bot.message_handler(func=lambda message: message.text == "💸 Withdraw")
def request_withdraw(message):
    bot.send_message(message.chat.id, "💸 Please send your withdrawal wallet address:")
    bot.register_next_step_handler(message, save_withdrawal)

def save_withdrawal(message):
    wallet = message.text
    withdrawals_db.append({"id": len(withdrawals_db) + 1, "user": message.from_user.username, "wallet": wallet, "status": "Pending"})
    bot.send_message(message.chat.id, f"✅ *Withdrawal Request Submitted with wallet:* `{wallet}`")

# --- FLASK ADMIN DASHBOARD ---

@app.route('/')
def admin_dashboard():
    return render_template('dashboard.html', settings=settings, submissions=submissions_db, withdrawals=withdrawals_db)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    settings['cookie_rate'] = float(request.form.get('cookie_rate', 0.065))
    settings['fa_rate'] = float(request.form.get('fa_rate', 0.06))
    settings['timer_minutes'] = int(request.form.get('timer_minutes', 45))
    flash("Settings updated successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/approve/<int:sub_id>')
def approve_task(sub_id):
    for sub in submissions_db:
        if sub['id'] == sub_id:
            sub['status'] = 'Approved'
            uid = int(sub['uid'])
            if uid in users_db:
                users_db[uid]['balance'] += sub['reward']
    return redirect(url_for('admin_dashboard'))

@app.route('/reject/<int:sub_id>')
def reject_task(sub_id):
    for sub in submissions_db:
        if sub['id'] == sub_id:
            sub['status'] = 'Rejected'
    return redirect(url_for('admin_dashboard'))

# Background thread runner for Telegram Bot
def run_bot():
    bot.infinity_none_stop = True
    bot.infinity_polling()

if __name__ == '__main__':
    # Start Telegram Bot in a separate background thread to prevent crashing with Flask
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask Web Server
    app.run(host='0.0.0.0', port=5000)
