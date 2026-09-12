import os
import threading
from flask import Flask, render_template_string, request, redirect, url_for
import telebot
from telebot import types

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "honest_crazy_secret_key")

settings = {
    "cookie_rate": 0.065,
    "fa_rate": 0.06,
    "timer_minutes": 45
}

submissions_db = []
withdrawals_db = []
users_db = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    if user_id not in users_db:
        users_db[user_id] = {"uid": user_id, "username": username, "balance": 0.0}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🚀 Start Work")
    btn2 = types.KeyboardButton("💼 Balance")
    btn3 = types.KeyboardButton("💸 Withdraw")
    btn4 = types.KeyboardButton("🌐 Language")
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(
        message.chat.id,
        "👋 Welcome to *HONEST CRAZY EARN BOT*!\n\nUse the menu buttons below to start earning and managing your account.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    if text == "🚀 Start Work":
        bot.send_message(message.chat.id, "✨ Task generation started! Please check available tasks in the web app or continue clicking.")
    elif text == "💼 Balance":
        user_id = message.from_user.id
        bal = users_db.get(user_id, {}).get("balance", 0.0)
        bot.send_message(message.chat.id, f"💰 Your current balance: **${bal:.2f}**")
    elif text == "💸 Withdraw":
        bot.send_message(message.chat.id, "💳 To withdraw your earnings, please use the web dashboard or contact support.")
    elif text == "🌐 Language":
        bot.send_message(message.chat.id, "🌐 Language is currently set to English.")
    else:
        bot.send_message(message.chat.id, "I did not understand that. Please use the menu buttons.")

@app.route('/')
def admin_panel():
    return render_template_string('''
        <!doctype html>
        <title>Honest Crazy Admin Panel</title>
        <h2>Admin Dashboard</h2>
        <p>Bot is running successfully!</p>
        <h3>Settings</h3>
        <form method="POST" action="/update_settings">
            Cookie Rate: <input type="text" name="cookie_rate" value="{{settings.cookie_rate}}"><br><br>
            FA Rate: <input type="text" name="fa_rate" value="{{settings.fa_rate}}"><br><br>
            Timer (Mins): <input type="text" name="timer_minutes" value="{{settings.timer_minutes}}"><br><br>
            <input type="submit" value="Update Settings">
        </form>
    ''', settings=settings)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    settings['cookie_rate'] = float(request.form.get('cookie_rate', settings['cookie_rate']))
    settings['fa_rate'] = float(request.form.get('fa_rate', settings['fa_rate']))
    settings['timer_minutes'] = int(request.form.get('timer_minutes', settings['timer_minutes']))
    return redirect(url_for('admin_panel'))

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    bot.infinity_polling()
