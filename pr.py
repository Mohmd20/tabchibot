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
#"""شروع مکالمه و نمایش مواد اولیه"""
    update.message.reply_text("reza kocholo")
    materials = get_applications()
    keyboard = [[InlineKeyboardButton(material, callback_data=f"material_{i+1}")]
    for i, material in enumerate(materials)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً ماده مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

# --- تنظیم برنامه ---
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))

# async def main():
#     print("ربات در حال اجراست ....")
#     await application.start
#     await application.updater.start_polling()
#     await application.updater.stop()
#     await application.stop()
# if __name__ == "__main__":
#     asyncio.run(main())
# --- اجرا ---
print(applications_data.columns)
if __name__ == "__main__":
    print("ربات در حال اجراست...")
    application.run_polling()