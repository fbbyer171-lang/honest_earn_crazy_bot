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
    btn_balance = types.KeyboardButton("💰 ব্যালেন্স চেক")
    btn_earn = types.KeyboardButton("🚀 কাজ শুরু করুন")
    btn_withdraw = types.KeyboardButton("📤 উইথড্র")
    btn_ref = types.KeyboardButton("👥 রেফারেল")
    markup.add(btn_balance, btn_earn, btn_withdraw, btn_ref)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    
    if text == "💰 ব্যালেন্স চেক":
        bot.send_message(chat_id, "💳 আপনার বর্তমান ব্যালেন্স: *0.00 BDT*\nটাকা জমাতে কাজ শুরু করুন!")
    elif text == "🚀 কাজ শুরু করুন":
        bot.send_message(chat_id, "📌 এই মুহূর্তে কোনো কাজ উপলব্ধ নেই। দয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন।")
    elif text == "📤 উইথড্র":
        bot.send_message(chat_id, "⚠️ উইথড্র করার জন্য আপনার পর্যাপ্ত ব্যালেন্স নেই। ন্যূনতম ব্যালেন্স হতে হবে ১০০ টাকা।")
    elif text == "👥 রেফারেল":
        bot.send_link = f"https://t.me/YourBotUsername?start={message.from_user.id}"
        bot.send_message(chat_id, f"🔗 আপনার রেফারেল লিংক:\n`{bot.send_link}`\n\nবন্ধুদের সাথে শেয়ার করে ইনকাম করুন!")
    else:
        bot.send_message(chat_id, "দয়া করে নিচের মেনু থেকে একটি অপশন বেছে নিন।")

if __name__ == '__main__':
    print("Bot is starting up...")
    bot.infinity_polling()
   
