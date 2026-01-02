from flask import Flask, request
import requests

TOKEN = "8282597486:AAHV4fyHqc5QQjJ7y93vq0L63P9_bPtLqw8"
ADMIN_ID = 533251328
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)


def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    requests.post(f"{API_URL}/sendMessage", json=payload)


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "ok"

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            keyboard = {
                "keyboard": [
                    ["🏥 Лікарня", "🚕 Таксі"],
                    ["🚌 Графік автобусів", "🏠 Житло"],
                    ["☕ Відпочинок", "🐾 Ветеринари"]
                ],
                "resize_keyboard": True
            }

            send_message(
                chat_id,
                "👋 <b>Вітаємо!</b>\n\n"
                "Це міський бот корисних контактів Кобеляк.\n"
                "Оберіть потрібну категорію 👇",
                keyboard
            )
        else:
            send_message(chat_id, "ℹ️ Скористайтесь меню нижче 👇")

    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "Bot is running"
