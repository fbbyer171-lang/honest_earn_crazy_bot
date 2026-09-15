import base64
import hashlib
import hmac
import logging
import random
import string
import struct
import telebot
from telebot import types

# Bot Configuration
TOKEN = "8980706201:AAEKtfUROOEPtsO8ZrwjKQ10Nnuan8ZHBrA"
ADMIN_CHAT_ID = 8444176616
SUPPORT_USERNAME = "@Owners_honestearnnow790"
HELP_USERNAME = "@timotyservice"

# Task Rewards Configuration
FB_HOTMAIL_REWARD = 0.08
FB_2FA_REWARD = 0.06
FB_COOKIES_REWARD = 0.07
FB_GMAIL_REWARD = 0.07
FB_COOKIES_30F_REWARD = 0.12

bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

user_data = {}

FIRST_NAMES = [
    "Shakib",
    "Fahim",
    "Mintu",
    "Rakib",
    "Nayeem",
    "Tanvir",
    "Sojib",
    "Imran",
    "Arman",
    "Sumon",
    "Ripon",
    "Juel",
    "Hridoy",
    "Mahmud",
    "Shohan",
    "Mehedi",
    "Nabil",
    "Joy",
    "Al-Amin",
    "Parvez",
]
LAST_NAMES = [
    "Ahmed",
    "Hasan",
    "Khan",
    "Ali",
    "Chowdhury",
    "Talukdar",
    "Sarker",
    "Mollah",
    "Bhuyan",
    "Mia",
    "Biswas",
    "Hawlader",
]


def get_user(chat_id):
  if chat_id not in user_data:
    user_data[chat_id] = {
        "balance": 0.0,
        "total_submitted": 0,
        "total_success": 0,
        "review_pending": 0,
        "admin_rejected": 0,
        "bot_rejected": 0,
        "referrals": 0,
        "active_referrals": 0,
        "commission": 0.0,
        "state": None,
        "pending_reward": 0.0,
        "gen_user": None,
        "gen_pass": None,
        "gen_2fa": None,
    }
  return user_data[chat_id]


def generate_bangladeshi_credentials():
  first = random.choice(FIRST_NAMES)
  last = random.choice(LAST_NAMES)
  full_name = f"{first} {last}"
  letters = string.ascii_letters + string.digits
  rand_pass = "".join(random.choice(letters) for i in range(8))
  password = f"Pass_{rand_pass}"
  base32_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
  secret_2fa = "".join(random.choice(base32_chars) for _ in range(16))
  return full_name, password, secret_2fa


def get_totp_code(secret_key):
  try:
    key = base64.b32decode(
        secret_key.upper() + "=" * (-len(secret_key) % 8), casefold=True
    )
    import time

    counter = struct.pack(">Q", int(time.time() // 30))
    mac = hmac.new(key, counter, hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    binary = (
        struct.unpack(">I", mac[offset : offset + 4])[0] & 0x7FFFFFFF
    )
    otp = str(binary % 1000000).zfill(6)
    return otp
  except Exception:
    return "123456"


def get_main_menu():
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
  btn_work = types.KeyboardButton("🚀 Start Work")
  btn_balance = types.KeyboardButton("💰 Balance")
  btn_withdraw = types.KeyboardButton("💸 Withdraw")
  btn_ref = types.KeyboardButton("👥 Referrals")
  btn_leaderboard = types.KeyboardButton("🏆 Leaderboard")
  btn_stats = types.KeyboardButton("📊 Statistics")
  btn_support = types.KeyboardButton("🎧 Support")
  btn_help = types.KeyboardButton("❓ Help")
  markup.add(
      btn_work,
      btn_balance,
      btn_withdraw,
      btn_ref,
      btn_leaderboard,
      btn_stats,
      btn_support,
      btn_help,
  )
  return markup


def get_cancel_markup():
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
  markup.add(types.KeyboardButton("❌ Cancel Process"))
  return markup


@bot.message_handler(commands=["start"])
def send_welcome(message):
  chat_id = message.chat.id
  user = get_user(chat_id)
  user["state"] = None
  welcome_text = (
      f"👋 Welcome, {message.from_user.first_name}!\n\n🤖 Earn money by"
      " completing available tasks.\nPlease use the menu below to start"
      " working!"
  )
  bot.send_message(chat_id, welcome_text, reply_markup=get_main_menu())


@bot.message_handler(content_types=["text"])
def handle_messages(message):
  text = message.text
  chat_id = message.chat.id
  user = message.from_user
  u_data = get_user(chat_id)
  state = u_data.get("state", None)

  if text == "❌ Cancel Process":
    u_data["state"] = None
    bot.send_message(
        chat_id,
        "❌ Process Cancelled. Use the menu below to continue.",
        reply_markup=get_main_menu(),
    )
    return

  # MAIN MENU COMMANDS
  if text == "🚀 Start Work":
    u_data["state"] = None
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "📘 1. Facebook Tasks", callback_data="task_facebook"
        ),
        types.InlineKeyboardButton(
            "📷 2. Instagram Tasks (Off)", callback_data="task_off_alert"
        ),
        types.InlineKeyboardButton(
            "📧 3. Gmail Task (Coming Soon)", callback_data="task_off_alert"
        ),
    )
    bot.send_message(
        chat_id, "📌 Please select a category to start working:", reply_markup=markup
    )
    return

  elif text == "💰 Balance":
    u_data["state"] = None
    bal = u_data["balance"]
    bot.send_message(chat_id, f"💰 Your Current Balance: ${bal:.2f}")
    return

  elif text == "💸 Withdraw":
    u_data["state"] = None
    bal = u_data["balance"]
    if bal < 0.20:
      bot.send_message(
          chat_id,
          "⚠️ Insufficient balance for withdrawal. Minimum balance must be"
          " $0.20.",
      )
    else:
      markup = types.InlineKeyboardMarkup(row_width=1)
      markup.add(
          types.InlineKeyboardButton("Bkash", callback_data="wd_bkash"),
          types.InlineKeyboardButton("Binance", callback_data="wd_binance"),
          types.InlineKeyboardButton("BEP20 Address", callback_data="wd_bep20"),
      )
      bot.send_message(
          chat_id, "💳 Please select your payout method:", reply_markup=markup
      )
    return

  elif text == "👥 Referrals":
    u_data["state"] = None
    ref_count = u_data["referrals"]
    comm = u_data["commission"]
    ref_link = f"https://t.me/{bot.get_me().username}?start={chat_id}"
    ref_text = (
        "👥 Referral Program\n\nInvite friends and earn a 20% lifetime commission"
        f" on their task earnings!\n\n🔗 Your Referral Link:\n{ref_link}\n\n📊 Total"
        f" Referrals: {ref_count}\n💰 Total Commission Earned: ${comm:.3f}"
    )
    bot.send_message(chat_id, ref_text)
    return

  elif text == "🏆 Leaderboard":
    u_data["state"] = None
    bot.send_message(chat_id, "🏆 Referral Earnings Leaderboard\n\nNo records yet.")
    return

  elif text == "📊 Statistics":
    u_data["state"] = None
    stats_text = (
        f"📊 Your Work Statistics\n\n📝 Total Submitted:"
        f" {u_data['total_submitted']}\n✅ Total Success:"
        f" {u_data['total_success']}\n⏳ Review Pending:"
        f" {u_data['review_pending']}\n❌ Admin Rejected:"
        f" {u_data['admin_rejected']}\n🤖 Bot Rejected: {u_data['bot_rejected']}"
    )
    bot.send_message(chat_id, stats_text)
    return

  elif text == "🎧 Support":
    u_data["state"] = None
    bot.send_message(
        chat_id,
        f"🎧 For any help or issues, contact our support admin:\n👉"
        f" {SUPPORT_USERNAME}",
    )
    return

  elif text == "❓ Help":
    u_data["state"] = None
    bot.send_message(
        chat_id,
        f"ℹ️ For any assistance, contact our help desk:\n👉 {HELP_USERNAME}",
    )
    return

  # PROCESS INPUT BASED ON STATE
  if state == "WAITING_FB_HOTMAIL_DATA":
    details = text
    gen_user = u_data.get("gen_user", "N/A")
    gen_pass = u_data.get("gen_pass", "N/A")
    u_data["state"] = None
    u_data["total_submitted"] += 1
    u_data["review_pending"] += 1
    u_data["pending_reward"] = FB_HOTMAIL_REWARD

    admin_msg = (
        f"🚨 New Facebook Hotmail Task Submission! (Reward:"
        f" ${FB_HOTMAIL_REWARD})\n\n👤 Worker: @{user.username or 'None'}"
        f" ({chat_id})\n👤 Generated Name: {gen_user}\n🔒 Generated Password:"
        f" {gen_pass}\n📋 Submitted Hotmail/Outlook Format:\n{details}\n⏳ Report"
        " Time Window: 30 Minutes"
    )

    approval_markup = types.InlineKeyboardMarkup(row_width=2)
    approval_markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{chat_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{chat_id}"),
    )

    try:
      bot.send_message(
          ADMIN_CHAT_ID, admin_msg, reply_markup=approval_markup
      )
    except Exception as e:
      print(f"Error: {e}")

    bot.send_message(
        chat_id,
        "✅ Facebook Hotmail Task Submitted Successfully!\n⏳ An admin will"
        " review it within 30 minutes.",
        reply_markup=get_main_menu(),
    )

  elif state == "WAITING_FB_2FA_UID":
    u_data["temp_uid"] = text
    u_data["state"] = "WAITING_FB_2FA_KEY_CONFIRM"
    bot.send_message(
        chat_id,
        "🔑 Please paste your Facebook 2FA Setup Key or confirmation details:",
        reply_markup=get_cancel_markup(),
    )

  elif state == "WAITING_FB_2FA_KEY_CONFIRM":
    uid = u_data.get("temp_uid")
    key_info = text
    gen_user = u_data.get("gen_user", "N/A")
    gen_pass = u_data.get("gen_pass", "N/A")
    gen_2fa = u_data.get("gen_2fa", "N/A")
    u_data["state"] = None
    u_data["total_submitted"] += 1
    u_data["review_pending"] += 1
    u_data["pending_reward"] = FB_2FA_REWARD

    admin_msg = (
        f"🚨 New Facebook 2FA Task Submission! (Reward: ${FB_2FA_REWARD})\n\n👤"
        f" Worker: @{user.username or 'None'} ({chat_id})\n👤 Generated Name:"
        f" {gen_user}\n🔒 Generated Password: {gen_pass}\n🛡️ Bot 2FA Secret:"
        f" {gen_2fa}\n🆔 UID: {uid}\n📋 Details: {key_info}\n⏳ Report Time"
        " Window: 30 Minutes"
    )

    approval_markup = types.InlineKeyboardMarkup(row_width=2)
    approval_markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{chat_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{chat_id}"),
    )

    try:
      bot.send_message(
          ADMIN_CHAT_ID, admin_msg, reply_markup=approval_markup
      )
    except Exception as e:
      print(f"Error: {e}")

    bot.send_message(
        chat_id,
        "✅ Facebook 2FA Account Submitted Successfully!\n⏳ An admin will"
        " review it within 30 minutes.",
        reply_markup=get_main_menu(),
    )

  elif state == "WAITING_FB_COOKIES_UID":
    u_data["temp_uid"] = text
    u_data["state"] = "WAITING_FB_COOKIES_DATA"
    bot.send_message(
        chat_id,
        "🍪 Please paste your Facebook Cookies (JSON string):",
        reply_markup=get_cancel_markup(),
    )

  elif state == "WAITING_FB_COOKIES_DATA":
    uid = u_data.get("temp_uid")
    cookies = text
    gen_user = u_data.get("gen_user", "N/A")
    gen_pass = u_data.get("gen_pass", "N/A")
    u_data["state"] = None
    u_data["total_submitted"] += 1
    u_data["review_pending"] += 1
    u_data["pending_reward"] = FB_COOKIES_REWARD

    admin_msg = (
        f"🚨 New Facebook Cookies Task Submission! (Reward:"
        f" ${FB_COOKIES_REWARD})\n\n👤 Worker: @{user.username or 'None'}"
        f" ({chat_id})\n👤 Generated Name: {gen_user}\n🔒 Generated Password:"
        f" {gen_pass}\n🆔 UID: {uid}\n🍪 Cookies: {cookies}\n⏳ Report Time"
        " Window: 30 Minutes"
    )

    approval_markup = types.InlineKeyboardMarkup(row_width=2)
    approval_markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{chat_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{chat_id}"),
    )

    try:
      bot.send_message(
          ADMIN_CHAT_ID, admin_msg, reply_markup=approval_markup
      )
    except Exception as e:
      print(f"Error: {e}")

    bot.send_message(
        chat_id,
        "✅ Facebook Cookies Submitted Successfully!\n⏳ An admin will review it"
        " within 30 minutes.",
        reply_markup=get_main_menu(),
    )

  elif state == "WAITING_WITHDRAW_DETAILS":
    method = u_data.get("withdraw_method")
    details = text
    u_data["state"] = None

    admin_msg = (
        f"💸 New Withdrawal Request!\n\n👤 User: @{user.username or 'None'}"
        f" ({chat_id})\n💳 Method: {method}\n📋 Details: {details}"
    )

    approval_markup = types.InlineKeyboardMarkup(row_width=2)
    approval_markup.add(
        types.InlineKeyboardButton(
            "✅ Approve Payout", callback_data=f"wd_app_{chat_id}"
        ),
        types.InlineKeyboardButton(
            "❌ Reject Payout", callback_data=f"wd_rej_{chat_id}"
        ),
    )

    try:
      bot.send_message(
          ADMIN_CHAT_ID, admin_msg, reply_markup=approval_markup
      )
    except Exception as e:
      print(f"Error: {e}")

    bot.send_message(
        chat_id,
        "✅ Withdrawal request submitted successfully! Admin will process it"
        " soon.",
        reply_markup=get_main_menu(),
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
  chat_id = call.message.chat.id
  data = call.data

  if data.startswith("app_"):
    target_user = int(data.split("_")[1])
    bot.answer_callback_query(call.id, "Task Approved Successfully!")
    target_u_data = get_user(target_user)
    reward = target_u_data.get("pending_reward", 0.08)
    target_u_data["balance"] += reward
    target_u_data["total_success"] += 1
    if target_u_data["review_pending"] > 0:
      target_u_data["review_pending"] -= 1
    target_u_data["pending_reward"] = 0.0

    try:
      bot.send_message(
          target_user,
          f"🎉 Your submitted task has been approved by the admin! Your"
          f" reward of ${reward:.2f} has been added to your balance.",
      )
    except Exception:
      pass

    try:
      bot.edit_message_text(
          call.message.text + "\n\n✅ STATUS: APPROVED BY ADMIN",
          call.message.chat.id,
          call.message.message_id,
      )
    except Exception:
      pass
    return

  elif data.startswith("rej_"):
    target_user = int(data.split("_")[1])
    bot.answer_callback_query(call.id, "Task Rejected!")
    target_u_data = get_user(target_user)
    target_u_data["admin_rejected"] += 1
    if target_u_data["review_pending"] > 0:
      target_u_data["review_pending"] -= 1
    target_u_data["pending_reward"] = 0.0

    try:
      bot.send_message(
          target_user,
          "❌ Your submitted task was rejected by the admin. Please try again"
          " correctly.",
      )
    except Exception:
      pass

    try:
      bot.edit_message_text(
          call.message.text + "\n\n❌ STATUS: REJECTED BY ADMIN",
          call.message.chat.id,
          call.message.message_id,
      )
    except Exception:
      pass
    return

  elif data.startswith("wd_app_"):
    target_user = int(data.split("_")[2])
    bot.answer_callback_query(call.id, "Payout Approved!")
    try:
      bot.edit_message_text(
          call.message.text + "\n\n✅ STATUS: PAYOUT APPROVED",
          call.message.chat.id,
          call.message.message_id,
      )
      bot.send_message(
          target_user,
          "🎉 Your withdrawal request has been approved and paid by the admin!",
      )
    except Exception:
      pass
    return

  elif data.startswith("wd_rej_"):
    target_user = int(data.split("_")[2])
    bot.answer_callback_query(call.id, "Payout Rejected!")
    try:
      bot.edit_message_text(
          call.message.text + "\n\n❌ STATUS: PAYOUT REJECTED",
          call.message.chat.id,
          call.message.message_id,
      )
      bot.send_message(
          target_user,
          "❌ Your withdrawal request was rejected by the admin.",
      )
    except Exception:
      pass
    return

  u_data = get_user(chat_id)

  if data == "task_facebook":
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            f"🔥 Facebook Hotmail (${FB_HOTMAIL_REWARD}) [ON]",
            callback_data="fb_task_hotmail_info",
        ),
        types.InlineKeyboardButton(
            f"📘 Fb 2FA (0 Friend) (${FB_2FA_REWARD}) [ON]",
            callback_data="fb_task_2fa_info",
        ),
        types.InlineKeyboardButton(
            f"🍪 Fb Cookies (${FB_COOKIES_REWARD}) [ON]",
            callback_data="fb_task_cookies_info",
        ),
        types.InlineKeyboardButton(
            f"📧 Create FB with Gmail (${FB_GMAIL_REWARD}) [OFF]",
            callback_data="task_off_alert",
        ),
        types.InlineKeyboardButton(
            f"🍪 Cookies (30 Friends) (${FB_COOKIES_30F_REWARD}) [OFF]",
            callback_data="task_off_alert",
        ),
        types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main"),
    )
    bot.edit_message_text(
        "📂 Choose Facebook Task Type:",
        chat_id,
        call.message.message_id,
        reply_markup=markup,
    )

  elif data == "task_off_alert":
    bot.answer_callback_query(
        call.id,
        "⚠️ This task is currently turned off by admin!",
        show_alert=True,
    )

  elif data == "back_to_main":
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "📘 1. Facebook Tasks", callback_data="task_facebook"
        ),
        types.InlineKeyboardButton(
            "📷 2. Instagram Tasks (Off)", callback_data="task_off_alert"
        ),
        types.InlineKeyboardButton(
            "📧 3. Gmail Task (Coming Soon)", callback_data="task_off_alert"
        ),
    )
    bot.edit_message_text(
        "📌 Please select a category to start working:",
        chat_id,
        call.message.message_id,
        reply_markup=markup,
    )

  elif data == "fb_task_hotmail_info":
    uname, upass, _ = generate_bangladeshi_credentials()
    u_data["gen_user"] = uname
    u_data["gen_pass"] = upass

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "▶️ Start", callback_data="fb_task_hotmail_start"
        ),
        types.InlineKeyboardButton("◀️ Back", callback_data="task_facebook"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="back_to_main"),
    )

    info_text = (
        "⏱️ Processing Time: 6-12 Hours\n\n📌 Task: Facebook Hotmail (Cookies"
        " Only)\n\n📖 Instructions:\n1. Create a Facebook account using these"
        " details along with your own Hotmail/Outlook account.\n2. Do NOT enable"
        f" 2FA.\n3. Click Start to submit details.\n\n👤 Name: {uname}\n🔑"
        f" Password: {upass}"
    )
    bot.edit_message_text(
        info_text,
        chat_id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup,
    )

  elif data == "fb_task_hotmail_start":
    u_data["state"] = "WAITING_FB_HOTMAIL_DATA"
    prompt_text = (
        "📥 Please submit your Outlook/Hotmail format:\n\n"
        "`email|password|token|client_id|proxy`\n\n"
        "Paste the complete string below:"
    )
    bot.send_message(
        chat_id,
        prompt_text,
        parse_mode="Markdown",
        reply_markup=get_cancel_markup(),
    )

  elif data == "fb_task_2fa_info":
    uname, upass, secret_2fa = generate_bangladeshi_credentials()
    u_data["gen_user"] = uname
    u_data["gen_pass"] = upass
    u_data["gen_2fa"] = secret_2fa

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "📱 Get Code (2FA OTP)", callback_data="fb_task_get_code"
        ),
        types.InlineKeyboardButton(
            "▶️ Start Task", callback_data="fb_task_2fa_start"
        ),
        types.InlineKeyboardButton("◀️ Back", callback_data="task_facebook"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="back_to_main"),
    )

    info_text = (
        "⏱️ Processing Time: 6-12 Hours\n\n📌 Task: Facebook 2FA (0"
        " Friend)\n\n📖 Instructions:\n1. Create a Facebook account using these"
        " details.\n2. Enable 2FA using secret key below.\n\n👤 Name:"
        f" {uname}\n🔑 Password: {upass}\n🛡️ 2FA Secret Key: `{secret_2fa}`"
    )
    bot.edit_message_text(
        info_text,
        chat_id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup,
    )

  elif data == "fb_task_get_code":
    secret_2fa = u_data.get("gen_2fa", "JBSWY3DPEHPK3PXP")
    current_otp = get_totp_code(secret_2fa)
    bot.answer_callback_query(
        call.id, f"🔑 Current 2FA Code: {current_otp}", show_alert=True
    )

  elif data == "fb_task_2fa_start":
    u_data["state"] = "WAITING_FB_2FA_UID"
    bot.send_message(
        chat_id,
        "🆔 Please provide your Facebook UID:",
        reply_markup=get_cancel_markup(),
    )

  elif data == "fb_task_cookies_info":
    uname, upass, _ = generate_bangladeshi_credentials()
    u_data["gen_user"] = uname
    u_data["gen_pass"] = upass

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "▶️ Start Task", callback_data="fb_task_cookies_start"
        ),
        types.InlineKeyboardButton("◀️ Back", callback_data="task_facebook"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="back_to_main"),
    )

    info_text = (
        "⏱️ Processing Time: 6-12 Hours\n\n📌 Task: Facebook Cookies\n\n📖"
        " Instructions:\n1. Create FB account.\n2. Extract cookies.\n3. Click"
        f" Start Task.\n\n👤 Name: {uname}\n🔑 Password: {upass}"
    )
    bot.edit_message_text(
        info_text,
        chat_id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup,
    )

  elif data == "fb_task_cookies_start":
    u_data["state"] = "WAITING_FB_COOKIES_UID"
    bot.send_message(
        chat_id,
        "🆔 Please provide your Facebook UID:",
        reply_markup=get_cancel_markup(),
    )

  elif data in ["wd_bkash", "wd_binance", "wd_bep20"]:
    method = data.replace("wd_", "").upper()
    u_data["withdraw_method"] = method
    u_data["state"] = "WAITING_WITHDRAW_DETAILS"
    bot.send_message(
        chat_id,
        f"✅ You selected {method}.\n📱 Please send your payout account details"
        " (Number or Wallet Address):",
        reply_markup=get_cancel_markup(),
    )


if __name__ == "__main__":
  print("Bot is running...")
  try:
    bot.remove_webhook()
  except Exception:
    pass
  bot.infinity_polling(skip_pending=True)
