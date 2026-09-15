import logging
import random
import string
import telebot
from telebot import types

# Bot Configuration
TOKEN = "8980706201:AAHmK_q9vcStJiTbd-m1HGaDjbYhga3pfps"
ADMIN_CHAT_ID = 8444176616  # Your Real Admin Chat ID
SUPPORT_USERNAME = "@Owners_honestearnnow790"
HELP_USERNAME = "@timotyservice"

# Task Rewards Configuration
FB_REWARD = 0.06
IG_REWARD = 0.04

bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

# User database dictionary
user_data = {}


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
    }
  return user_data[chat_id]


def generate_random_credentials(prefix="User"):
  rand_num = random.randint(1000, 9999)
  letters = string.ascii_letters + string.digits
  rand_pass = "".join(random.choice(letters) for i in range(8))
  return f"{prefix}_{rand_num}", f"Pass_{rand_pass}"


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
  markup.add(types.KeyboardButton("❌ Cancel"))
  return markup


@bot.message_handler(commands=["start"])
def send_welcome(message):
  chat_id = message.chat.id
  user = get_user(chat_id)
  user["state"] = None

  welcome_text = (
      f"👋 Welcome, {message.from_user.first_name}!\n\n"
      "🤖 Earn money by completing tasks like Facebook & Instagram account submissions.\n"
      "Please use the menu below to start working!"
  )
  bot.send_message(chat_id, welcome_text, reply_markup=get_main_menu())


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
  text = message.text
  chat_id = message.chat.id
  user = message.from_user
  u_data = get_user(chat_id)

  state = u_data.get("state", None)

  if text == "❌ Cancel":
    u_data["state"] = None
    bot.send_message(
        chat_id,
        "❌ Process Cancelled. Use the menu below to continue.",
        reply_markup=get_main_menu(),
    )
    return

  # --- Facebook 2FA Flow ---
  if state == "WAITING_FB_2FA_UID":
    u_data["temp_uid"] = text
    u_data["state"] = "WAITING_FB_2FA_KEY"
    bot.send_message(
        chat_id,
        "🔑 Please paste your Facebook 2FA Setup Key (Base32 string):",
        reply_markup=get_cancel_markup(),
    )
    return

  elif state == "WAITING_FB_2FA_KEY":
    uid = u_data.get("temp_uid")
    key = text
    gen_user = u_data.get("gen_user", "N/A")
    gen_pass = u_data.get("gen_pass", "N/A")
    u_data["state"] = None

    u_data["total_submitted"] += 1
    u_data["review_pending"] += 1
    u_data["pending_reward"] = FB_REWARD

    admin_msg = (
        f"🚨 New Facebook 2FA Task Submission! (Reward: ${FB_REWARD})\n\n"
        f"👤 Worker: @{user.username or 'None'} ({chat_id})\n"
        f"🔑 Generated Username: {gen_user}\n"
        f"🔒 Generated Password: {gen_pass}\n"
        f"🆔 UID: {uid}\n"
        f"🛡️ 2FA Key: {key}\n"
        f"⏳ Report Time Window: 30 Minutes"
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
    return

  # --- Facebook Cookies Flow ---
  elif state == "WAITING_FB_COOKIES_UID":
    u_data["temp_uid"] = text
    u_data["state"] = "WAITING_FB_COOKIES_DATA"
    bot.send_message(
        chat_id,
        "🍪 Please paste your Facebook Cookies (JSON string):",
        reply_markup=get_cancel_markup(),
    )
    return

  elif state == "WAITING_FB_COOKIES_DATA":
    uid = u_data.get("temp_uid")
    cookies = text
    gen_user = u_data.get("gen_user", "N/A")
    gen_pass = u_data.get("gen_pass", "N/A")
    u_data["state"] = None

    u_data["total_submitted"] += 1
    u_data["review_pending"] += 1
    u_data["pending_reward"] = FB_REWARD

    admin_msg = (
        f"🚨 New Facebook Cookies Task Submission! (Reward: ${FB_REWARD})\n\n"
        f"👤 Worker: @{user.username or 'None'} ({chat_id})\n"
        f"🔑 Generated Username: {gen_user}\n"
        f"🔒 Generated Password: {gen_pass}\n"
        f"🆔 UID: {uid}\n"
        f"🍪 Cookies: {cookies}\n"
        f"⏳ Report Time Window: 30 Minutes"
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
    return

  # --- Instagram 2FA Flow ---
  elif state == "WAITING_IG_2FA_KEY":
    key = text
    gen_user = u_data.get("gen_user", "N/A")
    gen_pass = u_data.get("gen_pass", "N/A")
    u_data["state"] = None

    u_data["total_submitted"] += 1
    u_data["review_pending"] += 1
    u_data["pending_reward"] = IG_REWARD

    admin_msg = (
        f"🚨 New Instagram 2FA Task Submission! (Reward: ${IG_REWARD})\n\n"
        f"👤 Worker: @{user.username or 'None'} ({chat_id})\n"
        f"🔑 Generated Username: {gen_user}\n"
        f"🔒 Generated Password: {gen_pass}\n"
        f"🛡️ 2FA Key: {key}\n"
        f"⏳ Report Time Window: 30 Minutes"
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
        "✅ Instagram 2FA Submitted Successfully!\n⏳ An admin will review it"
        " within 30 minutes.",
        reply_markup=get_main_menu(),
    )
    return

  elif state == "WAITING_WITHDRAW_DETAILS":
    method = u_data.get("withdraw_method")
    details = text
    u_data["state"] = None

    admin_msg = (
        f"💸 New Withdrawal Request!\n\n"
        f"👤 User: @{user.username or 'None'} ({chat_id})\n"
        f"💳 Method: {method}\n"
        f"📋 Details: {details}"
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
        "✅ Withdrawal request submitted successfully! Admin will process it soon.",
        reply_markup=get_main_menu(),
    )
    return

  if text == "🚀 Start Work":
    u_data["state"] = None
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            f"📘 1. Facebook Task (${FB_REWARD})", callback_data="task_facebook"
        ),
        types.InlineKeyboardButton(
            f"📷 2. Instagram Task (${IG_REWARD})", callback_data="task_instagram"
        ),
        types.InlineKeyboardButton(
            "📧 3. Gmail Task (Coming Soon)", callback_data="task_gmail"
        ),
    )
    bot.send_message(
        chat_id, "📌 Please select a category to start working:", reply_markup=markup
    )

  elif text == "💰 Balance":
    u_data["state"] = None
    bal = u_data["balance"]
    bot.send_message(chat_id, f"💰 Your Current Balance: ${bal:.2f}")

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

  elif text == "🏆 Leaderboard":
    u_data["state"] = None
    bot.send_message(chat_id, "🏆 Referral Earnings Leaderboard\n\nNo records yet.")

  elif text == "📊 Statistics":
    u_data["state"] = None
    u = u_data
    stats_text = (
        f"📊 Your Work Statistics\n\n📝 Total Submitted:"
        f" {u['total_submitted']}\n✅ Total Success: {u['total_success']}\n⏳"
        f" Review Pending: {u['review_pending']}\n❌ Admin Rejected:"
        f" {u['admin_rejected']}\n🤖 Bot Rejected: {u['bot_rejected']}"
    )
    bot.send_message(chat_id, stats_text)

  elif text == "🎧 Support":
    u_data["state"] = None
    bot.send_message(
        chat_id,
        f"🎧 For any help or issues, contact our support admin:\n👉"
        f" {SUPPORT_USERNAME}",
    )

  elif text == "❓ Help":
    u_data["state"] = None
    bot.send_message(
        chat_id,
        f"ℹ️ For any assistance, contact our help desk:\n👉 {HELP_USERNAME}",
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
  chat_id = call.message.chat.id
  data = call.data

  if data.startswith("app_"):
    target_user = int(data.split("_")[1])
    bot.answer_callback_query(call.id, "Task Approved Successfully!")

    target_u_data = get_user(target_user)
    reward = target_u_data.get("pending_reward", 0.06)  # Default Fallback

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
    except Exception:
      pass
    try:
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
    except Exception:
      pass
    try:
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
            "📘 Fb 2FA Task", callback_data="fb_task_2fa"
        ),
        types.InlineKeyboardButton(
            "🍪 Fb Cookies Task", callback_data="fb_task_cookies"
        ),
    )
    try:
      bot.edit_message_text(
          "📂 Choose Facebook Task Type:",
          chat_id,
          call.message.message_id,
          reply_markup=markup,
      )
    except Exception:
      bot.send_message(
          chat_id, "📂 Choose Facebook Task Type:", reply_markup=markup
      )

  elif data == "fb_task_2fa":
    u_data["state"] = "WAITING_FB_2FA_UID"
    uname, upass = generate_random_credentials("FB_2FA")
    u_data["gen_user"] = uname
    u_data["gen_pass"] = upass
    bot.send_message(
        chat_id,
        f"👤 Use this details to open account:\n"
        f"🔹 Username: `{uname}`\n"
        f"🔹 Password: `{upass}`\n\n"
        f"🆔 Now, please provide your Facebook UID:",
        parse_mode="Markdown",
        reply_markup=get_cancel_markup(),
    )

  elif data == "fb_task_cookies":
    u_data["state"] = "WAIT_FB_COOKIES_UID"  # fixed key mapping below
    u_data["state"] = "WAITING_FB_COOKIES_UID"
    uname, upass = generate_random_credentials("FB_Cookie")
    u_data["gen_user"] = uname
    u_data["gen_pass"] = upass
    bot.send_message(
        chat_id,
        f"👤 Use this details to open account:\n"
        f"🔹 Username: `{uname}`\n"
        f"🔹 Password: `{upass}`\n\n"
        f"🆔 Now, please provide your Facebook UID:",
        parse_mode="Markdown",
        reply_markup=get_cancel_markup(),
    )

  elif data == "task_instagram":
    u_data["state"] = "WAITING_IG_2FA_KEY"
    uname, upass = generate_random_credentials("IG_User")
    u_data["gen_user"] = uname
    u_data["gen_pass"] = upass
    bot.send_message(
        chat_id,
        f"📸 Instagram Task\n"
        f"👤 Use this details to open account:\n"
        f"🔹 Username: `{uname}`\n"
        f"🔹 Password: `{upass}`\n\n"
        f"🔑 Now, please provide your 2FA Key:",
        parse_mode="Markdown",
        reply_markup=get_cancel_markup(),
    )

  elif data == "task_gmail":
    bot.answer_callback_query(
        call.id,
        "Gmail tasks will be available soon! Stay tuned.",
        show_alert=True,
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
  bot.infinity_polling()
