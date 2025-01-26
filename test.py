async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
#"""نمایش گزینه‌های مدل انتخاب‌شده (ویژگی‌ها، معرفی و تفاوت)"""
    query = update.callback_query
    await query.answer()

    # استخراج اطلاعات مدل از callback_data
    _, material_id, device_index = query.data.split("_")
    material_id = int(material_id)
    device_index = int(device_index)

    # فیلتر دستگاه‌ها مرتبط با ماده انتخاب‌شده
    filtered_devices = devices_data[
        devices_data["کاربرد ID"]
        .apply(lambda x: str(material_id) in map(str.strip, str(x).split(",")))
    ].drop_duplicates(subset=["دستگاه"]).reset_index(drop=True)

    # بازیابی دستگاه انتخاب‌شده
    selected_device = filtered_devices.loc[device_index, "دستگاه"]

    # فیلتر مدل‌های مرتبط با دستگاه انتخاب‌شده
    device_models = devices_data[
        (devices_data["دستگاه"] == selected_device) &
        devices_data["کاربرد ID"].apply(lambda x: str(material_id) in map(str.strip, str(x).split(",")))
    ]

    # ایجاد دکمه‌ها برای مدل‌های دستگاه
    keyboard = [
        [InlineKeyboardButton(f"{row['مدل']} - {'هوشمند' if row['هوشمند یا غیر هوشمند'] == 'هوشمند' else 'غیر هوشمند'}",
                              callback_data=f"model_{material_id}_{row.name}")]
        for _, row in device_models.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً مدل دستگاه را انتخاب کنید:", reply_markup=reply_markup)

async def handle_info_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات مرتبط با گزینه انتخاب‌شده (ویژگی‌ها، معرفی، تفاوت)"""
    query = update.callback_query
    await query.answer()

    # استخراج نوع اطلاعات و مدل از callback_data
    _, info_type, model_id = query.data.split("_")
    model_id = int(model_id)

    # فیلتر داده‌ها بر اساس model_id
    if info_type == "features":
        filtered_data = features_data[features_data["ویژگی ID"] == model_id]
        if not filtered_data.empty:
            content = filtered_data["ویژگی ها"].iloc[0]
        else:
            content = "اطلاعات ویژگی‌ها موجود نیست."
    elif info_type == "intro":
        filtered_data = introductions_data[introductions_data["معرفی ID"] == model_id]
        if not filtered_data.empty:
            content = filtered_data["متن معرفی"].iloc[0]
        else:
            content = "اطلاعات معرفی موجود نیست."
    elif info_type == "diff":
        filtered_data = differences_data[differences_data["تفاوت ID"] == model_id]
        if not filtered_data.empty:
            content = filtered_data["توضیحات تفاوت"].iloc[0]
        else:
            content = "اطلاعات تفاوت موجود نیست."
    else:
        content = "اطلاعاتی در دسترس نیست."

    # ارسال پیام اطلاعات
    await query.message.reply_text(content)

