import os
import telebot
from telebot import types

TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"স্বাগতম, *{user_name}*! 🎉\n\n"
        "আমাদের আর্নিং ও ক্রেইজি বটে আপনাকে স্বাগতম। নিচে দেওয়া অপশনগুলো থেকে আপনার পছন্দের সেবাটি বেছে নিন:"
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
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "💰 Balance":
        bot.send_message(chat_id, "💳 আপনার বর্তমান ব্যালেন্স: *0.00 BDT*\nটাকা জমাতে কাজ শুরু করুন!")
    elif text == "🚀 Start Work":
        bot.send_message(chat_id, "📌 এই মুহূর্তে কোনো কাজ উপলব্ধ নেই। দয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন।")
    elif text == "💸 Withdraw":
        bot.send_message(chat_id, "⚠️ উইথড্র করার জন্য আপনার পর্যাপ্ত ব্যালেন্স নেই। ন্যূনতম ব্যালেন্স হতে হবে ১০০ টাকা।")
    elif text == "👥 Referrals":
        ref_link = f"https://t.me/YourBotUsername?start={message.from_user.id}"
        bot.send_message(chat_id, f"🔗 আপনার রেফারেল লিংক:\n`{ref_link}`\n\nবন্ধুদের সাথে শেয়ার করে ইনকাম করুন!")
    elif text == "🏆 Leaderboard":
        bot.send_message(chat_id, "🏆 লিডারবোর্ড আপাতত খালি রয়েছে। কাজ করে সবার উপরে চলে আসুন!")
    elif text == "📊 Statistics":
        bot.send_message(chat_id, "📊 আপনার পরিসংখ্যান:\nমোট রেফার: ০\nমোট ইনকাম: 0.00 BDT")
    elif text == "🎧 Support":
        bot.send_message(chat_id, "🎧 যেকোনো প্রয়োজনে আমাদের সাপোর্ট টিমের সাথে যোগাযোগ করুন: @SupportAdmin")
    elif text == "📁 Help":
        bot.send_message(chat_id, "📁 সাহায্য নির্দেশিকা:\n১. কাজ শুরু করুন থেকে টাস্ক সম্পন্ন করুন।\n২. রেফার করে বাড়তি ইনকাম করুন।")
    else:
        bot.send_message(chat_id, "দয়া করে নিচের মেনু থেকে একটি অপশন বেছে নিন।")

if __name__ == '__main__':
    print("Bot is starting up...")
    bot.infinity_polling()
