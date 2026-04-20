#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json

# ===== НАСТРОЙКИ =====
TOKEN = os.environ.get("TOKEN", "7533119660:AAHymK3kK8BvIKWsgeBYz0p44kwzy8gX-hc")
NOTES_FILE = "/opt/render/project/src/notes.json"

# ===== ЛОГИ =====
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== РАБОТА С ЗАМЕТКАМИ =====
def load_notes():
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки заметок: {e}")
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
    await update.message.reply_text(
        "🖤 ДОБРО ПОЖАЛОВАТЬ В X_LAB\n\n"
        "Ты находишься в точке, где анализ закончился, а действие ещё не началось.\n\n"
        "Здесь:\n"
        "— Ежедневное творческое задание на 25 минут\n"
        "— Дневник наблюдений в любом формате\n"
        "— Сводка раз в неделю\n\n"
        "Ты не зритель. Ты — Автор.\n\n"
        "/menu — панель управления\n"
        "/today — задание дня\n"
        "/note — оставить заметку\n"
        "/week — сводка за 7 дней\n"
        "/anchor — якорь (напоминание о себе)"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("☀️ Задание дня", callback_data='today')],
        [InlineKeyboardButton("✍️ Новая заметка", callback_data='note')],
        [InlineKeyboardButton("📊 Сводка за неделю", callback_data='week')],
        [InlineKeyboardButton("⚓️ Якорь", callback_data='anchor')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧭 ВЫБЕРИ ДЕЙСТВИЕ:", reply_markup=reply_markup)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🌅 ДЕНЬ 1 ИЗ 40. РАЗМОРОЗКА

Задание: УТРЕННИЕ СТРАНИЦЫ

Возьми ручку и 3 листа бумаги.
Пиши всё, что приходит в голову.
Начни с фразы: «Я не знаю, что писать, но...»

Заполни 3 страницы. Не останавливайся.
Не перечитывай. Не исправляй ошибки.

🕒 25 минут.

Когда закончишь — напиши /done"""
    await update.message.reply_text(text)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ День 1 выполнен. Ты сделала шаг. Завтра — следующий.")

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'today':
        await today(query.message, context)
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
    app.add_handler(CommandHandler("note", note_command))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("anchor", anchor))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VOICE, handle_note_content))
    
    logger.info("✅ X_Lab запущен и работает 24/7")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
