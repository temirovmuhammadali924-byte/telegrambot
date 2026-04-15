from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio

TOKEN = "8669155846:AAGye0XrqGP3qhX1jX-rYi1yTfEPp-puJIc"

# STICKER ID (o'zgartirsa ham bo'ladi)
STICKERS = {
    "excellent": "CAACAgIAAxkBAAEBQXNkY...",
    "good": "CAACAgIAAxkBAAEBQXVkY...",
    "bad": "CAACAgIAAxkBAAEBQXdkY..."
}

# SAVOLLAR
questions = [
    {"question": "Python nima?", "options": ["Dasturlash tili", "Oyin", "Telefon", "Kompyuter"], "answer": "Dasturlash tili"},
    {"question": "HTML nima?", "options": ["Dasturlash tili", "Belgilash tili", "Oyin", "Server"], "answer": "Belgilash tili"},
    {"question": "CSS nima?", "options": ["Dizayn tili", "Database", "Server", "Oyin"], "answer": "Dizayn tili"},
    {"question": "2 + 5 = ?", "options": ["6", "7", "8", "9"], "answer": "7"},
    {"question": "3 * 3 = ?", "options": ["6", "7", "8", "9"], "answer": "9"},
    {"question": "Telegram nima?", "options": ["Messenger", "Oyin", "Browser", "Server"], "answer": "Messenger"},
    {"question": "CPU nima?", "options": ["Miya", "Xotira", "Disk", "Monitor"], "answer": "Miya"},
    {"question": "RAM nima?", "options": ["Xotira", "Protsessor", "Disk", "Printer"], "answer": "Xotira"},
    {"question": "Internet nima?", "options": ["Tarmoq", "Kompyuter", "Oyin", "Telefon"], "answer": "Tarmoq"},
    {"question": "1 + 1 = ?", "options": ["1", "2", "3", "4"], "answer": "2"},
    {"question": "5 + 3 = ?", "options": ["7", "8", "9", "10"], "answer": "8"},
    {"question": "10 - 4 = ?", "options": ["5", "6", "7", "8"], "answer": "6"},
    {"question": "4 * 2 = ?", "options": ["6", "7", "8", "9"], "answer": "8"},
    {"question": "9 / 3 = ?", "options": ["2", "3", "4", "5"], "answer": "3"},
    {"question": "AI nima?", "options": ["Sun'iy intellekt", "Oyin", "Telefon", "Server"], "answer": "Sun'iy intellekt"}
]

user_data = {}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"score": 0, "q": 0}
    await update.message.reply_text("🚀 Test boshlandi!")
    await send_question(update, context)

# SAVOL
async def send_question(update, context):
    user = update.effective_user.id
    q_index = user_data[user]["q"]

    if q_index < len(questions):
        q = questions[q_index]

        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in q["options"]]

        msg = await update.message.reply_text(
            f"❓ Savol {q_index + 1}:\n{q['question']}\n⏱ 10 sekund",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # TIMER
        asyncio.create_task(timeout(update, context, msg.message_id, user))

    else:
        await finish(update, context)

# TIMEOUT
async def timeout(update, context, message_id, user):
    await asyncio.sleep(10)

    if user in user_data and user_data[user]["q"] < len(questions):
        user_data[user]["q"] += 1

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⏱ Vaqt tugadi!"
        )

        await send_question(update, context)

# JAVOB
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id
    q_index = user_data[user]["q"]
    correct = questions[q_index]["answer"]

    if query.data == correct:
        user_data[user]["score"] += 1
        text = "✅ To‘g‘ri!"
    else:
        text = f"❌ Noto‘g‘ri!\nTo‘g‘ri: {correct}"

    user_data[user]["q"] += 1

    await query.edit_message_text(text)

    if user_data[user]["q"] < len(questions):
        q = questions[user_data[user]["q"]]

        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in q["options"]]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❓ Savol {user_data[user]['q'] + 1}:\n{q['question']}\n⏱ 10 sekund",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await finish_callback(query, context)

# NATIJA
def result_text(score):
    total = len(questions)

    if score >= 12:
        grade = "🏆 A’lo"
        sticker = STICKERS["excellent"]
    elif score >= 7:
        grade = "👍 Yaxshi"
        sticker = STICKERS["good"]
    else:
        grade = "⚠️ Qoniqarli"
        sticker = STICKERS["bad"]

    text = f"🎉 Test tugadi!\n📊 {score}/{total}\n🎯 {grade}"

    return text, sticker

# FINISH
async def finish(update, context):
    user = update.effective_user.id
    score = user_data[user]["score"]

    text, sticker = result_text(score)

    keyboard = [[InlineKeyboardButton("🔄 Qayta boshlash", callback_data="restart")]]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    await update.message.reply_sticker(sticker)

# FINISH CALLBACK
async def finish_callback(query, context):
    user = query.from_user.id
    score = user_data[user]["score"]

    text, sticker = result_text(score)

    keyboard = [[InlineKeyboardButton("🔄 Qayta boshlash", callback_data="restart")]]

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await context.bot.send_sticker(
        chat_id=query.message.chat_id,
        sticker=sticker
    )

# RESTART
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data[query.from_user.id] = {"score": 0, "q": 0}

    await query.answer()
    await query.message.reply_text("🔄 Qayta boshlandi!")
    await send_question(query, context)

# APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
app.add_handler(CallbackQueryHandler(answer))

app.run_polling()