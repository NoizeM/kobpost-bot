print("=== BOT STARTED ===")

from flask import Flask, request
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# ---------- CONFIG ----------
TOKEN = "8282597486:AAHV4fyHqc5QQjJ7y93vq0L63P9_bPtLqw8"
ADMIN_ID = 533251328
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)
admin_state = {}

# ---------- GOOGLE SHEETS ----------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key("1DlZcHWX_Gjatf6Dfw6XIT7an4jRiED6K_ZgJwar0FhI")
sheet = spreadsheet.worksheet("categories")


# ---------- DATA ----------
def load_categories():
    rows = sheet.get_all_records()
    data = {}
    for r in rows:
        cat = r["category"]
        sub = r["subcategory"]
        if cat not in data:
            data[cat] = {}
        if sub:
            data[cat][sub] = []
    return data

def add_category(cat):
    sheet.append_row([cat, ""])

def add_subcategory(cat, sub):
    sheet.append_row([cat, sub])

def delete_category(cat):
    rows = sheet.get_all_values()
    sheet.clear()
    sheet.append_row(["category", "subcategory"])
    for r in rows[1:]:
        if r[0] != cat:
            sheet.append_row(r)

def delete_subcategory(cat, sub):
    rows = sheet.get_all_values()
    sheet.clear()
    sheet.append_row(["category", "subcategory"])
    for r in rows[1:]:
        if not (r[0] == cat and r[1] == sub):
            sheet.append_row(r)

# ---------- UI ----------
def build_keyboard(items, row_size=2):
    keyboard, row = [], []
    for item in items:
        row.append(item)
        if len(row) == row_size:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return {"keyboard": keyboard, "resize_keyboard": True}

def admin_menu():
    return {
        "keyboard": [
            ["➕ Додати категорію"],
            ["➕ Додати підкатегорію"],
            ["🗑 Видалити категорію"],
            ["🗑 Видалити підкатегорію"],
            ["⬅ Назад"]
        ],
        "resize_keyboard": True
    }

def send(chat_id, text, kb=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if kb:
        payload["reply_markup"] = kb
    requests.post(f"{API_URL}/sendMessage", json=payload)

# ---------- WEBHOOK ----------
@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    state = admin_state.get(chat_id)

    categories = load_categories()

    # START
    if text == "/start":
        send(chat_id, "📍 Каталог міста", build_keyboard(categories.keys()))
        return "ok"

    # ADMIN PANEL
    if chat_id == ADMIN_ID and text == "/admin":
        send(chat_id, "⚙️ Адмінка", admin_menu())
        return "ok"

    # ---------- ADMIN ----------
    if chat_id == ADMIN_ID:

        if text == "⬅ Назад":
            admin_state.pop(chat_id, None)
            send(chat_id, "📍 Каталог міста", build_keyboard(categories.keys()))
            return "ok"
