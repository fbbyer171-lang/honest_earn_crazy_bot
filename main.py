info_text = (
        "⏱️ Processing Time: 6-12 Hours\n\n📌 Task: Facebook 2FA (0"
        " Friend)\n\n📖 Instructions:\n1. Create a Facebook account using these"
        " details.\n2. Enable 2FA using secret key below.\n\n👤 Name:"
        f" {uname}\n🔑 Password: {upass}\n🛡️ 2FA Secret Key: {secret_2fa}"
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


if name == "main":
  print("Bot is running...")
  try:
    bot.remove_webhook()
  except Exception:
    pass
  bot.infinity_polling(skip_pending=True)
   
