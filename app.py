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
            send_message(chat_id, "✏️ Назва категорії (можна з емодзі):")
            return "ok"

        if state == "add_category":
            categories[text] = {}
            save_data()
            admin_state.pop(chat_id)
            send_message(chat_id, f"✅ Додано: <b>{text}</b>", admin_menu())
            return "ok"

        if text == "➕ Додати підкатегорію":
            admin_state[chat_id] = "choose_category"
            send_message(chat_id, "✏️ Введіть категорію:")
            return "ok"

        if state == "choose_category":
            if text not in categories:
                send_message(chat_id, "❌ Такої категорії нема")
                return "ok"
            admin_state[chat_id] = f"add_sub:{text}"
            send_message(chat_id, "✏️ Назва підкатегорії:")
            return "ok"

        if state and state.startswith("add_sub:"):
            cat = state.split(":")[1]
            categories[cat][text] = []
            save_data()
            admin_state.pop(chat_id)
            send_message(chat_id, f"✅ Додано <b>{text}</b>", admin_menu())
            return "ok"

        if text == "🗑 Видалити категорію":
            admin_state[chat_id] = "delete_category"
            send_message(chat_id, "✏️ Назва категорії:")
            return "ok"

        if state == "delete_category":
            if text not in categories:
                send_message(chat_id, "❌ Такої категорії нема")
                return "ok"
            categories.pop(text)
            save_data()
            admin_state.pop(chat_id)
            send_message(chat_id, f"🗑 Видалено <b>{text}</b>", admin_menu())
            return "ok"

        if text == "🗑 Видалити підкатегорію":
            admin_state[chat_id] = "del_sub_cat"
            send_message(chat_id, "✏️ Введіть категорію:")
            return "ok"

        if state == "del_sub_cat":
            if text not in categories:
                send_message(chat_id, "❌ Такої категорії нема")
                return "ok"
            admin_state[chat_id] = f"del_sub:{text}"
            send_message(chat_id, "✏️ Назва підкатегорії:")
            return "ok"

        if state and state.startswith("del_sub:"):
            cat = state.split(":")[1]
            if text not in categories[cat]:
                send_message(chat_id, "❌ Такої підкатегорії нема")
                return "ok"
            categories[cat].pop(text)
            save_data()
            admin_state.pop(chat_id)
            send_message(chat_id, f"🗑 Видалено <b>{text}</b>", admin_menu())
            return "ok"

    # ----- USER NAVIGATION -----
    if text in categories:
        send_message(chat_id, f"📂 {text}", build_keyboard(categories[text].keys()))
        return "ok"

    for cat, subs in categories.items():
        if text in subs:
            send_message(
                chat_id,
                f"ℹ️ <b>{text}</b>\n\n🔗 Переглянути лікаря та залишити відгук у каналі",
                {
                    "inline_keyboard": [[
                        {"text": "💬 Перейти в каталог", "url": "https://t.me/your_channel"}
                    ]]
                }
            )
            return "ok"

    send_message(chat_id, "⬅ Оберіть розділ", main_menu())
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
