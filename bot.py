from flask import Flask, request
import telebot
import requests
import json
import os
from datetime import datetime
import threading
import time

TOKEN = os.environ.get("TOKEN", "8617624370:AAHbRVLvYjnf-bdCk9J45iuVTVZVHnRfk1o")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "AIzaSyBHHUBryBB7oR-ykH1r8eoRQnPnnnuQ1WI")
RENDER_URL = os.environ.get("RENDER_URL", "")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ Xato: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    name = message.from_user.first_name
    users = load_users()
    if chat_id not in users:
        users[chat_id] = {
            "name": name,
            "level": "beginner",
            "tasks_done": 0,
            "reports": []
        }
        save_users(users)
    bot.send_message(
        message.chat.id,
        f"👋 Salom, *{name}*! Men sizning AI ingliz tili o'qituvchingizman! 🎓\n\n"
        "📌 *Imkoniyatlarim:*\n"
        "✅ Har kuni 20:00 da hisobot so'rayman\n"
        "✅ Matnlaringizni tekshiraman\n"
        "✅ Kunlik vazifalar beraman\n"
        "✅ Baholayman va tahlil qilaman\n\n"
        "📚 *Komandalar:*\n"
        "/task — Kunlik vazifa\n"
        "/check — Matn tekshirish\n"
        "/report — Hisobot yuborish\n"
        "/progress — Natijalarim\n"
        "/level — Daraja o'zgartirish",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['task'])
def give_task(message):
    chat_id = str(message.chat.id)
    users = load_users()
    user = users.get(chat_id, {})
    level = user.get("level", "beginner")
    name = user.get("name", "o'quvchi")
    bot.send_chat_action(message.chat.id, 'typing')
    prompt = f"""Sen professional ingliz tili o'qituvchisisan.
{name} uchun bugungi vazifa tayyorla. Daraja: {level}
1. 📝 Grammatika qoidasi + 5 ta mashq jumla
2. 📖 5 ta yangi so'z (tarjima + misol)
3. ✍️ Kichik yozish vazifasi
O'zbek tilida tushuntir, inglizcha misollar ber."""
    task = ask_gemini(prompt)
    if chat_id in users:
        users[chat_id]["tasks_done"] = users[chat_id].get("tasks_done", 0) + 1
        save_users(users)
    bot.send_message(message.chat.id, f"📚 *Bugungi vazifang:*\n\n{task}", parse_mode="Markdown")

@bot.message_handler(commands=['check'])
def check_ask(message):
    msg = bot.send_message(message.chat.id, "✏️ Tekshirishni istagan inglizcha matnni yuboring 👇")
    bot.register_next_step_handler(msg, check_text)

def check_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    prompt = f"""Sen ingliz tili o'qituvchisisan. Bu matnni tekshir:
"{message.text}"
1. ✅ To'g'ri qismlar
2. ❌ Xatolar (har birini tushuntir)
3. 💡 To'g'rilangan variant
4. ⭐ Baho (10 dan)
O'zbek tilida javob ber."""
    result = ask_gemini(prompt)
    bot.send_message(message.chat.id, f"🔍 *Tahlil:*\n\n{result}", parse_mode="Markdown")

@bot.message_handler(commands=['report'])
def ask_report(message):
    msg = bot.send_message(
        message.chat.id,
        "📊 *Kunlik hisobot*\n\n"
        "Quyidagilarni yozing:\n"
        "1️⃣ Bugun qancha vaqt o'rgandingiz?\n"
        "2️⃣ Nima o'rgandingiz?\n"
        "3️⃣ Qiyinchiliklar bo'ldimi?\n"
        "4️⃣ Vazifani bajardingizmi?\n\n"
        "Hammasini *bitta xabarda* yozing 👇",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, analyze_report)

def analyze_report(message):
    bot.send_chat_action(message.chat.id, 'typing')
    chat_id = str(message.chat.id)
    users = load_users()
    name = users.get(chat_id, {}).get("name", "o'quvchi")
    if chat_id in users:
        if "reports" not in users[chat_id]:
            users[chat_id]["reports"] = []
        users[chat_id]["reports"].append(message.text[:200])
        save_users(users)
    prompt = f"""Sen ingliz tili o'qituvchisisan.
O'quvchi: {name}
Hisobot: "{message.text}"
1. 📊 Tahlil qil
2. ⭐ Baho (10 dan)
3. 💪 Motivatsion so'zlar
4. 📌 Ertangi maslahat
O'zbek tilida javob ber."""
    analysis = ask_gemini(prompt)
    bot.send_message(message.chat.id, f"📈 *Hisobot tahlili:*\n\n{analysis}", parse_mode="Markdown")

@bot.message_handler(commands=['progress'])
def progress(message):
    chat_id = str(message.chat.id)
    users = load_users()
    user = users.get(chat_id, {})
    reports = len(user.get("reports", []))
    tasks = user.get("tasks_done", 0)
    level = user.get("level", "beginner")
    bot.send_message(
        message.chat.id,
        f"📊 *Natijalaringiz:*\n\n"
        f"👤 Ism: {user.get('name', '?')}\n"
        f"🎯 Daraja: {level}\n"
        f"📚 Vazifalar: {tasks} ta\n"
        f"📝 Hisobotlar: {reports} ta\n\n"
        f"{'🔥 Zo\'r! Davom eting!' if reports >= 5 else '💪 Har kun hisobot yuboring!'}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['level'])
def level_cmd(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("🟢 Beginner", callback_data="level_beginner"),
        telebot.types.InlineKeyboardButton("🟡 Elementary", callback_data="level_elementary")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("🔵 Intermediate", callback_data="level_intermediate"),
        telebot.types.InlineKeyboardButton("🔴 Advanced", callback_data="level_advanced")
    )
    bot.send_message(message.chat.id, "📊 Darajangizni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("level_"))
def set_level(call):
    chat_id = str(call.message.chat.id)
    level = call.data.replace("level_", "")
    users = load_users()
    if chat_id in users:
        users[chat_id]["level"] = level
        save_users(users)
    bot.answer_callback_query(call.id, f"✅ Daraja: {level}")
    bot.edit_message_text(
        f"✅ Darajangiz *{level}* ga o'rnatildi!\n/task bilan yangi vazifa oling.",
        call.message.chat.id, call.message.message_id,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    prompt = f"""Sen ingliz tili o'qituvchisisan.
Foydalanuvchi: "{message.text}"
- Inglizcha matn bo'lsa — grammatikasini tekshir
- O'zbekcha savol bo'lsa — ingliz tiliga oid javob ber
- Salomlashish bo'lsa — do'stona javob ber
O'zbek tilida javob ber."""
    response = ask_gemini(prompt)
    bot.send_message(message.chat.id, response)

# =====================
# KUNLIK 20:00 ESLATMA
# =====================
def daily_reminder():
    sent_today = False
    while True:
        now = datetime.now()
        if now.hour == 20 and now.minute == 0 and not sent_today:
            users = load_users()
            for chat_id, user in users.items():
                try:
                    bot.send_message(
                        int(chat_id),
                        f"🌙 *Kechqurungi hisobot vaqti!*\n\n"
                        f"Salom, *{user.get('name', '')}*! 👋\n\n"
                        f"Bugun ham ingliz tili bilan shug'ullandingizmi?\n\n"
                        f"📊 /report — Hisobot yuborish\n"
                        f"📚 /task — Ertangi vazifa\n"
                        f"📈 /progress — Natijalarim",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            sent_today = True
        if now.hour == 20 and now.minute == 1:
            sent_today = False
        time.sleep(30)

threading.Thread(target=daily_reminder, daemon=True).start()

# =====================
# WEBHOOK
# =====================
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return 'Bot ishlayapti! ✅'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
