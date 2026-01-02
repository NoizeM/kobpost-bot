import os
import json
import gspread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from google.oauth2.service_account import Credentials

print("=== BOT STARTED ===")

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = 533251328
SPREADSHEET_ID = "1DlZcHWX_Gjatf6Dfw6XIT7an4jRiED6K_ZgJwar0FhI"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("categories")

def load_categories():
    rows = sheet.get_all_records()
    cats = [r["category"] for r in rows if r.get("category")]
    return list(dict.fromkeys(cats))

def build_keyboard(items, row_size=2):
    kb, row = [], []
    for i in items:
        row.append(i)
        if len(row) == row_size:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cats = load_categories()
    if not cats:
        await update.message.reply_text("Каталог порожній")
        return
    await update.message.reply_text("📍 Каталог міста", reply_markup=build_keyboard(cats))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
