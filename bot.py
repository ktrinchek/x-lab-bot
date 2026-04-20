#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import random
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json

# ===== НАСТРОЙКИ =====
TOKEN = os.environ.get("TOKEN", "7533119660:AAHymK3kK8BvIKWsgeBYz0p44kwzy8gX-hc")
DATA_FILE = "/opt/render/project/src/user_data.json"
NOTES_FILE = "/opt/render/project/src/notes.json"
DREAMS_FILE = "/opt/render/project/src/dreams.json"
SYNC_FILE = "/opt/render/project/src/syncs.json"

# ===== ЛОГИ =====
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== 40 ЗАДАНИЙ (первые 7) =====
TASKS = {
    1: """🌅 ДЕНЬ 1. РАЗМОРОЗКА

Задание: УТРЕННИЕ СТРАНИЦЫ

Возьми ручку и 3 листа бумаги.
Пиши всё, что приходит в голову.
Начни с фразы: «Я не знаю, что писать, но...»

Заполни 3 страницы. Не останавливайся.
Не перечитывай. Не исправляй ошибки.

🕒 25 минут.

---
🎲 ЧИТ-КОД ДНЯ: {code}""",

    2: """🌅 ДЕНЬ 2. РУКА

Задание: СЛЕПОЙ РИСУНОК

Возьми лист бумаги и ручку.
Закрой глаза. Нащупай любой предмет рядом.
Рисуй его контур не глядя на лист. 5 минут.

Затем открой глаза и посмотри, что получилось.
Не оценивай «красиво/некрасиво». Просто смотри.

🕒 15 минут.

---
🎲 ЧИТ-КОД ДНЯ: {code}""",

    3: """🌅 ДЕНЬ 3. ЗВУК

Задание: ЗВУКОВАЯ ПРОГУЛКА

Выйди на улицу или открой окно.
Закрой глаза на 10 минут.
Слушай. Не анализируй источники.
Просто собирай звуки, как собирают камни.

Запиши 3-5 звуков, которые запомнились.
Одним словом каждый. Например: «шорох», «гудок», «смех».

🕒 20 минут.

---
🎲 ЧИТ-КОД ДНЯ: {code}""",

    4: """🌅 ДЕНЬ 4. ТЕЛО

Задание: ГДЕ ЖИВЁТ ЭМОЦИЯ

Сядь удобно. Закрой глаза.
Спроси себя: «Что я сейчас чувствую?»
Не думай. Жди ответа от тела.

Где в теле живёт это чувство?
Грудь? Живот? Горло? Плечи?

Положи туда руку. Побудь с этим 10 минут.
Ничего не меняй. Просто заметь.

🕒 20 минут.

---
🎲 ЧИТ-КОД ДНЯ: {code}""",

    5: """🌅 ДЕНЬ 5. ПАМЯТЬ

Задание: ЗАПАХ ДЕТСТВА

Вспомни запах, который связан с детством.
Не событие — именно запах.
Бабушкин суп? Мокрый асфальт? Духи мамы? Книжная пыль?

Опиши его в 5 предложениях.
Не «пахло чем-то сладким», а «тёплый, дрожжевой, с кислинкой».

🕒 25 минут.

---
🎲 ЧИТ-КОД ДНЯ: {code}""",

    6: """🌅 ДЕНЬ 6. ТЕНЬ

Задание: ПИСЬМО ТОМУ, ЧТО ТЫ ПОДАВЛЯЕШЬ

Вспомни качество, которое ты в себе не принимаешь.
Лень? Злость? Глупость? Хаотичность?

Напиши ему письмо. Начни так:
«Дорогая моя [Лень], я долго тебя прятала, но сегодня я хочу сказать...»

Не оправдывайся. Не обещай исправиться.
Просто дай этому качеству голос.

🕒 30 минут.

---
🎲 ЧИТ-КОД ДНЯ: {code}""",

    7: """🌅 ДЕНЬ 7. ИТОГИ НЕДЕЛИ

Задание: ПИСЬМО СЕБЕ ПРОШЕДШЕЙ

Напиши письмо себе, которая начала этот путь 7 дней назад.
Что ты узнала? Что удивило? Что было трудно?
Что ты хочешь взять с собой дальше?

Никакой оценки «хорошо/плохо».
Только наблюдение.

🕒 25 минут.

---
🎲 ЧИТ-КОД ДНЯ: {code}""",
}

# ===== ЧИТ-КОДЫ (17) =====
CODES = [
    {"code": "я есмь", "desc": "Напоминание о чистом присутствии. Ты не роль, не функция. Ты — само бытие."},
    {"code": "так есть", "desc": "Принятие реальности без борьбы. Не сопротивление, а направление энергии в созидание."},
    {"code": "Пусть поток ведет меня", "desc": "Доверие процессу. Отпустить контроль и позволить жизни нести."},
    {"code": "я свет проходящий сквозь форму", "desc": "Ты больше, чем тело и социальная маска. Ты — свет, временно принявший эту форму."},
    {"code": "любовь моя частота", "desc": "Вибрация, которую ты излучаешь. Настройся на любовь — и реальность ответит тем же."},
    {"code": "я помню себя", "desc": "Возвращение к сути. Среди шума — вспомнить, кто ты на самом деле."},
    {"code": "все уже происходит", "desc": "Отпускание контроля. Всё уже в движении. Твоё дело — заметить и участвовать."},
    {"code": "я свидетель чуда", "desc": "Взгляд художника на мир. В обыденном скрыто волшебство."},
    {"code": "я открыта тайне", "desc": "Готовность к неизвестному. Не нужно всё понимать — можно просто быть в контакте с тайной."},
    {"code": "Я — магнит для хороших людей и событий", "desc": "Притяжение возможностей. Твоё поле привлекает то, что резонирует."},
    {"code": "Я действую из лёгкости, и всё складывается", "desc": "Снятие напряжения с результата. Лёгкость — не лень, а доверие."},
    {"code": "Я в безопасности, я доверяю миру", "desc": "Базовое спокойствие. Мир не враг. Можно выдохнуть."},
    {"code": "832523295", "desc": "Числовой код Грабового. Лёгкие деньги, неожиданные поступления. Позволь потоку принести."},
    {"code": "888 412 1289018", "desc": "Числовой код Грабового. Магнит для любви. Открой сердце."},
    {"code": "9187948181", "desc": "Числовой код Грабового. Исцеление тела, восстановление энергии."},
    {"code": "817219738", "desc": "Числовой код Грабового. Колесо фортуны, удача, благоприятные совпадения."},
    {"code": "93151 864 1491", "desc": "Числовой код Грабового. Карьерный прорыв, успех в делах."},
]

# ===== ВОПРОСЫ ДЛЯ /shadow (25) =====
SHADOW_QUESTIONS = [
    # Блок 1: Контроль и страх "глупости"
    "Что страшнее: быть уличенной в некомпетентности или быть незамеченной вовсе?",
    "Какую книгу/фильм ты НЕ досмотрела, но в разговоре делаешь вид, что знаешь?",
    "Кого ты считаешь «поверхностным» в своём окружении? А в чём ты сама поверхностна?",
    "Когда ты в последний раз притворялась, что тебе интересно, хотя внутри было пусто?",
    "Какую свою «глупую» радость ты скрываешь от других?",
    # Блок 2: Мужчины, выбор и тело
    "Какое качество в мужчине тебя необъяснимо притягивает, даже если умом ты его не одобряешь?",
    "Ты боишься, что выбираешь «не тех», или боишься, что «те» тебя не выберут?",
    "Когда ты чувствуешь своё тело как помеху, а не как союзника?",
    "Что бы ты сделала на свидании, если бы точно знала, что тебя не осудят?",
    "Если бы все твои бывшие собрались в одной комнате, что бы ты хотела, чтобы они поняли о тебе?",
    # Блок 3: Творчество и недоделки
    "Что ты скажешь себе, когда наконец доделаешь ту самую «недоделку»? (А если не доделаешь — что тогда?)",
    "Чьё мнение о твоём творчестве тебя парализует больше всего?",
    "Что ты почувствуешь, если твоя работа окажется «средней»?",
    "Ты больше боишься провала или успеха, после которого придётся соответствовать?",
    "Какую свою идею ты похоронила со словами «это уже было» или «это банально»?",
    # Блок 4: Одиночество, свобода и правда
    "Что ты чувствуешь, когда остаёшься одна в тишине без цели?",
    "От какой своей черты ты бы отказалась, если бы могла? А от какой — ни за что?",
    "Кому ты завидуешь по-чёрному, до жжения в груди?",
    "Если бы тебе осталось жить год, какое единственное правило ты бы выбросила из своей жизни первым?",
    "Что ты осуждаешь в других женщинах, но тайно позволяешь себе?",
    # Блок 5: От аналитика
    "Что произойдёт, если ты однажды посмотришь фильм и просто скажешь: «Мне понравилось», — без анализа?",
    "Что ты почувствуешь, когда поймёшь, что инструкции кончились и дальше — только твой голос?",
    "Ты создаёшь бота, пишешь коды. Где в этом процессе твоё тело? Что оно делает прямо сейчас?",
    "X_Lab завершена. 40 дней прошло. Кто просыпается на 41-й день?",
    "Ты просишь меня о помощи. Что ты на самом деле хочешь, чтобы я сделал? Написал код? Или разрешил тебе начать?",
]

# ===== ДЫХАТЕЛЬНЫЕ ПРАКТИКИ =====
BREATHE = [
    "🌬️ КВАДРАТНОЕ ДЫХАНИЕ\nВдох на 4 счёта.\nЗадержка на 4.\nВыдох на 4.\nЗадержка на 4.\nПовтори 5 циклов.",
    "🌬️ 4-7-8\nВдох через нос на 4 счёта.\nЗадержка на 7.\nВыдох через рот на 8.\nПовтори 4 цикла.",
    "🌬️ ДЫХАНИЕ ЖИВОТОМ\nПоложи руку на живот.\nВдох — живот надувается.\nВыдох — сдувается.\nГрудь неподвижна.\n3 минуты.",
    "🌬️ ПОПЕРЕМЕННОЕ ДЫХАНИЕ\nЗакрой правую ноздрю, вдох левой.\nЗакрой левую, выдох правой.\nВдох правой, выдох левой.\n5 циклов.",
    "🌬️ ВЫДОХ ВДВОЕ ДЛИННЕЕ\nВдох на 3 счёта.\nВыдох на 6.\nБез задержек.\n2 минуты.",
]

# ===== ЦИТАТЫ ДЛЯ /inspire =====
QUOTES = [
    "«Пока вы не сделаете бессознательное сознательным, оно будет управлять вашей жизнью, и вы назовёте это судьбой.» — Карл Юнг",
    "«Творчество — это не соревнование. Творчество — это дыхание.» — Джулия Кэмерон",
    "«Ты не капля в океане. Ты — целый океан в капле.» — Руми",
    "«Иногда поиск — это просто отсрочка. Найденное ждёт там, где ты перестала искать.»",
    "«Не сравнивай своё начало с чужой серединой.» — Джон Акафф",
    "«Искусство — это ложь, которая позволяет нам осознать правду.» — Пабло Пикассо",
    "«Твоя Тень — это не враг. Это часть тебя, которую ты не научилась любить.»",
    "«Делай что можешь, с тем что имеешь, там где ты есть.» — Теодор Рузвельт",
    "«Перфекционизм — это не стремление к лучшему. Это страх.»",
    "«Ты — автор. Не комментатор.»",
]

# ===== РАБОТА С ДАННЫМИ =====
def load_json(filepath, default):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки {filepath}: {e}")
    return default

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения {filepath}: {e}")

def load_user_data():
    return load_json(DATA_FILE, {"start_date": None, "current_day": 1, "completed_days": []})

def save_user_data(data):
    save_json(DATA_FILE, data)

def load_notes():
    return load_json(NOTES_FILE, [])

def save_note(text):
    notes = load_notes()
    notes.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": text})
    save_json(NOTES_FILE, notes)

def load_dreams():
    return load_json(DREAMS_FILE, [])

def save_dream(text):
    dreams = load_dreams()
    dreams.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": text})
    save_json(DREAMS_FILE, dreams)

def load_syncs():
    return load_json(SYNC_FILE, [])

def save_sync(text):
    syncs = load_syncs()
    syncs.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": text})
    save_json(SYNC_FILE, syncs)

def get_random_code():
    c = random.choice(CODES)
    return f"⚡️ *{c['code']}*\n\n_{c['desc']}_"

# ===== КОМАНДЫ =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    if user_data["start_date"] is None:
        user_data["start_date"] = date.today().isoformat()
        user_data["current_day"] = 1
        save_user_data(user_data)
        await update.message.reply_text(
            "🖤 ДОБРО ПОЖАЛОВАТЬ В X_LAB\n\n"
            "Твой путь начался сегодня.\nДень 1 из 40.\n\n"
            "Напиши /today, чтобы получить первое задание.\n\n"
            "Ты не зритель. Ты — Автор."
        )
    else:
        day = user_data["current_day"]
        await update.message.reply_text(
            f"🖤 С ВОЗВРАЩЕНИЕМ В X_LAB\n\nСегодня День {day} из 40.\n\n"
            f"/today — задание дня\n/progress — твой прогресс"
        )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("☀️ Задание дня", callback_data='today')],
        [InlineKeyboardButton("✅ Отметить выполнение", callback_data='done')],
        [InlineKeyboardButton("📊 Прогресс", callback_data='progress')],
        [InlineKeyboardButton("✍️ Новая заметка", callback_data='note')],
        [InlineKeyboardButton("📅 Сводка за неделю", callback_data='week')],
        [InlineKeyboardButton("🎲 Чит-код", callback_data='code')],
        [InlineKeyboardButton("🌑 Вопрос Тени", callback_data='shadow')],
        [InlineKeyboardButton("🌬️ Дыхание", callback_data='breathe')],
        [InlineKeyboardButton("💭 Вдохновение", callback_data='inspire')],
        [InlineKeyboardButton("⚓️ Якорь", callback_data='anchor')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧭 ВЫБЕРИ ДЕЙСТВИЕ:", reply_markup=reply_markup)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    day = user_data["current_day"]
    if day > 40:
        await update.message.reply_text("🎉 ПОЗДРАВЛЯЮ! Ты прошла все 40 дней. Ты — Автор.")
        return
    code = random.choice(CODES)
    code_str = f"{code['code']} — {code['desc']}"
    task = TASKS.get(day, f"🌅 ДЕНЬ {day}\n\nЗадание в разработке.\n\n---\n🎲 ЧИТ-КОД ДНЯ: {code_str}")
    await update.message.reply_text(task.format(code=code_str) if "{" in task else task)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    day = user_data["current_day"]
    if day > 40:
        await update.message.reply_text("Ты уже прошла все 40 дней.")
        return
    if day not in user_data["completed_days"]:
        user_data["completed_days"].append(day)
    if day < 40:
        user_data["current_day"] = day + 1
        save_user_data(user_data)
        await update.message.reply_text(f"✅ ДЕНЬ {day} ВЫПОЛНЕН\n\nЗавтра — День {day + 1}.")
    else:
        user_data["current_day"] = 41
        save_user_data(user_data)
        await update.message.reply_text("🎉 ДЕНЬ 40 ВЫПОЛНЕН!\n\nТы прошла весь путь. Ты — Автор.")

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    day = user_data["current_day"]
    completed = len(user_data["completed_days"])
    start_str = user_data["start_date"]
    if start_str:
        start = date.fromisoformat(start_str)
        days_passed = (date.today() - start).days + 1
    else:
        days_passed = 0
    pct = int((completed / 40) * 100) if completed > 0 else 0
    await update.message.reply_text(
        f"📊 ТВОЙ ПРОГРЕСС\n\n"
        f"📍 Сегодня: День {day if day <= 40 else 40} из 40\n"
        f"✅ Выполнено заданий: {completed}\n"
        f"📅 Дней в пути: {days_passed}\n"
        f"📈 Пройдено: {pct}%\n\n"
        f"{'🖤 Продолжай.' if day <= 40 else '🎉 Путь пройден.'}"
    )

async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Я СЛУШАЮ.\n\nОтправь текстом, голосом или фото. Я сохраню.")
    context.user_data['awaiting_note'] = True

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
    await update.message.reply_text(summary)

async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_random_code(), parse_mode="Markdown")

async def shadow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(SHADOW_QUESTIONS)
    await update.message.reply_text(f"🌑 ВОПРОС ТЕНИ:\n\n{q}\n\nОтветь честно. Можно одним предложением. Это только для тебя.")
    context.user_data['awaiting_shadow'] = True
    context.user_data['shadow_question'] = q

async def dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌙 ЗАПИШИ СОН\n\nОпиши, что приснилось. Детали, ощущения, странности.")
    context.user_data['awaiting_dream'] = True

async def sync_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 ЗАПИШИ СИНХРОНИЮ\n\nСтранное совпадение, знак, подмигивание вселенной.")
    context.user_data['awaiting_sync'] = True

async def breathe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(BREATHE))

async def inspire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💭 {random.choice(QUOTES)}")

async def anchor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚓️ ЯКОРЬ\n\n"
        "\"Иногда поиск — это просто отсрочка. Найденное ждёт там, где ты перестала искать.\"\n\n"
        "Ты не комментатор. Ты — автор.\nДыши. Ты здесь."
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user_data({"start_date": None, "current_day": 1, "completed_days": []})
    await update.message.reply_text("🔄 Прогресс сброшен. Напиши /start, чтобы начать заново.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    
    text = msg.text or ""
    if msg.photo:
        content = "[Фото]"
    elif msg.voice:
        content = "[Голосовое]"
    else:
        content = text[:500] if text else "[Медиа]"
    
    if context.user_data.get('awaiting_note'):
        save_note(content)
        context.user_data['awaiting_note'] = False
        await msg.reply_text("✅ Заметка сохранена.")
    elif context.user_data.get('awaiting_shadow'):
        q = context.user_data.get('shadow_question', '')
        save_note(f"🌑 Тень: {q} → {content}")
        context.user_data['awaiting_shadow'] = False
        await msg.reply_text("🌑 Ответ сохранён. Спасибо за честность.")
    elif context.user_data.get('awaiting_dream'):
        save_dream(content)
        context.user_data['awaiting_dream'] = False
        await msg.reply_text("🌙 Сон записан.")
    elif context.user_data.get('awaiting_sync'):
        save_sync(content)
        context.user_data['awaiting_sync'] = False
        await msg.reply_text("🔮 Синхрония записана.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    msg = query.message
    
    if data == 'today':
        await today(msg, context)
    elif data == 'done':
        await done(msg, context)
    elif data == 'progress':
        await progress(msg, context)
    elif data == 'note':
        await msg.reply_text("📝 Отправь текстом, голосом или фото. Я сохраню.")
        context.user_data['awaiting_note'] = True
    elif data == 'week':
        await week(msg, context)
    elif data == 'code':
        await code(msg, context)
    elif data == 'shadow':
        await shadow(msg, context)
    elif data == 'breathe':
        await breathe(msg, context)
    elif data == 'inspire':
        await inspire(msg, context)
    elif data == 'anchor':
        await anchor(msg, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("note", note_command))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("code", code))
    app.add_handler(CommandHandler("shadow", shadow))
    app.add_handler(CommandHandler("dream", dream))
    app.add_handler(CommandHandler("sync", sync_command))
    app.add_handler(CommandHandler("breathe", breathe))
    app.add_handler(CommandHandler("inspire", inspire))
    app.add_handler(CommandHandler("anchor", anchor))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VOICE, handle_message))
    
    logger.info("✅ X_Lab v2.0 запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
