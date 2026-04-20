#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json

# ===== НАСТРОЙКИ =====
TOKEN = os.environ.get("TOKEN", "7533119660:AAHymK3kK8BvIKWsgeBYz0p44kwzy8gX-hc")
DATA_FILE = "/opt/render/project/src/user_data.json"
NOTES_FILE = "/opt/render/project/src/notes.json"

# ===== ЛОГИ =====
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== 40 ЗАДАНИЙ =====
TASKS = {
    1: """🌅 ДЕНЬ 1. РАЗМОРОЗКА

Задание: УТРЕННИЕ СТРАНИЦЫ

Возьми ручку и 3 листа бумаги.
Пиши всё, что приходит в голову.
Начни с фразы: «Я не знаю, что писать, но...»

Заполни 3 страницы. Не останавливайся.
Не перечитывай. Не исправляй ошибки.

🕒 25 минут.""" ,

    2: """🌅 ДЕНЬ 2. РУКА

Задание: СЛЕПОЙ РИСУНОК

Возьми лист бумаги и ручку.
Закрой глаза. Нащупай любой предмет рядом.
Рисуй его контур не глядя на лист. 5 минут.

Затем открой глаза и посмотри, что получилось.
Не оценивай «красиво/некрасиво». Просто смотри.

🕒 15 минут.""" ,

    3: """🌅 ДЕНЬ 3. ЗВУК

Задание: ЗВУКОВАЯ ПРОГУЛКА

Выйди на улицу или открой окно.
Закрой глаза на 10 минут.
Слушай. Не анализируй источники.
Просто собирай звуки, как собирают камни.

Запиши 3-5 звуков, которые запомнились.
Одним словом каждый. Например: «шорох», «гудок», «смех».

🕒 20 минут.""" ,

    4: """🌅 ДЕНЬ 4. ТЕЛО

Задание: ГДЕ ЖИВЁТ ЭМОЦИЯ

Сядь удобно. Закрой глаза.
Спроси себя: «Что я сейчас чувствую?»
Не думай. Жди ответа от тела.

Где в теле живёт это чувство?
Грудь? Живот? Горло? Плечи?

Положи туда руку. Побудь с этим 10 минут.
Ничего не меняй. Просто заметь.

🕒 20 минут.""" ,

    5: """🌅 ДЕНЬ 5. ПАМЯТЬ

Задание: ЗАПАХ ДЕТСТВА

Вспомни запах, который связан с детством.
Не событие — именно запах.
Бабушкин суп? Мокрый асфальт? Духи мамы? Книжная пыль?

Опиши его в 5 предложениях.
Не «пахло чем-то сладким», а «тёплый, дрожжевой, с кислинкой».

🕒 25 минут.""" ,

    6: """🌅 ДЕНЬ 6. ТЕНЬ

Задание: ПИСЬМО ТОМУ, ЧТО ТЫ ПОДАВЛЯЕШЬ

Вспомни качество, которое ты в себе не принимаешь.
Лень? Злость? Глупость? Хаотичность?

Напиши ему письмо. Начни так:
«Дорогая моя [Лень], я долго тебя прятала, но сегодня я хочу сказать...»

Не оправдывайся. Не обещай исправиться.
Просто дай этому качеству голос.

🕒 30 минут.""" ,

    7: """🌅 ДЕНЬ 7. ИТОГИ НЕДЕЛИ

Задание: ПИСЬМО СЕБЕ ПРОШЕДШЕЙ

Напиши письмо себе, которая начала этот путь 7 дней назад.
Что ты узнала? Что удивило? Что было трудно?
Что ты хочешь взять с собой дальше?

Никакой оценки «хорошо/плохо».
Только наблюдение.

🕒 25 минут."""
}

# ===== РАБОТА С ДАННЫМИ =====
def load_user_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
    return {"start_date": None, "current_day": 1, "completed_days": []}

def save_user_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

def load_notes():
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def save_note(text):
    notes = load_notes()
    notes.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "text": text
    })
    try:
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения заметки: {e}")

# ===== КОМАНДЫ =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    if user_data["start_date"] is None:
        user_data["start_date"] = date.today().isoformat()
        user_data["current_day"] = 1
        save_user_data(user_data)
        await update.message.reply_text(
            "🖤 ДОБРО ПОЖАЛОВАТЬ В X_LAB\n\n"
            "Твой путь начался сегодня.\n"
            "День 1 из 40.\n\n"
            "Напиши /today, чтобы получить первое задание.\n\n"
            "Ты не зритель. Ты — Автор."
        )
    else:
        await update.message.reply_text(
            f"🖤 С ВОЗВРАЩЕНИЕМ В X_LAB\n\n"
            f"Сегодня День {user_data['current_day']} из 40.\n\n"
            f"/today — задание дня\n"
            f"/progress — твой прогресс"
        )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("☀️ Задание дня", callback_data='today')],
        [InlineKeyboardButton("✅ Отметить выполнение", callback_data='done')],
        [InlineKeyboardButton("📊 Прогресс", callback_data='progress')],
        [InlineKeyboardButton("✍️ Новая заметка", callback_data='note')],
        [InlineKeyboardButton("📅 Сводка за неделю", callback_data='week')],
        [InlineKeyboardButton("⚓️ Якорь", callback_data='anchor')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧭 ВЫБЕРИ ДЕЙСТВИЕ:", reply_markup=reply_markup)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    day = user_data["current_day"]
    
    if day > 40:
        await update.message.reply_text(
            "🎉 ПОЗДРАВЛЯЮ!\n\n"
            "Ты прошла все 40 дней X_Lab.\n\n"
            "Ты больше не зритель. Ты — Автор.\n\n"
            "Что дальше? Решать тебе.\n"
            "Можешь продолжать оставлять заметки через /note."
        )
        return
    
    task = TASKS.get(day, f"🌅 ДЕНЬ {day}\n\nЗадание в разработке. Напиши /note и расскажи, что сейчас чувствуешь.")
    await update.message.reply_text(task)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    day = user_data["current_day"]
    
    if day > 40:
        await update.message.reply_text("Ты уже прошла все 40 дней. Ты — Автор.")
        return
    
    if day not in user_data["completed_days"]:
        user_data["completed_days"].append(day)
    
    if day < 40:
        user_data["current_day"] = day + 1
        save_user_data(user_data)
        await update.message.reply_text(
            f"✅ ДЕНЬ {day} ВЫПОЛНЕН\n\n"
            f"Ты сделала шаг. Завтра — День {day + 1}.\n\n"
            f"Хочешь посмотреть задание на завтра? Напиши /today"
        )
    else:
        user_data["current_day"] = 41
        save_user_data(user_data)
        await update.message.reply_text(
            "🎉 ДЕНЬ 40 ВЫПОЛНЕН!\n\n"
            "Ты прошла весь путь.\n"
            "Из зрителя — в Автора.\n\n"
            "Что теперь? Ты решаешь."
        )

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    day = user_data["current_day"]
    completed = len(user_data["completed_days"])
    
    if user_data["start_date"]:
        start = date.fromisoformat(user_data["start_date"])
        days_passed = (date.today() - start).days + 1
    else:
        days_passed = 0
    
    await update.message.reply_text(
        f"📊 ТВОЙ ПРОГРЕСС\n\n"
        f"Сегодня: День {day} из 40\n"
        f"Выполнено заданий: {completed}\n"
        f"Дней в пути: {days_passed}\n\n"
        f"{'🖤 Продолжай.' if day <= 40 else '🎉 Путь пройден.'}"
    )

async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Я СЛУШАЮ.\n\n"
        "Что сейчас внутри? Слова, образ, ощущение, звук.\n"
        "Отправь текстом, голосом или фото.\n"
        "Я сохраню это с датой."
    )
    context.user_data['awaiting_note'] = True

async def handle_note_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_note'):
        return
    
    if update.message.text:
        content = f"[Текст] {update.message.text[:500]}"
    elif update.message.photo:
        content = "[Фото]"
    elif update.message.voice:
        content = "[Голосовое сообщение]"
    else:
        content = "[Медиа]"
    
    save_note(content)
    context.user_data['awaiting_note'] = False
    await update.message.reply_text("✅ Принято. Сохранено в твоей лаборатории.")

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = load_notes()
    if not notes:
        await update.message.reply_text("📭 Заметок пока нет. Начни с /note")
        return
    
    recent = notes[-7:] if len(notes) >= 7 else notes
    summary = "📅 ПОСЛЕДНИЕ ЗАМЕТКИ:\n\n"
    for n in recent:
        summary += f"[{n['date']}] {n['text']}\n"
    
    summary += f"\n🔍 ВСЕГО ЗАМЕТОК: {len(notes)}"
    summary += "\n\n💬 Чтобы проанализировать — скопируй это и отправь в ChatGPT."
    
    await update.message.reply_text(summary)

async def anchor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚓️ ЯКОРЬ\n\n"
        "\"Иногда поиск — это просто отсрочка. Найденное ждёт там, где ты перестала искать.\"\n\n"
        "Ты не комментатор. Ты — автор.\n"
        "Дыши. Ты здесь. Ты в процессе."
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = {"start_date": None, "current_day": 1, "completed_days": []}
    save_user_data(user_data)
    await update.message.reply_text("🔄 Прогресс сброшен. Напиши /start, чтобы начать заново.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'today':
        await today(query.message, context)
    elif query.data == 'done':
        await done(query.message, context)
    elif query.data == 'progress':
        await progress(query.message, context)
    elif query.data == 'note':
        await query.message.reply_text("📝 Отправь текстом, голосом или фото. Я сохраню.")
        context.user_data['awaiting_note'] = True
    elif query.data == 'week':
        await week(query.message, context)
    elif query.data == 'anchor':
        await anchor(query.message, context)

# ===== ЗАПУСК =====
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("note", note_command))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("anchor", anchor))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VOICE, handle_note_content))
    
    logger.info("✅ X_Lab запущен с автоматическим счётчиком дней")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
