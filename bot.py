import telebot
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
import time
import requests

# API kalitlarni Environment Variables orqali olamiz (Xavfsizlik uchun)
TOKEN = os.environ.get("TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_KEY)

# O'quv dasturi asosida tizim ko'rsatmasi
system_instruction = """
Sen professional ingliz tili o'qituvchisi va yordamchi AIsan. O'quvchingning maqsadi maxsus dastur asosida noldan C2 darajagacha chiqish.

Sening asosiy vazifalaring:
1. DASTUR BO'YICHA O'QITISH: Har kuni dars boshlashdan oldin avvalgi darsni baholash uchun 3-4 ta qisqa savol berasan. To'g'ri topshirilsa, yangi mavzuni o'tasan.
2. LUG'AT: Dars oxirida yodlash uchun 20 ta eng ko'p ishlatiladigan so'z berasan va keyingi darsda ularni so'raysan.
3. SAVOLLARGA JAVOB BERISH: O'quvchi darsdan tashqari vaqtda istalgan savol bersa (masalan, "Present Perfect bilan Past Simple farqi nima?", "Shu gapni qanday tarjima qilaman?"), unga batafsil, tushunarli va do'stona javob berasan. U xato qilsa, to'g'rilaysan.
4. SHAXSIY YONDASHUV: O'quvchiga ingliz tili qoidalarini yoki yangi so'zlarni tushuntirayotganda, misollarni tibbiyot, inson anatomiyasi, biologik jarayonlar (masalan, oqsillar funksiyasi) yoki o'zbek adabiyotidagi hayotiy mavzularga bog'lab tushuntir. Bu unga mavzuni chuqurroq his qilishiga yordam beradi.

Muloqot tili: O'zbek tili. Doim qo'llab-quvvatlovchi va rag'batlantiruvchi ohangda gapir.
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

