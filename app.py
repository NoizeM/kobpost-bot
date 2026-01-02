from flask import Flask, request
import requests
import json
import os

TOKEN = "8282597486:AAHV4fyHqc5QQjJ7y93vq0L63P9_bPtLqw8"
ADMIN_ID = 533251328
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

DATA_FILE = "data.json"
admin_state = {}

# ---------- DATA ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

categories = load_data()

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

def main_menu():
    if not categories:
        return {"keyboard": [["ℹ️ Каталог порожній"]], "resize_keyboard": True}
    return build_keyboard(categories.keys())

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

def send_message(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(f"{API_URL}/sendMessage", json=payload)

# ---------- WEBHOOK ----------
@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    state = admin_state.get(chat_id)

    # /start
    if text == "/start":
        send_message(chat_id, "📍 Каталог міста", main_menu())
        return "ok"

    # ADMIN
    if chat_id == ADMIN_ID and text == "/admin":
        send_message(chat_id, "⚙️ Адмінка", admin_menu())
        return "ok"

    # ----- ADMIN ACTIONS -----
    if chat_id == ADMIN_ID:

        if text == "⬅ Назад":
            admin_state.pop(chat_id, None)
            send_message(chat_id, "📍 Каталог міста", main_menu())
            return "ok"

        if text == "➕ Додати категорію":
            admin_state[chat_id] = "add_category"
            send_message(chat_id, "✏️ Назва кате
