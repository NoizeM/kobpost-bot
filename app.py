import os
import json
import gspread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from google.oauth2.service_account import Credentials

# ---------- CONFIG ----------
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = 533251328
SPREADSHEET_ID = "1DlZcHWX_Gjatf6Dfw6XIT7an4jRiED6K_ZgJwar0FhI"

# ---------- GOOGLE SHEETS ----------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("categories")

# ---------- HELPERS ----------
def load_categories():
    rows = sheet.get_all_records()
    categories = []
    for r in rows:
        if r.get("category"):
            categories.append(r["category"])
    return list(dict.fromkeys(categories))  # унікальні

def build_keyboard(items, row_size=2):
    keyboard, row = [], []
    for item in items:
        row.append(item)
        if len(row) == row_size:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = load_categories()

    if not categories:
        await update.message.reply_text("Каталог порожній")
        return

    await update.message.reply_text(
        "📍 Каталог міста",
        reply_markup=build_keyboard(categories)
    )

# ---------- MAIN ----------
def main():
    print("=== BOT STARTED ===")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
