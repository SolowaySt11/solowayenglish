from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3
import os
import json
import matplotlib.pyplot as plt
import io
import hashlib  # для хэширования паролей
import re

TOKEN = "8681728801:AAFNkjp2eeIZ3KYEOnpXgIu3IowwERXSEWM"
DB_PATH = "/data/english.db"

# ===== ЗАГРУЗКА ВСЕХ JSON ФАЙЛОВ =====

def load_all_tests():
    """Загружает все JSON файлы из папки telegram_bot"""
    TESTS = {}
    
    level_map = {
        "A1 (Beginner)": "A1",
        "A2 (Elementary)": "A2",
        "B1 (Intermediate)": "B1",
        "B2 (Upper-Intermediate)": "B2"
    }
    
    base_path = os.path.dirname(__file__)
    
    for level_name, level_key in level_map.items():
        TESTS[level_name] = {}
        
        grammar_file = os.path.join(base_path, f"{level_key}_grammar.json")
        if os.path.exists(grammar_file):
            try:
                with open(grammar_file, "r", encoding="utf-8") as f:
                    grammar_data = json.load(f)
                    TESTS[level_name]["Грамматика"] = grammar_data
                print(f"✅ Загружена грамматика для {level_name}")
            except Exception as e:
                print(f"❌ Ошибка загрузки {grammar_file}: {e}")
                TESTS[level_name]["Грамматика"] = {}
        else:
            print(f"⚠️ Файл не найден: {grammar_file}")
            TESTS[level_name]["Грамматика"] = {}
        
        vocabulary_file = os.path.join(base_path, f"{level_key}_vocabulary.json")
        if os.path.exists(vocabulary_file):
            try:
                with open(vocabulary_file, "r", encoding="utf-8") as f:
                    vocab_data = json.load(f)
                    TESTS[level_name]["Лексика"] = vocab_data
                print(f"✅ Загружена лексика для {level_name}")
            except Exception as e:
                print(f"❌ Ошибка загрузки {vocabulary_file}: {e}")
                TESTS[level_name]["Лексика"] = {}
        else:
            print(f"⚠️ Файл не найден: {vocabulary_file}")
            TESTS[level_name]["Лексика"] = {}
    
    return TESTS

print("📂 Загрузка JSON файлов...")
TESTS = load_all_tests()

print("\n📊 Загруженные данные:")
for level in TESTS:
    print(f"  📚 {level}:")
    for cat in TESTS[level]:
        topics = TESTS[level][cat]
        print(f"    📂 {cat}: {len(topics)} тем")

# ===== TOPICS (полный список) =====
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
            "Наречия частоты (always, never, sometimes, often)"
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
            "Повседневные действия (get up, have breakfast, go to school)"
        ]
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
            "Вопросы косвенные (Can you tell me where…)"
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
            "Здоровье и тело"
        ]
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
            "Инверсия (Never have I seen…)"
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
            "Финансы и деньги"
        ]
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
            "Пунктуация и стилистика"
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
            "Реферирование и пересказ"
        ]
    }
}

# ===== БАЗА ДАННЫХ =====

def init_db():
    try:
        os.makedirs("/data", exist_ok=True)
    except:
        pass
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )""")
    
    # Таблица прогресса
    c.execute("""CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        level TEXT,
        category TEXT,
        topic TEXT,
        done INTEGER DEFAULT 0,
        UNIQUE(user_id, level, topic)
    )""")
    
    # Таблица результатов тестов
    c.execute("""CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        level TEXT,
        category TEXT,
        topic TEXT,
        score INTEGER,
        total INTEGER,
        date TEXT
    )""")
    
    # Создаём админа, если его нет
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", 
                  ("admin", admin_password, 1))
        print("✅ Создан аккаунт администратора (логин: admin, пароль: admin123)")
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, password, is_admin FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed = hash_password(password)
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)", 
                  (username, hashed))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None

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

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def has_test(level, topic):
    try:
        if level not in TESTS:
            return False
        for cat in TESTS[level]:
            if topic in TESTS[level][cat]:
                if "questions" in TESTS[level][cat][topic]:
                    return True
    except:
        pass
    return False

def find_topic_index(level, category, topic_name):
    if level in TOPICS and category in TOPICS[level]:
        topics = TOPICS[level][category]
        for idx, topic in enumerate(topics):
            if topic == topic_name:
                return idx
    return 0

def generate_table_image(headers, rows, topic):
    fig, ax = plt.subplots(figsize=(10, len(rows) * 0.5 + 1))
    ax.axis('off')
    table = ax.table(cellText=rows, colLabels=headers, cellLoc='left', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('#2c3e50')
        if i == 0:
            cell.set_facecolor('#3498db')
            cell.set_text_props(color='white', weight='bold')
        elif i % 2 == 0:
            cell.set_facecolor('#ecf0f1')
        else:
            cell.set_facecolor('white')
    plt.title(topic, fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

# ===== ОСНОВНЫЕ ОБРАБОТЧИКИ =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое меню — вход или регистрация"""
    keyboard = [
        [InlineKeyboardButton("🔑 Войти", callback_data="login")],
        [InlineKeyboardButton("📝 Зарегистрироваться", callback_data="register")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Добро пожаловать в Soloway English Tracker!*\n\n"
        "У тебя уже есть аккаунт? Войди или зарегистрируйся!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔑 *Вход*\n\n"
        "Введи свой *логин* (первым сообщением) и *пароль* (вторым сообщением).\n\n"
        "Пример:\n"
        "`username`\n"
        "`password`",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_login"] = True

async def show_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📝 *Регистрация*\n\n"
        "Придумай *логин* и *пароль*.\n\n"
        "Логин должен содержать только буквы и цифры (мин. 3 символа).\n"
        "Пароль — минимум 4 символа.\n\n"
        "Введи их в двух сообщениях:\n"
        "1. *Логин*\n"
        "2. *Пароль*",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_register"] = True

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Вход
    if context.user_data.get("awaiting_login"):
        if not context.user_data.get("login_username"):
            context.user_data["login_username"] = text
            await update.message.reply_text("✅ Логин сохранён! Теперь введи пароль:")
        else:
            username = context.user_data.get("login_username")
            password = text
            user = get_user(username)
            
            if user and user[2] == hash_password(password):
                context.user_data["authenticated"] = True
                context.user_data["user_id"] = user[0]
                context.user_data["username"] = user[1]
                context.user_data["is_admin"] = user[3]
                context.user_data.pop("awaiting_login", None)
                context.user_data.pop("login_username", None)
                
                await update.message.reply_text(f"✅ Добро пожаловать, {username}! 🎉")
                await show_levels(update, context)
            else:
                context.user_data.pop("awaiting_login", None)
                context.user_data.pop("login_username", None)
                await update.message.reply_text("❌ Неверный логин или пароль. Попробуй /start")
    
    # Регистрация
    elif context.user_data.get("awaiting_register"):
        if not context.user_data.get("reg_username"):
            if re.match(r'^[a-zA-Z0-9_]{3,}$', text):
                context.user_data["reg_username"] = text
                await update.message.reply_text("✅ Логин подходит! Теперь введи пароль (мин. 4 символа):")
            else:
                await update.message.reply_text("❌ Логин должен содержать минимум 3 буквы или цифры. Попробуй ещё раз:")
        else:
            username = context.user_data.get("reg_username")
            password = text
            
            if len(password) < 4:
                await update.message.reply_text("❌ Пароль должен быть минимум 4 символа. Попробуй ещё раз:")
                return
            
            new_user_id = create_user(username, password)
            if new_user_id:
                context.user_data["authenticated"] = True
                context.user_data["user_id"] = new_user_id
                context.user_data["username"] = username
                context.user_data["is_admin"] = 0
                context.user_data.pop("awaiting_register", None)
                context.user_data.pop("reg_username", None)
                
                await update.message.reply_text(f"✅ Аккаунт создан! Добро пожаловать, {username}! 🎉")
                await show_levels(update, context)
            else:
                context.user_data.pop("awaiting_register", None)
                context.user_data.pop("reg_username", None)
                await update.message.reply_text("❌ Пользователь с таким логином уже существует. Попробуй /start")

async def show_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает уровни"""
    user_id = context.user_data.get("user_id")
    if not user_id:
        await start(update, context)
        return
    
    keyboard = [
        [InlineKeyboardButton("📚 A1 (Beginner)", callback_data="level_A1 (Beginner)")],
        [InlineKeyboardButton("📚 A2 (Elementary)", callback_data="level_A2 (Elementary)")],
        [InlineKeyboardButton("📚 B1 (Intermediate)", callback_data="level_B1 (Intermediate)")],
        [InlineKeyboardButton("📚 B2 (Upper-Intermediate)", callback_data="level_B2 (Upper-Intermediate)")],
        [InlineKeyboardButton("📊 Общий прогресс", callback_data="total_progress")],
        [InlineKeyboardButton("🚪 Выйти", callback_data="logout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"🎓 *Soloway English Tracker*\n\n👤 {context.user_data.get('username')}\n\nВыбери уровень:"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выход из аккаунта"""
    context.user_data.clear()
    await update.callback_query.answer("🚪 Выход...")
    keyboard = [
        [InlineKeyboardButton("🔑 Войти", callback_data="login")],
        [InlineKeyboardButton("📝 Зарегистрироваться", callback_data="register")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "👋 Ты вышел из аккаунта.\n\nЧтобы продолжить, войди или зарегистрируйся:",
        reply_markup=reply_markup
    )

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE, level):
    """Показывает категории"""
    user_id = context.user_data.get("user_id")
    if not user_id:
        await start(update, context)
        return
    
    categories = list(TOPICS[level].keys())
    keyboard = []
    for cat in categories:
        progress = get_progress(user_id, level)
        total = len(TOPICS[level][cat])
        done = sum(1 for topic in TOPICS[level][cat] if progress.get(topic, 0))
        keyboard.append([InlineKeyboardButton(f"{cat} ({done}/{total})", callback_data=f"cat_{level}|{cat}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_levels")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(f"📚 {level}\n\nВыбери категорию:", reply_markup=reply_markup)

async def show_topics(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, page=0):
    """Показывает темы"""
    user_id = context.user_data.get("user_id")
    if not user_id:
        await start(update, context)
        return
    
    topics = TOPICS[level][category]
    progress = get_progress(user_id, level)
    per_page = 8
    total_pages = (len(topics) + per_page - 1) // per_page
    if page < 0: page = 0
    if page >= total_pages: page = total_pages - 1
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(topics))
    keyboard = []
    for idx in range(start_idx, end_idx):
        topic = topics[idx]
        done = progress.get(topic, 0)
        emoji = "✅" if done else "⬜"
        keyboard.append([InlineKeyboardButton(f"{emoji} {topic}", callback_data=f"topic_{level}|{category}|{idx}")])
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀️", callback_data=f"page_{level}|{category}|{page-1}"))
    nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("▶️", callback_data=f"page_{level}|{category}|{page+1}"))
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"level_{level}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    total = len(topics)
    done = sum(1 for t in topics if progress.get(t, 0))
    percent = int(done / total * 100) if total > 0 else 0
    bar = "🟩" * (percent // 10) + "⬜" * (10 - percent // 10)
    await update.callback_query.edit_message_text(
        f"📚 {level} → {category}\n\n{bar} {done}/{total} ({percent}%)\n\nСтр. {page+1}/{total_pages}:",
        reply_markup=reply_markup
    )

async def show_topic_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    """Показывает меню для конкретной темы"""
    user_id = context.user_data.get("user_id")
    if not user_id:
        await start(update, context)
        return
    
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    progress = get_progress(user_id, level)
    done = progress.get(topic, 0)
    status = "✅ Пройдена" if done else "⬜ Не пройдена"
    
    has_expl = False
    try:
        if level in TESTS:
            for cat in TESTS[level]:
                if topic in TESTS[level][cat]:
                    expl = TESTS[level][cat][topic].get("explanation")
                    if expl and isinstance(expl, dict):
                        has_expl = True
                        break
    except:
        pass
    
    has_vocab = False
    try:
        if level in TESTS:
            for cat in TESTS[level]:
                if topic in TESTS[level][cat]:
                    vocab = TESTS[level][cat][topic].get("vocabulary")
                    if vocab:
                        has_vocab = True
                        break
    except:
        pass
    
    keyboard = [
        [InlineKeyboardButton("✅ Отметить" if not done else "❌ Снять отметку", callback_data=f"tog_{level}|{category}|{idx}")],
    ]
    if has_expl:
        keyboard.append([InlineKeyboardButton("📖 Теория", callback_data=f"expl_{level}|{category}|{idx}")])
    if has_vocab:
        keyboard.append([InlineKeyboardButton("📚 Словарь", callback_data=f"vocab_{level}|{category}|{idx}")])
    if has_test(level, topic):
        keyboard.append([InlineKeyboardButton("📝 Пройти тест (8 вопросов)", callback_data=f"test_{level}|{category}|{idx}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{level}|{category}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        f"📚 {topic}\n\n{status}\n\nВыбери действие:",
        reply_markup=reply_markup
    )

async def show_explanation(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    """Показывает таблицу с теорией"""
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    expl_data = None
    try:
        if level in TESTS:
            for cat in TESTS[level]:
                if topic in TESTS[level][cat]:
                    expl = TESTS[level][cat][topic].get("explanation")
                    if expl and isinstance(expl, dict):
                        expl_data = expl
                        break
    except:
        pass
    
    if not expl_data:
        await update.callback_query.answer("❌ Теория пока не добавлена", show_alert=True)
        return
    
    buf = generate_table_image(expl_data["headers"], expl_data["rows"], topic)
    keyboard = [[InlineKeyboardButton("🔙 К теме", callback_data=f"topic_{level}|{category}|{idx}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.message.delete()
    except:
        pass
    await update.effective_chat.send_photo(photo=buf, caption=f"📖 {topic}", reply_markup=reply_markup)

async def show_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    """Показывает словарь"""
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    vocab_data = None
    try:
        if level in TESTS:
            for cat in TESTS[level]:
                if topic in TESTS[level][cat]:
                    vocab = TESTS[level][cat][topic].get("vocabulary")
                    if vocab:
                        vocab_data = vocab
                        break
    except:
        pass
    
    if not vocab_data:
        await update.callback_query.answer("❌ Словарь пока не добавлен", show_alert=True)
        return
    
    if isinstance(vocab_data, list):
        for i, table in enumerate(vocab_data):
            buf = generate_table_image(table["headers"], table["rows"], f"{topic} (часть {i+1})")
            try:
                if i == 0:
                    await update.callback_query.message.delete()
            except:
                pass
            await update.effective_chat.send_photo(
                photo=buf,
                caption=f"📚 {topic} - Словарь" if i == 0 else "",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 К теме", callback_data=f"topic_{level}|{category}|{idx}")]]) if i == len(vocab_data) - 1 else None
            )
    else:
        buf = generate_table_image(vocab_data["headers"], vocab_data["rows"], f"📚 {topic}")
        try:
            await update.callback_query.message.delete()
        except:
            pass
        await update.effective_chat.send_photo(
            photo=buf,
            caption=f"📚 {topic} - Словарь",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 К теме", callback_data=f"topic_{level}|{category}|{idx}")]])
        )

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    """Запускает тест"""
    user_id = context.user_data.get("user_id")
    if not user_id:
        await start(update, context)
        return
    
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    test_data = None
    try:
        if level in TESTS:
            for cat in TESTS[level]:
                if topic in TESTS[level][cat]:
                    if "questions" in TESTS[level][cat][topic]:
                        test_data = TESTS[level][cat][topic]
                        break
    except:
        pass
    
    if not test_data or "questions" not in test_data:
        await update.callback_query.answer("❌ Тест не найден", show_alert=True)
        return
    
    questions = test_data["questions"]
    context.user_data["test"] = {
        "level": level,
        "category": category,
        "topic": topic,
        "questions": questions,
        "current": 0,
        "score": 0,
        "user_answers": [],
        "user_id": user_id
    }
    await show_question(update, context)

async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    test = context.user_data.get("test")
    if not test: return
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
        f"📝 *Тест: {test['topic']}*\n\nВопрос {q_num + 1}/{len(test['questions'])}:\n\n*{question['q']}*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, answer_idx):
    test = context.user_data.get("test")
    if not test:
        await update.callback_query.answer("Тест не найден.")
        return
    question = test["questions"][test["current"]]
    correct = question["answer"]
    correct_ans = question["options"][correct]
    user_answer = question["options"][answer_idx]
    is_correct = (answer_idx == correct)
    test["user_answers"].append({
        "question": question["q"],
        "user_answer": user_answer,
        "correct_answer": correct_ans,
        "is_correct": is_correct
    })
    if is_correct:
        test["score"] += 1
        await update.callback_query.answer(f"✅ Правильно! ({correct_ans})")
    else:
        await update.callback_query.answer(
            f"❌ Твой ответ: {user_answer}. Правильно: {correct_ans}",
            show_alert=True
        )
    test["current"] += 1
    if test["current"] >= len(test["questions"]):
        await finish_test(update, context)
    else:
        await show_question(update, context)

async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    test = context.user_data.get("test")
    if not test: return
    score = test["score"]
    total = len(test["questions"])
    percent = int(score / total * 100)
    user_id = test["user_id"]
    save_test_result(user_id, test["level"], test["category"], test["topic"], score, total)
    
    if percent == 100:
        emoji, comment = "🏆", "Идеально!"
    elif percent >= 75:
        emoji, comment = "🎉", "Хороший результат!"
    elif percent >= 50:
        emoji, comment = "📚", "Неплохо! Но стоит повторить."
    else:
        emoji, comment = "💪", "Нужно подучить."
    
    wrong_answers = [ans for ans in test["user_answers"] if not ans["is_correct"]]
    idx = find_topic_index(test["level"], test["category"], test["topic"])
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти ещё раз", callback_data=f"test_{test['level']}|{test['category']}|{idx}")],
        [InlineKeyboardButton("🔙 К теме", callback_data=f"topic_{test['level']}|{test['category']}|{idx}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    result_text = f"{emoji} *Тест завершён!*\n\n📝 {test['topic']}\n📊 Результат: {score}/{total} ({percent}%)\n\n{comment}"
    if wrong_answers:
        result_text += f"\n\n❌ *Ошибки: {len(wrong_answers)} из {total}*"
    
    await update.callback_query.edit_message_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    if wrong_answers:
        for i in range(0, len(wrong_answers), 2):
            chunk = wrong_answers[i:i+2]
            error_text = "*❌ Ошибки:*\n\n"
            for j, wrong in enumerate(chunk, i+1):
                error_text += f"{j}. *{wrong['question']}*\n   ❌ Ваш ответ: {wrong['user_answer']}\n   ✅ Правильно: {wrong['correct_answer']}\n\n"
            await update.effective_chat.send_message(error_text, parse_mode="Markdown")
    
    del context.user_data["test"]

async def toggle_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, level, category, idx):
    user_id = context.user_data.get("user_id")
    if not user_id:
        await start(update, context)
        return
    
    topics = TOPICS[level][category]
    topic = topics[int(idx)]
    new_status = toggle_topic(user_id, level, category, topic)
    await update.callback_query.answer(f"{'✅ Отмечено!' if new_status else '❌ Снято!'}")
    await show_topic_menu(update, context, level, category, idx)

async def show_total_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("user_id")
    if not user_id:
        await start(update, context)
        return
    
    text = "📊 *Общий прогресс*\n\n"
    total_all = done_all = 0
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
    
    # Если админ — добавляем кнопку управления пользователями
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_levels")]]
    if context.user_data.get("is_admin"):
        keyboard.append([InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# ===== АДМИН-ФУНКЦИИ =====

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список пользователей (только для админа)"""
    if not context.user_data.get("is_admin"):
        await update.callback_query.answer("❌ Нет доступа", show_alert=True)
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, is_admin FROM users ORDER BY id")
    users = c.fetchall()
    conn.close()
    
    text = "👥 *Список пользователей*\n\n"
    for user in users:
        role = "👑 Админ" if user[2] else "👤 Пользователь"
        text += f"ID: {user[0]} | {user[1]} — {role}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_levels")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back_to_levels":
        await show_levels(update, context)
    elif data == "total_progress":
        await show_total_progress(update, context)
    elif data == "logout":
        await logout(update, context)
    elif data == "login":
        await show_login(update, context)
    elif data == "register":
        await show_register(update, context)
    elif data == "admin_users":
        await admin_users(update, context)
    elif data == "noop":
        pass
    elif data.startswith("level_"):
        await show_categories(update, context, data[6:])
    elif data.startswith("cat_"):
        parts = data[4:].split("|")
        await show_topics(update, context, parts[0], parts[1], 0)
    elif data.startswith("topic_"):
        parts = data[6:].split("|")
        await show_topic_menu(update, context, parts[0], parts[1], parts[2])
    elif data.startswith("page_"):
        parts = data[5:].split("|")
        await show_topics(update, context, parts[0], parts[1], int(parts[2]))
    elif data.startswith("expl_"):
        parts = data[5:].split("|")
        await show_explanation(update, context, parts[0], parts[1], parts[2])
    elif data.startswith("vocab_"):
        parts = data[6:].split("|")
        await show_vocabulary(update, context, parts[0], parts[1], parts[2])
    elif data.startswith("tog_"):
        parts = data[4:].split("|")
        await toggle_topic_handler(update, context, parts[0], parts[1], parts[2])
    elif data.startswith("test_"):
        parts = data[5:].split("|")
        await start_test(update, context, parts[0], parts[1], parts[2])
    elif data.startswith("ans_"):
        await handle_answer(update, context, int(data[4:]))

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    print("🎓 Soloway English Tracker запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()