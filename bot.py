import telebot
import os
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# API kalitlarni Environment Variables orqali olamiz (Xavfsizlik uchun)
TOKEN = os.environ.get("TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_KEY)

# O'quv dasturi asosida tizim ko'rsatmasi
system_instruction = """
Sen professional ingliz tili o'qituvchisisan. O'quvchingning dasturi quyidagicha:
1. [span_0](start_span)A1-A2: To be, Present Simple/Continuous, Past Simple, artikllar[span_0](end_span).
2. [span_1](start_span)[span_2](start_span)B1-B2: Present Perfect, Passive Voice, Conditionals, Gerund/Infinitive[span_1](end_span)[span_2](end_span).
3. [span_3](start_span)[span_4](start_span)C1-C2: Advanced Passives, Inversion, Idioms va tibbiy etika lug'ati[span_3](end_span)[span_4](end_span).

Vazifang:
- [span_5](start_span)Har kuni 20:00da yangi mavzu o'tish[span_5](end_span).
- Darsdan oldin 3-4 savol bilan o'zlashtirishni tekshirish.
- Har dars oxirida 20 ta eng ko'p ishlatiladigan so'z berish.
- O'quvchi savol bersa, AI kabi batafsil tushuntirish. Misollarni tibbiyot yoki adabiyotga bog'la.
Muloqot tili: O'zbek tili.
"""

model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
chats = {}

def get_chat(chat_id):
    if chat_id not in chats:
        chats[chat_id] = model.start_chat(history=[])
    return chats[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Men sizning shaxsiy o'qituvchingizman. Har kuni 20:00da dars o'tamiz.")

@bot.message_handler(func=lambda message: True)
def handle_questions(message):
    chat_session = get_chat(message.chat.id)
    response = chat_session.send_message(message.text)
    bot.reply_to(message, response.text, parse_mode='Markdown')

def daily_lesson():
    # Bu yerda foydalanuvchilarga dars yuborish mantiqi bo'ladi
    pass

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Tashkent'))
scheduler.add_job(daily_lesson, 'cron', hour=20, minute=0)
scheduler.start()

bot.infinity_polling()

