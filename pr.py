import asyncio
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup ,BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes, Application

# --- خواندن فایل اکسل ---

file_normalized = "output2.xlsx"

devices_data = pd.read_excel(file_normalized, sheet_name="اطلاعات کلی")
applications_data = pd.read_excel(file_normalized, sheet_name="کاربرد ها")
features_data = pd.read_excel(file_normalized, sheet_name="ویژگی")
introductions_data = pd.read_excel(file_normalized, sheet_name="معرفی")
differences_data = pd.read_excel(file_normalized, sheet_name="تفاوت")

# --- مقداردهی اولیه ---
TOKEN = '7980217172:AAFuQy4Gv9wYqtm42zxbRyh9zh89oWfHqMM'


# --- تعریف توابع کمکی ---
def get_applications():
    """بازگرداندن لیست مواد و کاربردها"""
    return applications_data["ماده"].tolist()

def get_devices_by_application(application_id):
    """بازگرداندن دستگاه‌های مرتبط با یک ماده مشخص"""
    filtered_devices = devices_data[devices_data["کاربرد ID"].astype(str).str.contains(str(application_id))]
    return filtered_devices[["دستگاه"]].drop_duplicates()

def get_models_by_device(device_name, application_id):
    """بازگرداندن مدل‌های مرتبط با دستگاه و کاربرد مشخص"""
    filtered_models = devices_data[
        (devices_data["دستگاه"] == device_name) & 
        (devices_data["کاربرد ID"].astype(str).str.contains(str(application_id)))
    ]
    return filtered_models[["مدل", "هوشمند یا غیر هوشمند"]].drop_duplicates()

# --- توابع هندلر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("بزن بریم", callback_data="start_chat")]]
    keyboard.append([InlineKeyboardButton("پشتیبانی", url="https://t.me/misterwebdeveloper")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام ! من ربات لیزر دات کام هستم , اینجام تا کمکت کنم دستگاه مد نظرت رو بخری", reply_markup=reply_markup)
async def support (update:Update , context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای ارتباط با ما روی   id زیر کلیک کنید :(https://t.me/misterwebdeveloper)" , parse_mode="Markdown")
async def set_bot_commands(application: Application):
    commands = [
        BotCommand("start" , "خانه"),
        BotCommand("support" , "ارتباط با پشتیبانی")
    ]
    await application.bot.set_my_commands(commands)
async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "برای شروع اول باید بدونم روی چی میخوای حکاکی کنی!"
    )

    materials = get_applications()
    keyboard = [[InlineKeyboardButton(material, callback_data=f"material_{i+1}")] for i, material in enumerate(materials)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً متریال مورد نظرت رو انتخاب کن:", reply_markup=reply_markup)

async def handle_material_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""نمایش دستگاه‌های مرتبط با ماده انتخاب‌شده"""
    query = update.callback_query
    await query.answer()  # ارسال پاسخ برای جلوگیری از timeout

    # استخراج ماده انتخاب‌شده از callback_data
    material_id = int(query.data.split("_")[1])
    selected_material = applications_data.loc[material_id - 1, "ماده"]

    # ارسال پیام ماده انتخاب‌شده
    # await query.message.reply_text(f"شما '{selected_material}' را انتخاب کردید.")

    # فیلتر دستگاه‌ها مرتبط با ماده انتخاب‌شده
    filtered_devices = devices_data[
        devices_data["کاربرد ID"]
        .apply(lambda x: str(material_id) in map(str.strip, str(x).split(",")))
    ].drop_duplicates(subset=["دستگاه"]).reset_index(drop=True)

    # ایجاد دکمه‌ها برای دستگاه‌های فیلتر شده
    keyboard = [
        [InlineKeyboardButton(row["دستگاه"], callback_data=f"device_{material_id}_{i}")]
        for i, row in filtered_devices.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    keyboard.append([InlineKeyboardButton("بازگشت" , callback_data =  "start_chat")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(f"لطفا دستگاه مناسب مربوط به {selected_material} را انتخاب کنید", reply_markup=reply_markup)

async def handle_device_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""نمایش مدل‌های دستگاه انتخاب‌شده"""
    query = update.callback_query
    await query.answer()

    # استخراج اطلاعات دستگاه از callback_data
    _, material_id, device_index = query.data.split("_")
    material_id = int(material_id)
    device_index = int(device_index)

    # فیلتر دستگاه‌ها مرتبط با ماده انتخاب‌شده
    filtered_devices = devices_data[
        devices_data["کاربرد ID"]
        .apply(lambda x: str(material_id) in map(str.strip, str(x).split(",")))
    ].drop_duplicates(subset=["دستگاه"]).reset_index(drop= True)

    # بازیابی دستگاه انتخاب‌شده با ایندکس فیلتر شده
    selected_device = filtered_devices.loc[device_index, "دستگاه"]

    # ارسال پیام دستگاه انتخاب‌شده
    # await query.message.reply_text(f"شما دستگاه '{selected_device}' را انتخاب کردید.")

    # فیلتر مدل‌های مرتبط با دستگاه انتخاب‌شده
    device_models = devices_data[
        (devices_data["دستگاه"] == selected_device) &
        devices_data["کاربرد ID"].apply(lambda x: str(material_id) in map(str.strip, str(x).split(",")))
    ]

    # بررسی اینکه آیا مدل‌هایی برای دستگاه یافت شده‌اند
    if device_models.empty:
        await query.message.reply_text("مدل‌هایی برای این دستگاه یافت نشد.")
        return

    # ایجاد دکمه‌ها برای مدل‌های دستگاه
    keyboard = [
        [InlineKeyboardButton(f"{row['مدل']} - {'هوشمند' if row['هوشمند یا غیر هوشمند'] == 'هوشمند' else 'غیر هوشمند'}",
                              callback_data=f"model_{i}_{i}_{material_id}_{device_index}")]
        for i, row in device_models.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    keyboard.append([InlineKeyboardButton("بازگشت" , callback_data =  f"material_{material_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(f"مدل مربوط به دستگاه {selected_device} رو انتخاب کن", reply_markup=reply_markup)

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""نمایش گزینه‌های مدل انتخاب‌شده (ویژگی‌ها، معرفی و تفاوت)"""
    query = update.callback_query
    await query.answer()

    # استخراج اطلاعات مدل از callback_data
    _, device_id, model_id , material_id , device_index = query.data.split("_")
    device_id = int(device_id) 
    model_id = int(model_id) 
    # دریافت اطلاعات مدل
    selected_model = devices_data.loc[devices_data.index[model_id], "مدل"]
    selected_device = devices_data.loc[devices_data.index[device_id], "دستگاه"]

    # ارسال پیام مدل انتخاب‌شده
    # await query.message.reply_text(f"شما مدل '{selected_model}' از دستگاه '{selected_device}' را انتخاب کردید.")

    # نمایش گزینه‌ها
    keyboard = [
        [InlineKeyboardButton("ویژگی‌ها", callback_data=f"info_features_{model_id}")],
        [InlineKeyboardButton("معرفی", callback_data=f"info_intro_{model_id}")]
    ]

    # اضافه کردن گزینه تفاوت برای دستگاه فایبر
    if selected_device == "فایبر":
        keyboard.append([InlineKeyboardButton("تفاوت هوشمند و غیرهوشمند", callback_data=f"info_diff_{model_id}")])


    reply_markup = InlineKeyboardMarkup(keyboard)
    keyboard.append([InlineKeyboardButton("بازگشت" , callback_data =  f"device_{material_id}_{device_index}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(f"چی میخوای درباره مدل {selected_model} دستگاه {selected_device} بدونی؟؟", reply_markup=reply_markup)
async def handle_info_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""نمایش اطلاعات مرتبط با گزینه انتخاب‌شده (ویژگی‌ها، معرفی، تفاوت)"""
    query = update.callback_query
    await query.answer()

    # استخراج نوع اطلاعات و مدل از callback_data
    _, info_type, model_id = query.data.split("_")
    model_id = int(model_id) + 1
   
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
        filtered_data = differences_data[differences_data["تفاوت ID"] == 1]
        
        if not filtered_data.empty:
            content = filtered_data["توضیحات تفاوت"].iloc[0]
        else:
            content = "اطلاعات تفاوت موجود نیست."
    else:
        content = "اطلاعاتی در دسترس نیست."

    # ارسال پیام اطلاعات
    await query.message.reply_text(content)
# --- تنظیمات ربات ---
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_material_selection, pattern="^material_"))
application.add_handler(CallbackQueryHandler(handle_device_selection, pattern="^device_"))
application.add_handler(CallbackQueryHandler(welcome_message, pattern="^start_chat$"))
application.add_handler(CallbackQueryHandler(handle_model_selection, pattern="^model_"))
application.add_handler(CallbackQueryHandler(handle_info_request, pattern="^info_"))
application.add_handler(CommandHandler("support" , support))
# --- اجرا ---
if __name__ == "__main__":
    print("ربات در حال اجراست...")
    application.post_init = set_bot_commands
    application.run_polling()
