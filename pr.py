# import asyncio
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes , Application

# --- خواندن فایل اکسل ---
file_path = "lazer.com.xlsx"

# شیت‌های مختلف را بارگذاری می‌کنیم
devices_data = pd.read_excel(file_path, sheet_name="اطلاعات کلی")
applications_data = pd.read_excel(file_path, sheet_name="کاربرد ها")
features_data = pd.read_excel(file_path, sheet_name="ویژگی")
introductions_data = pd.read_excel(file_path, sheet_name="معرفی")
differences_data = pd.read_excel(file_path, sheet_name="تفاوت")

# --- مقداردهی اولیه ---
TOKEN = '7980217172:AAFuQy4Gv9wYqtm42zxbRyh9zh89oWfHqMM'

# --- تعریف توابع کمکی ---
def get_applications():
#"""بازگرداندن لیست مواد و کاربردها"""
    return applications_data["ماده "].tolist()

def get_devices_by_application(application_id):
#"""بازگرداندن دستگاه‌های مرتبط با یک ماده مشخص"""
    filtered_devices = devices_data[devices_data["ID کاربرد"].astype(str).str.contains(str(application_id))]
    return filtered_devices[["دستگاه", "نوع دستگاه", "مدل"]].drop_duplicates()

# --- راه‌اندازی بات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#"""نمایش دکمه شروع"""
    keyboard = [[InlineKeyboardButton("انتخاب متریال", callback_data="start_chat")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("بزن روی دکمه زیر تا بهت توی خرید دستگاه مد نظرت کمک کنم", reply_markup=reply_markup)

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

# --- تنظیم برنامه ---
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(welcome_message, pattern="^start_chat$"))
application.add_handler(CallbackQueryHandler(handle_material_selection, pattern="^material_"))

# --- اجرا ---
if __name__ == "__main__":
    print("ربات در حال اجراست...")
    application.run_polling()