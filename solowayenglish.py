from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3
import os
import json

TOKEN = "8681728801:AAHYuSN_UtHSe4w6F3uOLXwoaL0dSGjuF9k"

DB_PATH = "/data/english.db"

# Загружаем тесты из JSON
try:
    with open("test.json", "r", encoding="utf-8") as f:
        TESTS = json.load(f)
except:
    TESTS = {}

# ===== ВСЕ ТЕМЫ =====
TOPICS = {
    "A1 (Beginner)": {
        "Грамматика": [
            "Глагол to be (am/is/are)",
            "Личные местоимения (I, you, he, she, it, we, they)",
            "Объектные местоимения (me, him, her, us, them)",
            "Притяжательные местоимения (my/mine, your/yours)",
            "Указательные местоимения (this, that, these, those)",
            "Неопределённые местоимения (some, any, no)",
            "Множественное число существительных",
            "Притяжательный падеж ('s)",
            "Артикли (a/an, the)",
            "Present Simple",
            "Present Continuous",
            "Present Simple vs Present Continuous",
            "Past Simple (was/were, правильные глаголы)",
            "Past Simple (неправильные глаголы, топ-20)",
            "Future Simple (will)",
            "Конструкция to be going to",
            "Предлоги места (in, on, under, next to, behind)",
            "Предлоги времени (at, on, in)",
            "Порядок слов в утверждении (SVO)",
            "Общие вопросы (Do you…? Is he…?)",
            "Специальные вопросы (What, Where, When)",
            "Вопросы к подлежащему (Who lives here?)",
            "Повелительное наклонение (Open the door!)",
            "Союзы (and, but, or, because)",
            "Конструкция like + ing",
            "Модальный глагол can/can't",
            "There is / There are",
            "Наречия частоты (always, never, sometimes, often)",
        ],
        "Лексика": [
            "Цифры, числа, даты, время",
            "Дни недели, месяцы, времена года",
            "Семья (mother, father, sister, brother)",
            "Дом и комната (furniture, rooms)",
            "Еда и напитки (food, drink)",
            "Одежда и цвета (clothes, colours)",
            "Школа и школьные предметы",
            "Хобби и свободное время",
            "Описание людей (tall, short, kind, funny)",
            "Город и транспорт (places, prepositions)",
            "Погода (sunny, rainy, hot, cold)",
            "Повседневные действия (get up, have breakfast, go to school)",
        ],
    },
    "A2 (Elementary)": {
        "Грамматика": [
            "Past Continuous (I was doing)",
            "Present Perfect (I have done) — опыт, результат",
            "Present Perfect vs Past Simple",
            "Present Perfect Continuous (I have been doing)",
            "Future forms: will / going to / Present Continuous",
            "Конструкция used to",
            "Степени сравнения прилагательных",
            "Сравнительные конструкции (as…as, not as…as, than)",
            "Порядок прилагательных",
            "Наречия образа действия (quickly, well, fast)",
            "Модальные глаголы (must, have to, should, may, might, could)",
            "Предлоги времени (for, since, during, by, until)",
            "Предлоги места (in, on, at, behind, between)",
            "Предлоги движения (to, into, out of, through, along)",
            "Количественные слова (some, any, much, many, a lot of)",
            "Неопределённые местоимения (somebody, anybody, nobody)",
            "Возвратные местоимения (myself, yourself, himself)",
            "Союзы (because, so, although, however)",
            "Косвенная речь (база: He said that…)",
            "Условные предложения 0 и 1 типа",
            "Пассивный залог (база: is done, was done)",
            "Вопросы разделительные (You like coffee, don't you?)",
            "Вопросы косвенные (Can you tell me where…)",
        ],
        "Лексика": [
            "Путешествия и транспорт",
            "Еда и заказ в кафе",
            "Внешность и характер",
            "Семья и отношения",
            "Образование и экзамены",
            "Работа и профессии",
            "Город и ориентация",
            "Погода и времена года",
            "Покупки и одежда",
            "Здоровье и тело",
        ],
    },
    "B1 (Intermediate)": {
        "Грамматика": [
            "Past Perfect (I had done)",
            "Past Perfect vs Past Simple",
            "Present Perfect Continuous (углублённо)",
            "Future Continuous (I will be doing)",
            "Future Perfect (I will have done)",
            "Условные предложения 2 и 3 типа",
            "Сослагательное наклонение (I wish… / If only…)",
            "Конструкция be/get used to + ing",
            "Герундий и инфинитив (remember to do vs remember doing)",
            "Модальные глаголы в прошлом (must have, might have)",
            "Пассивный залог (все времена)",
            "Косвенная речь (вопросы, просьбы, приказы)",
            "Определительные придаточные (who, which, that, whose)",
            "Артикли (углублённо, включая нулевой артикль)",
            "Предлоги (углублённо: despite, in spite of, due to)",
            "Фразовые глаголы (get up, turn on, look for, give up)",
            "Инверсия (Never have I seen…)",
        ],
        "Лексика": [
            "Путешествия и культура",
            "Технологии и интернет",
            "Экология и окружающая среда",
            "Работа и карьера",
            "Образование",
            "Здоровье и медицина",
            "Медиа и новости",
            "Отношения и общение",
            "Искусство и литература",
            "Финансы и деньги",
        ],
    },
    "B2 (Upper-Intermediate)": {
        "Грамматика": [
            "Все времена (активный и пассивный залог)",
            "Все условные предложения (смешанные типы)",
            "Сослагательное наклонение после suggest, recommend, insist",
            "Модальные глаголы для выражения предположений",
            "Инверсия в условных предложениях (Had I known…)",
            "Эмфатические конструкции (It is … that… / What … is…)",
            "Сложные союзы (nonetheless, whereas, thereby, hence)",
            "Фразовые глаголы (углублённо, с несколькими значениями)",
            "Сложные герундиальные и инфинитивные обороты",
            "Пунктуация и стилистика",
        ],
        "Лексика": [
            "Бизнес и экономика",
            "Наука и технологии",
            "Политика и общество",
            "Юриспруденция и право",
            "Психология и саморазвитие",
            "Глобальные проблемы",
            "Культура и традиции (глубоко)",
            "Маркетинг и реклама",
            "Переговоры и убеждение",
            "Реферирование и пересказ",
        ],
    },
}

def init_db():
    try:
        os.makedirs("/data", exist_ok=True)
    except:
        pass
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            level TEXT,
            category TEXT,
            topic TEXT,
            done INTEGER DEFAULT 0,
            UNIQUE(user_id, level, topic)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            level TEXT,
            category TEXT,
            topic TEXT,
            score INTEGER,
            total INTEGER,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

ALLOWED_USERS = {
    "Соловей": "2011",
}

def get_progress(user_id, level):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT topic, done FROM progress WHERE user_id = ? AND level = ?", (user_id, level))
    rows = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def toggle_topic(user_id, level, category, topic):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT done FROM progress WHERE user_id = ? AND level = ? AND topic = ?",
              (user_id, level, topic))
    row = c.fetchone()
    
    if row:
        new_status = 0 if row[0] else 1
        c.execute("UPDATE progress SET done = ? WHERE user_id = ? AND level = ? AND topic = ?",
                  (new_status, user_id, level, topic))
    else:
        new_status = 1
        c.execute("INSERT INTO progress (user_id, level, category, topic, done) VALUES (?, ?, ?, ?, ?)",
                  (user_id, level, category, topic, 1))
    
    conn.commit()
    conn.close()
    return new_status

def save_test_result(user_id, level, category, topic, score, total):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO test_results (user_id, level, category, topic, score, total, date) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
              (user_id, level, category, topic, score, total))
    conn.commit()
    conn.close()

def has_test(level, topic):
    """Проверяет есть ли тест для данной темы"""
    try:
        for cat in TESTS.get(level, {}):
            if topic in TESTS[level][cat]:
                return True
    except:
        pass
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "authenticated" not in context.user_data:
        await update.message.reply_text("🔐 Привет! Введи свой ник:")
        context.user_data["awaiting_username"] = True
        return
    
    await show_levels(update, context)

async def show_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 A1 (Beginner)", callback_data="level_A1 (Beginner)")],
        [InlineKeyboardButton("📚 A2 (Elementary)", callback_data="level_A2 (Elementary)")],
        [InlineKeyboardButton("📚 B1 (Intermediate)", callback_data="level_B1 (Intermediate)")],
        [InlineKeyboardButton("📚 B2 (Upper-Intermediate)", callback_data="level_B2 (Upper-Intermediate)")],
        [InlineKeyboardButton("📊 Общий прогресс", callback_data="total_progress")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "🎓 *Soloway English Tracker*\n\nВыбери уровень:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE, level):
    categories = list(TOPICS[level].keys())
    keyboard = []
    for cat in categories:
        progress = get_progress(update.effective_user.id, level)
        total = len(TOPICS[level][cat])
        done = sum(1 for topic in TOPICS[level][cat] if progress.get(topic, 0))
        keyboard.append([InlineKeyboardButton(f"{cat} ({done}/{total})", callback_data=f"cat_{level}|{cat}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_levels")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"📚 {level}\n\nВыбери категорию:",
        reply_markup=reply_markup
    )

async def show_topics(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category):
    topics = TOPICS[level][category]
    progress = get_progress(update.effective_user.id, level)
    
    keyboard = []
    for idx, topic in enumerate(topics):
        done = progress.get(topic, 0)
        emoji = "✅" if done else "⬜"
        keyboard.append([InlineKeyboardButton(f"{emoji} {topic}", callback_data=f"topic_{level}|{category}|{idx}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"level_{level}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    total = len(topics)
    done = sum(1 for t in topics if progress.get(t, 0))
    percent = int(done / total * 100) if total > 0 else 0
    bar = "🟩" * (percent // 10) + "⬜" * (10 - percent // 10)
    
    await update.callback_query.edit_message_text(
        f"📚 {level} → {category}\n\n{bar} {done}/{total} ({percent}%)\n\nНажми на тему чтобы открыть меню:",
        reply_markup=reply_markup
    )

async def show_topic_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    progress = get_progress(update.effective_user.id, level)
    done = progress.get(topic, 0)
    
    status = "✅ Пройдена" if done else "⬜ Не пройдена"
    
    keyboard = [
        [InlineKeyboardButton("✅ Отметить как пройденное" if not done else "❌ Снять отметку", 
                              callback_data=f"tog_{level}|{category}|{idx}")],
    ]
    
    # Проверяем есть ли тест
    if has_test(level, topic):
        keyboard.append([InlineKeyboardButton("📝 Пройти тест (8 вопросов)", callback_data=f"test_{level}|{category}|{idx}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{level}|{category}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"📚 {topic}\n\n{status}\n\nВыбери действие:",
        reply_markup=reply_markup
    )

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    
    # Ищем тест
    test_data = None
    for cat in TESTS.get(level, {}):
        if topic in TESTS[level][cat]:
            test_data = TESTS[level][cat][topic]
            break
    
    if not test_data:
        await update.callback_query.answer("❌ Тест не найден", show_alert=True)
        return
    
    questions = test_data["questions"]
    context.user_data["test"] = {
        "level": level,
        "category": category,
        "topic": topic,
        "questions": questions,
        "current": 0,
        "score": 0
    }
    
    await show_question(update, context)

async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    test = context.user_data.get("test")
    if not test:
        return
    
    q_num = test["current"]
    if q_num >= len(test["questions"]):
        await finish_test(update, context)
        return
    
    question = test["questions"][q_num]
    options = question["options"]
    
    keyboard = []
    for i, opt in enumerate(options):
        keyboard.append([InlineKeyboardButton(f"{chr(97+i)}) {opt}", callback_data=f"ans_{i}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"📝 *Тест: {test['topic']}*\n\n"
        f"Вопрос {q_num + 1}/{len(test['questions'])}:\n\n"
        f"*{question['q']}*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, answer_idx):
    test = context.user_data.get("test")
    if not test:
        return
    
    question = test["questions"][test["current"]]
    correct = question["answer"]
    
    if answer_idx == correct:
        test["score"] += 1
        await update.callback_query.answer("✅ Правильно!")
    else:
        correct_ans = question["options"][correct]
        await update.callback_query.answer(f"❌ Неправильно! Правильно: {correct_ans}")
    
    test["current"] += 1
    
    # ПРИНУДИТЕЛЬНАЯ проверка — последний ли это был вопрос?
    if test["current"] >= len(test["questions"]):
        await finish_test(update, context)
    else:
        await show_question(update, context)

async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    test = context.user_data.get("test")
    if not test:
        return
    
    score = test["score"]
    total = len(test["questions"])
    percent = int(score / total * 100)
    
    user_id = update.effective_user.id
    save_test_result(user_id, test["level"], test["category"], test["topic"], score, total)
    
    if percent == 100:
        emoji = "🏆"
        comment = "Идеально! Ты отлично знаешь эту тему!"
    elif percent >= 75:
        emoji = "🎉"
        comment = "Хороший результат! Ещё немного и будет 100%!"
    elif percent >= 50:
        emoji = "📚"
        comment = "Неплохо! Но стоит повторить материал."
    else:
        emoji = "💪"
        comment = "Нужно подучить эту тему. Не сдавайся!"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти ещё раз", callback_data=f"test_{test['level']}|{test['category']}|{test['topic']}")],
        [InlineKeyboardButton("🔙 К теме", callback_data=f"topic_{test['level']}|{test['category']}|{test['topic']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"{emoji} *Тест завершён!*\n\n"
        f"📝 {test['topic']}\n"
        f"📊 Результат: {score}/{total} ({percent}%)\n\n"
        f"{comment}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    del context.user_data["test"]

async def toggle_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    
    user_id = update.effective_user.id
    new_status = toggle_topic(user_id, level, category, topic)
    await update.callback_query.answer(f"{'✅ Отмечено!' if new_status else '❌ Снято!'}")
    await show_topic_menu(update, context, level, category, idx)

async def show_total_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    text = "📊 *Общий прогресс*\n\n"
    total_all = 0
    done_all = 0
    
    for level in TOPICS:
        level_total = sum(len(topics) for topics in TOPICS[level].values())
        progress = get_progress(user_id, level)
        
        level_done = 0
        for cat in TOPICS[level]:
            for topic in TOPICS[level][cat]:
                if progress.get(topic, 0):
                    level_done += 1
        
        total_all += level_total
        done_all += level_done
        percent = int(level_done / level_total * 100) if level_total > 0 else 0
        bar = "🟩" * (percent // 10) + "⬜" * (10 - percent // 10)
        text += f"{bar} {level}: {level_done}/{level_total} ({percent}%)\n"
    
    total_percent = int(done_all / total_all * 100) if total_all > 0 else 0
    text += f"\n🎯 *Всего: {done_all}/{total_all} ({total_percent}%)*"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_levels")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if "authenticated" not in context.user_data:
        await query.edit_message_text("🔐 Сначала авторизуйся: /start")
        return
    
    if data == "back_to_levels":
        await show_levels(update, context)
    elif data == "total_progress":
        await show_total_progress(update, context)
    elif data.startswith("level_"):
        level = data[6:]
        await show_categories(update, context, level)
    elif data.startswith("cat_"):
        parts = data[4:].split("|")
        level, category = parts[0], parts[1]
        await show_topics(update, context, level, category)
    elif data.startswith("topic_"):
        parts = data[6:].split("|")
        level, category, idx = parts[0], parts[1], parts[2]
        await show_topic_menu(update, context, level, category, idx)
    elif data.startswith("tog_"):
        parts = data[4:].split("|")
        level, category, idx = parts[0], parts[1], parts[2]
        await toggle_topic_handler(update, context, level, category, idx)
    elif data.startswith("test_"):
        parts = data[5:].split("|")
        level, category, idx = parts[0], parts[1], parts[2]
        await start_test(update, context, level, category, idx)
    elif data.startswith("ans_"):
        answer_idx = int(data[4:])
        await handle_answer(update, context, answer_idx)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_username"):
        username = update.message.text.strip()
        if username in ALLOWED_USERS:
            context.user_data["temp_username"] = username
            context.user_data["awaiting_username"] = False
            context.user_data["awaiting_password"] = True
            await update.message.reply_text("🔑 Введи пароль:")
        else:
            await update.message.reply_text("❌ Неверный ник. Попробуй ещё раз:")
        return
    
    if context.user_data.get("awaiting_password"):
        password = update.message.text.strip()
        username = context.user_data.get("temp_username")
        if ALLOWED_USERS.get(username) == password:
            context.user_data["authenticated"] = True
            context.user_data.pop("temp_username", None)
            context.user_data.pop("awaiting_password", None)
            await update.message.reply_text("✅ Доступ разрешён!")
            await show_levels(update, context)
        else:
            context.user_data.pop("temp_username", None)
            context.user_data.pop("awaiting_password", None)
            context.user_data.pop("awaiting_username", None)
            await update.message.reply_text("❌ Неверный пароль. Начни заново с /start")
        return

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("🎓 Soloway English Tracker запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()