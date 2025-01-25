import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes, Application

# --- خواندن فایل اکسل ---

file_normalized = "output.xlsx"

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
    keyboard = [[InlineKeyboardButton("انتخاب متریال", callback_data="start_chat")]]
    keyboard.append([InlineKeyboardButton("پشتیبانی", url="https://t.me/Support_ID")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("بزن روی دکمه زیر تا توی خریدت بهت کمک کنم", reply_markup=reply_markup)

async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "یکی از موارد زیر رو که میخوای روش حکاکی کنی انتخاب کن تا توی انتخاب دستگاه بهت کمک کنم:"
    )

    materials = get_applications()
    keyboard = [[InlineKeyboardButton(material, callback_data=f"material_{i+1}")] for i, material in enumerate(materials)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً ماده مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def handle_material_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""نمایش دستگاه‌های مرتبط با ماده انتخاب‌شده"""
    query = update.callback_query
    await query.answer()  # ارسال پاسخ برای جلوگیری از timeout

    # استخراج ماده انتخاب‌شده از callback_data
    material_id = int(query.data.split("_")[1])
    selected_material = applications_data.loc[material_id - 1, "ماده"]

    # ارسال پیام ماده انتخاب‌شده
    await query.message.reply_text(f"شما '{selected_material}' را انتخاب کردید.")

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
    await query.message.reply_text("لطفاً دستگاه مناسب را انتخاب کنید:", reply_markup=reply_markup)

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
    ].drop_duplicates(subset=["دستگاه"]).reset_index(drop=True)

    # بازیابی دستگاه انتخاب‌شده با ایندکس فیلتر شده
    selected_device = filtered_devices.loc[device_index, "دستگاه"]

    # ارسال پیام دستگاه انتخاب‌شده
    await query.message.reply_text(f"شما دستگاه '{selected_device}' را انتخاب کردید.")

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
                              callback_data=f"model_{material_id}_{i}")]
        for i, row in device_models.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً مدل دستگاه را انتخاب کنید:", reply_markup=reply_markup)
# --- تنظیمات ربات ---
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_material_selection, pattern="^material_"))
application.add_handler(CallbackQueryHandler(handle_device_selection, pattern="^device_"))
application.add_handler(CallbackQueryHandler(welcome_message, pattern="^start_chat$"))
print("www")
# --- اجرا ---
if __name__ == "__main__":
    print("ربات در حال اجراست...")
    application.run_polling()