import os
import requests
import telebot

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_BASE = "http://127.0.0.1:8000/api"
DJANGO_USERNAME = os.environ["DJANGO_USERNAME"]
DJANGO_PASSWORD = os.environ["DJANGO_PASSWORD"]

bot = telebot.TeleBot(BOT_TOKEN)
_cached_access = None


def get_access_token():
    global _cached_access
    if _cached_access:
        return _cached_access

    r = requests.post(
        f"{API_BASE}/jwt/create/",
        json={"username": DJANGO_USERNAME, "password": DJANGO_PASSWORD},
        timeout=30,
    )
    r.raise_for_status()
    _cached_access = r.json()["access"]
    return _cached_access


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Привет! Команда: /mycats")


@bot.message_handler(commands=["mycats"])
def mycats(message):
    token = get_access_token()
    r = requests.get(
        f"{API_BASE}/cats/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    if isinstance(payload, dict):
        cats = payload.get("results", [])
    elif isinstance(payload, list):
        cats = payload
    else:
        cats = []

    if not cats:
        bot.reply_to(message, "Пока нет котиков.")
        return

    text = "\n".join(f"{c['id']}: {c['name']} ({c['color']})" for c in cats)
    bot.reply_to(message, text)


if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)