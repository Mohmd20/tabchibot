# import asyncio
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes , Application

# --- خواندن فایل اکسل ---
file_path = "lazer.com.xlsx"

# شیت‌های مختلف را بارگذاری می‌کنیم
allsheets = pd.read_excel(file_path,sheet_name=None)

for sheet, df in allsheets.items():
    df.columns = df.columns.str.strip()
    allsheets[sheet] = df
with pd.ExcelWriter("output.xlsx") as writer:
    for sheet_name , df in allsheets.items():
        df.to_excel(writer,sheet_name=sheet_name,index=False)

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
#"""بازگرداندن لیست مواد و کاربردها"""
    return applications_data["ماده"].tolist()

def get_devices_by_application(application_id):
#"""بازگرداندن دستگاه‌های مرتبط با یک ماده مشخص"""
    filtered_devices = devices_data[devices_data["ID کاربرد"].astype(str).str.contains(str(application_id))]
    return filtered_devices[["دستگاه", "نوع دستگاه", "مدل"]].drop_duplicates()

# --- راه‌اندازی بات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#"""نمایش دکمه شروع"""
    keyboard = [[InlineKeyboardButton("انتخاب متریال", callback_data="start_chat")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("بزن روی دکمه زیر تا توی خریدت بهت کمک کنم", reply_markup=reply_markup)

async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#"""ارسال پیام خوش‌آمدگویی و نمایش مواد اولیه"""
    query = update.callback_query
    await query.answer() # ارسال پاسخ برای جلوگیری از timeout

# ارسال پیام خوش‌آمدگویی
    await query.message.reply_text(
"یکی از موارد زیر رو که میخوای روش حکاکی کنی انتخاب کن تا توی انتخاب دستگاه بهت کمک کنم:"
)

# نمایش مواد اولیه به‌عنوان دکمه
    materials = get_applications()
    keyboard = [[InlineKeyboardButton(material, callback_data=f"material_{i+1}")] for i, material in enumerate(materials)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً ماده مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def handle_material_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
#"""نمایش دستگاه‌های مرتبط با ماده انتخاب‌شده"""
    query = update.callback_query
    await query.answer() # ارسال پاسخ برای جلوگیری از timeout

# استخراج ماده انتخاب‌شده از callback_data
    material_id = int(query.data.split("_")[1])
    selected_material = applications_data.loc[material_id - 1, "مواد"]

# ارسال پیام ماده انتخاب‌شده
    await query.message.reply_text(f"شما '{selected_material}' را انتخاب کردید.")

# نمایش دستگاه‌های مرتبط
    devices = get_devices_by_application(material_id)
    keyboard = [[InlineKeyboardButton(f"{row['دستگاه']} - {row['نوع دستگاه']}",
    callback_data=f"device_{material_id}_{i}")] for i, row in devices.iterrows()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً دستگاه مناسب را انتخاب کنید:", reply_markup=reply_markup)

async def handle_device_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش مدل‌های دستگاه انتخاب‌شده"""
    query = update.callback_query
    await query.answer()

    # استخراج اطلاعات دستگاه از callback_data
    _, material_id, device_id = query.data.split("_")
    material_id = int(material_id)
    device_id = int(device_id)

    # دریافت نام دستگاه
    selected_device = devices_data.loc[device_id - 1, "دستگاه"]

    # ارسال پیام دستگاه انتخاب‌شده
    await query.message.reply_text(f"شما دستگاه '{selected_device}' را انتخاب کردید.")

    # نمایش مدل‌های دستگاه
    device_models = devices_data[(devices_data["ID کاربرد"] == material_id) & (devices_data["دستگاه"] == selected_device)]
    keyboard = [[InlineKeyboardButton(row["مدل"], callback_data=f"model_{device_id}_{i}")]
                for i, row in device_models.iterrows()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً مدل دستگاه را انتخاب کنید:", reply_markup=reply_markup)

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش گزینه‌های مدل انتخاب‌شده (کاربردها، ویژگی‌ها، معرفی)"""
    query = update.callback_query
    await query.answer()

    # استخراج اطلاعات مدل از callback_data
    _, device_id, model_id = query.data.split("_")
    device_id = int(device_id)
    model_id = int(model_id)

    # دریافت اطلاعات مدل
    selected_model = devices_data.loc[model_id - 1, "مدل"]
    selected_device = devices_data.loc[device_id - 1, "دستگاه"]

    # ارسال پیام مدل انتخاب‌شده
    await query.message.reply_text(f"شما مدل '{selected_model}' از دستگاه '{selected_device}' را انتخاب کردید.")

    # نمایش گزینه‌ها
    keyboard = [
        [InlineKeyboardButton("کاربردها", callback_data=f"info_applications_{model_id}")],
        [InlineKeyboardButton("ویژگی‌ها", callback_data=f"info_features_{model_id}")],
        [InlineKeyboardButton("معرفی", callback_data=f"info_intro_{model_id}")]
    ]

    # اضافه کردن گزینه تفاوت هوشمند و غیرهوشمند برای دستگاه فایبر
    if selected_device == "فایبر":
        keyboard.append([InlineKeyboardButton("تفاوت هوشمند و غیرهوشمند", callback_data=f"info_diff_{model_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)

async def handle_info_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات مرتبط با گزینه انتخاب‌شده"""
    query = update.callback_query
    await query.answer()

    # استخراج نوع اطلاعات و مدل از callback_data
    _, info_type, model_id = query.data.split("_")
    model_id = int(model_id)

    # دریافت اطلاعات متناسب با نوع انتخاب‌شده
    if info_type == "applications":
        content = features_data.loc[features_data["ID مدل"] == model_id, "کاربرد"].iloc[0]
    elif info_type == "features":
        content = features_data.loc[features_data["ID مدل"] == model_id, "ویژگی"].iloc[0]
    elif info_type == "intro":
        content = introductions_data.loc[introductions_data["ID مدل"] == model_id, "معرفی"].iloc[0]
    elif info_type == "diff":
        content = differences_data.loc[differences_data["ID مدل"] == model_id, "تفاوت"].iloc[0]
    else:
        content = "اطلاعاتی در دسترس نیست."

    # ارسال پیام اطلاعات
    await query.message.reply_text(content)

# --- افزودن هندلرهای جدید ---
# --- تنظیم برنامه ---
application = Application.builder().token(TOKEN).build()
application.add_handler(CallbackQueryHandler(handle_device_selection, pattern="^device_"))
application.add_handler(CallbackQueryHandler(handle_model_selection, pattern="^model_"))
application.add_handler(CallbackQueryHandler(handle_info_request, pattern="^info_"))
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(welcome_message, pattern="^start_chat$"))
application.add_handler(CallbackQueryHandler(handle_material_selection, pattern="^material_"))

# --- اجرا ---
if __name__ == "__main__":
    print("ربات در حال اجراست...")
    application.run_polling()