from flask import Flask, request
import requests

TOKEN = "8282597486:AAHV4fyHqc5QQjJ7y93vq0L63P9_bPtLqw8"
ADMIN_ID = 533251328
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# ====== ДАНІ ======
categories = {}
admin_state = {}

# ====== ДОПОМІЖНІ ======
def send_message(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(f"{API_URL}/sendMessage", json=payload)


def main_menu():
    return {
        "keyboard": [[name] for name in categories.keys()],
        "resize_keyboard": True
    }


def admin_menu():
    return {
        "keyboard": [
            ["➕ Додати категорію"],
            ["➕ Додати підкатегорію"],
            ["➕ Додати контакт"],
            ["⬅ Назад"]
        ],
        "resize_keyboard": True
    }


# ====== WEBHOOK ======
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # ===== START =====
    if text == "/start":
        send_message(
            chat_id,
            "👋 <b>Міський довідник Кобеляк</b>\n\nОберіть категорію 👇",
            main_menu()
        )
        return "ok"

    # ===== ADMIN =====
    if text == "/admin" and chat_id == ADMIN_ID:
        send_message(chat_id, "⚙️ <b>Адмінка</b>", admin_menu())
        return "ok"

    # ===== АДМІН ЛОГІКА =====
    if chat_id == ADMIN_ID:
        state = admin_state.get(chat_id)

        if text == "➕ Додати категорію":
            admin_state[chat_id] = "add_category"
            send_message(chat_id, "✏️ Введіть назву категорії:")
            return "ok"

        if state == "add_category":
            categories[text] = {}
            admin_state.pop(chat_id)
            send_message(chat_id, f"✅ Категорія <b>{text}</b> додана", admin_menu())
            return "ok"

        if text == "➕ Додати підкатегорію":
            admin_state[chat_id] = "choose_category"
            send_message(chat_id, "✏️ Введіть назву категорії:")
            return "ok"

        if state == "choose_category":
            if text not in categories:
                send_message(chat_id, "❌ Такої категорії нема")
                return "ok"
            admin_state[chat_id] = f"add_sub:{text}"
            send_message(chat_id, "✏️ Введіть назву підкатегорії:")
            return "ok"

        if state and state.startswith("add_sub:"):
            cat = state.split(":")[1]
            categories[cat][text] = []
            admin_state.pop(chat_id)
            send_message(chat_id, f"✅ Підкатегорія <b>{text}</b> додана", admin_menu())
            return "ok"

        if text == "➕ Додати контакт":
            admin_state[chat_id] = "contact_category"
            send_message(chat_id, "✏️ Введіть категорію:")
            return "ok"

        if state == "contact_category":
            if text not in categories:
                send_message(chat_id, "❌ Нема такої категорії")
                return "ok"
            admin_state[chat_id] = f"contact_sub:{text}"
            send_message(chat_id, "✏️ Введіть підкатегорію:")
            return "ok"

        if state and state.startswith("contact_sub:"):
            cat = state.split(":")[1]
            if text not in categories[cat]:
                send_message(chat_id, "❌ Нема такої підкатегорії")
                return "ok"
            admin_state[chat_id] = f"contact_data:{cat}:{text}"
            send_message(chat_id, "✏️ Введіть контакт (імʼя, телефон, опис, посилання):")
            return "ok"

        if state and state.startswith("contact_data:"):
            _, cat, sub = state.split(":")
            categories[cat][sub].append(text)
            admin_state.pop(chat_id)
            send_message(chat_id, "✅ Контакт додано", admin_menu())
            return "ok"

    # ===== КОРИСТУВАЧ =====
    if text in categories:
        subs = categories[text]
        keyboard = {"keyboard": [[s] for s in subs], "resize_keyboard": True}
        send_message(chat_id, f"📂 <b>{text}</b>", keyboard)
        return "ok"

    for cat, subs in categories.items():
        if text in subs:
            items = subs[text]
            if not items:
                send_message(chat_id, "ℹ️ Поки що порожньо")
            else:
                send_message(chat_id, "\n\n".join(items))
            return "ok"

    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Bot is running"
