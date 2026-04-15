import telebot
from telebot import types
import time
import threading
import json
from datetime import datetime

TOKEN = "8771026096:AAHBh-H0KpCE2CFlG6MfEbWEwVXKnfoLJKw"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"


def load_tasks():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

            # 🔥 eski tasklarga status qo‘shamiz
            for t in data:
                if "status" not in t:
                    t["status"] = "⏳"

            return data
    except:
        return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f)


tasks = load_tasks()


# MENU
def menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("➕ Add", "📋 List")
    m.add("🗑 Delete", "✅ Done")
    m.add("📊 Stats", "📅 Today")
    return m


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "🔥 PRO DEADLINE BOT",
                     reply_markup=menu())


# BUTTON
@bot.message_handler(func=lambda m: True)
def handle(m):
    user_tasks = [t for t in tasks if t["chat_id"] == m.chat.id]

    if m.text == "➕ Add":
        bot.send_message(m.chat.id, "/add Math homework 2026-04-10 18:00")

    elif m.text == "📋 List":
        if not user_tasks:
            bot.send_message(m.chat.id, "📭 Bo‘sh")
            return

        text = "📋 Sening tasklaring:\n"
        for i, t in enumerate(user_tasks):
            text += f"{i+1}. {t['name']} - {t['time']} ({t['status']})\n"

        bot.send_message(m.chat.id, text)

    elif m.text == "🗑 Delete":
        bot.send_message(m.chat.id, "/delete 1")

    elif m.text == "✅ Done":
        bot.send_message(m.chat.id, "/done 1")

    elif m.text == "📊 Stats":
        total = len(user_tasks)
        done = len([t for t in user_tasks if t["status"] == "✅"])
        pending = len([t for t in user_tasks if t["status"] == "⏳"])

        bot.send_message(m.chat.id,
                         f"📊 Statistika:\nJami: {total}\nBajarilgan: {done}\nKutilmoqda: {pending}")

    elif m.text == "📅 Today":
        today = datetime.now().strftime("%Y-%m-%d")

        today_tasks = [t for t in user_tasks if t["time"].startswith(today)]

        if not today_tasks:
            bot.send_message(m.chat.id, "📭 Bugun yo‘q")
            return

        text = "📅 Bugungi tasklar:\n"
        for t in today_tasks:
            text += f"{t['name']} - {t['time']}\n"

        bot.send_message(m.chat.id, text)


# ADD
@bot.message_handler(commands=['add'])
def add_task(message):
    try:
        text = message.text.replace('/add ', '')
        parts = text.split(' ')

        name = " ".join(parts[:-2])
        date = parts[-2]
        time_ = parts[-1]

        deadline = datetime.strptime(date + " " + time_, "%Y-%m-%d %H:%M")

        task = {
            "name": name,
            "time": deadline.strftime("%Y-%m-%d %H:%M"),
            "chat_id": message.chat.id,
            "status": "⏳"
        }

        tasks.append(task)
        save_tasks(tasks)

        bot.send_message(message.chat.id, f"✅ Qo‘shildi: {name}")

    except:
        bot.send_message(message.chat.id, "❌ format xato")


# DELETE
@bot.message_handler(commands=['delete'])
def delete_task(message):
    try:
        index = int(message.text.split(' ')[1]) - 1

        user_tasks = [t for t in tasks if t["chat_id"] == message.chat.id]
        task = user_tasks[index]

        tasks.remove(task)
        save_tasks(tasks)

        bot.send_message(message.chat.id, "🗑 O‘chirildi")

    except:
        bot.send_message(message.chat.id, "❌ xato")


# DONE
@bot.message_handler(commands=['done'])
def done_task(message):
    try:
        index = int(message.text.split(' ')[1]) - 1

        user_tasks = [t for t in tasks if t["chat_id"] == message.chat.id]
        task = user_tasks[index]

        task["status"] = "✅"
        save_tasks(tasks)

        bot.send_message(message.chat.id, "🎉 Bajarildi!")

    except:
        bot.send_message(message.chat.id, "❌ xato")


# CHECK
def check_deadlines():
    while True:
        now = datetime.now()

        for task in tasks:

            # 🔥 himoya
            if "status" not in task:
                task["status"] = "⏳"

            task_time = datetime.strptime(task["time"], "%Y-%m-%d %H:%M")
            diff = (task_time - now).total_seconds()

            if 0 < diff < 600:
                bot.send_message(task["chat_id"],
                                 f"⏰ 10 min qoldi!\n{task['name']}")

            if diff < 0 and task["status"] == "⏳":
                bot.send_message(task["chat_id"],
                                 f"❌ O‘tib ketdi!\n{task['name']}")
                task["status"] = "❌"
                save_tasks(tasks)

        time.sleep(60)


thread = threading.Thread(target=check_deadlines)
thread.start()

bot.infinity_polling()
