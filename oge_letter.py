# ===== ОГЭ: ПИСЬМО (ЗАДАНИЕ 35) =====

import re
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ===== КОНСТАНТЫ =====

# Приветственные фразы для письма
GREETINGS = [
    "dear", "hi", "hello", "hey", "good morning", "good afternoon", "good evening"
]

# Фразы благодарности
THANK_YOU_PHRASES = [
    "thank you for", "thanks for", "i'm grateful for", "i appreciate"
]

# Фразы для выражения эмоций
EMOTION_PHRASES = [
    "i'm glad", "i am glad", "i'm happy", "i am happy", "i was glad", 
    "i was happy", "it was great", "it was nice", "i enjoyed"
]

# Фразы для надежды на последующие контакты
FUTURE_CONTACT_PHRASES = [
    "write soon", "write back soon", "hope to hear from you", 
    "looking forward to", "waiting for your reply", "hope you'll write",
    "keep in touch", "stay in touch", "i look forward"
]

# Завершающие фразы
CLOSING_PHRASES = [
    "best wishes", "with love", "yours sincerely", "yours faithfully",
    "all the best", "take care", "see you soon", "warm regards",
    "kind regards", "lots of love", "love", "cheers", "yours",
    "sincerely", "regards"
]

# ===== ФУНКЦИИ ПРОВЕРКИ =====

def count_words(text):
    """Подсчёт слов в письме по правилам ОГЭ"""
    if not text:
        return 0
    
    # Убираем лишние пробелы
    text = text.strip()
    
    # Считаем слова
    words = re.findall(r"[a-zA-Zа-яА-Я0-9\-']+", text)
    return len(words)

def check_letter_structure(text):
    """Проверка структуры письма"""
    text_lower = text.lower()
    
    # 1. Проверка обращения
    has_greeting = any(greeting in text_lower for greeting in GREETINGS)
    
    # 2. Проверка благодарности
    has_thanks = any(phrase in text_lower for phrase in THANK_YOU_PHRASES)
    
    # 3. Проверка эмоций
    has_emotion = any(phrase in text_lower for phrase in EMOTION_PHRASES)
    
    # 4. Проверка надежды на последующие контакты
    has_future_contact = any(phrase in text_lower for phrase in FUTURE_CONTACT_PHRASES)
    
    # 5. Проверка завершающей фразы и подписи
    has_closing = any(phrase in text_lower for phrase in CLOSING_PHRASES)
    
    # 6. Проверка подписи (имя в конце)
    lines = text.split('\n')
    has_signature = False
    if lines:
        last_line = lines[-1].strip().lower()
        # Имя обычно 2-4 слова, начинается с заглавной буквы
        if re.match(r'^[a-z]+\s*[a-z]*$', last_line) and len(last_line) > 2:
            has_signature = True
    
    # 7. Проверка, что письмо разделено на абзацы
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    has_paragraphs = len(paragraphs) >= 3  # Обычно: обращение, тело, подпись
    
    return {
        "has_greeting": has_greeting,
        "has_thanks": has_thanks,
        "has_emotion": has_emotion,
        "has_future_contact": has_future_contact,
        "has_closing": has_closing,
        "has_signature": has_signature,
        "has_paragraphs": has_paragraphs
    }

def check_questions_answered(text, questions):
    """Проверка ответов на вопросы"""
    text_lower = text.lower()
    answers = []
    
    for i, question in enumerate(questions):
        # Ищем ключевые слова из вопроса в тексте
        keywords = question.lower().replace('?', '').split()
        found = any(keyword in text_lower for keyword in keywords)
        answers.append({
            "question": question,
            "answered": found,
            "keywords": keywords
        })
    
    return answers

def check_grammar_and_vocabulary(text):
    """Упрощённая проверка лексико-грамматического оформления"""
    errors = []
    
    # Проверка на повторяющиеся слова (простейший случай)
    words = re.findall(r'[a-zA-Z]+', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Игнорируем короткие слова
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Слишком частые повторы
    for word, count in word_freq.items():
        if count > 5:
            errors.append(f"Повтор слова '{word}' ({count} раз)")
    
    # Проверка на наличие базовых грамматических конструкций
    has_verb_to_be = any(verb in text.lower() for verb in ['is', 'am', 'are', 'was', 'were'])
    if not has_verb_to_be:
        errors.append("Нет глаголов to be (возможно, проблемы с грамматикой)")
    
    # Проверка на наличие базовых союзов
    has_conjunctions = any(conj in text.lower() for conj in ['and', 'but', 'because', 'so', 'however'])
    if not has_conjunctions:
        errors.append("Нет союзов (and, but, because, so, however)")
    
    # Проверка артиклей (простейшая)
    article_errors = re.findall(r'(?<![a-z])[a-z](?![a-z])', text)
    if len(article_errors) > 5:
        errors.append("Возможны ошибки с артиклями")
    
    return errors

def check_spelling(text):
    """Упрощённая проверка орфографии и пунктуации"""
    errors = []
    
    # Проверка на отсутствие заглавных букв после точек
    sentences = re.split(r'[.!?]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence[0].islower():
            errors.append("Предложение начинается со строчной буквы")
            break
    
    # Проверка на точки в конце предложений
    if not re.search(r'[.!?]$', text.strip()):
        errors.append("Нет точки в конце письма")
    
    # Проверка на наличие запятых
    if ',' not in text:
        errors.append("Нет запятых (возможно, проблемы с пунктуацией)")
    
    # Базовые орфографические ошибки (проверка частых ошибок)
    common_mistakes = {
        r'teh': 'the',
        r'wich': 'which',
        r'thier': 'their',
        r'there is': 'there are'
    }
    
    for mistake, correction in common_mistakes.items():
        if re.search(mistake, text.lower()):
            errors.append(f"Орфографическая ошибка: '{mistake}' → '{correction}'")
    
    return errors

def check_letter(text, questions):
    """Основная функция проверки письма"""
    
    # 1. Проверка объёма
    word_count = count_words(text)
    volume_ok = 90 <= word_count <= 132
    
    if word_count < 90:
        return {
            "error": "Недостаточный объём",
            "message": f"В письме {word_count} слов. Минимум 90 слов. Задание оценивается 0 баллов."
        }
    
    if word_count > 132:
        # Обрезаем до 120 слов для проверки
        words = text.split()
        text = ' '.join(words[:120])
        word_count = 120
    
    # 2. Проверка структуры
    structure = check_letter_structure(text)
    
    # 3. Проверка ответов на вопросы
    answers = check_questions_answered(text, questions)
    answered_count = sum(1 for a in answers if a["answered"])
    
    # 4. Проверка грамматики
    grammar_errors = check_grammar_and_vocabulary(text)
    
    # 5. Проверка орфографии
    spelling_errors = check_spelling(text)
    
    # 6. Оценка по критериям
    
    # К1: Решение коммуникативной задачи (0-3)
    k1_score = 0
    
    # Проверяем ответы на 3 вопроса
    if answered_count == 3:
        # Все вопросы раскрыты
        if structure["has_greeting"] and structure["has_closing"] and structure["has_signature"]:
            k1_score = 3
        else:
            k1_score = 2
    elif answered_count >= 2:
        # 2 вопроса раскрыты
        if structure["has_greeting"] and structure["has_closing"]:
            k1_score = 2
        else:
            k1_score = 1
    elif answered_count >= 1:
        k1_score = 1
    else:
        k1_score = 0
    
    # Корректируем K1 за структуру
    if not structure["has_greeting"] and k1_score > 1:
        k1_score -= 1
    if not structure["has_closing"] and k1_score > 1:
        k1_score -= 1
    
    # Если 0 по К1, всё задание 0 баллов
    if k1_score == 0:
        return {
            "error": "К1 = 0",
            "message": "Задание оценивается 0 баллов по всем критериям.",
            "word_count": word_count,
            "k1_score": 0,
            "k2_score": 0,
            "k3_score": 0,
            "k4_score": 0,
            "total": 0,
            "details": {
                "answered_questions": answered_count,
                "structure": structure,
                "answers": answers,
                "grammar_errors": grammar_errors,
                "spelling_errors": spelling_errors
            }
        }
    
    # К2: Организация текста (0-2)
    k2_score = 2
    errors_org = 0
    
    if not structure["has_greeting"]:
        errors_org += 1
    if not structure["has_closing"]:
        errors_org += 1
    if not structure["has_signature"]:
        errors_org += 1
    if not structure["has_paragraphs"]:
        errors_org += 1
    if not structure["has_thanks"]:
        errors_org += 0.5
    if not structure["has_future_contact"]:
        errors_org += 0.5
    
    if errors_org >= 4:
        k2_score = 0
    elif errors_org >= 2:
        k2_score = 1
    else:
        k2_score = 2
    
    # К3: Лексико-грамматическое оформление (0-3)
    k3_score = 3
    grammar_errors_count = len(grammar_errors)
    
    if grammar_errors_count >= 5:
        k3_score = 0
    elif grammar_errors_count >= 4:
        k3_score = 1
    elif grammar_errors_count >= 2:
        k3_score = 2
    else:
        k3_score = 3
    
    # К4: Орфография и пунктуация (0-2)
    k4_score = 2
    spelling_errors_count = len(spelling_errors)
    
    if spelling_errors_count >= 5:
        k4_score = 0
    elif spelling_errors_count >= 3:
        k4_score = 1
    else:
        k4_score = 2
    
    # Итоговый балл
    total = k1_score + k2_score + k3_score + k4_score
    
    return {
        "word_count": word_count,
        "k1_score": k1_score,
        "k2_score": k2_score,
        "k3_score": k3_score,
        "k4_score": k4_score,
        "total": total,
        "max_total": 10,
        "details": {
            "answered_questions": answered_count,
            "total_questions": len(questions),
            "structure": structure,
            "answers": answers,
            "grammar_errors": grammar_errors,
            "grammar_errors_count": grammar_errors_count,
            "spelling_errors": spelling_errors,
            "spelling_errors_count": spelling_errors_count,
            "volume_ok": 90 <= word_count <= 132
        }
    }

def format_letter_result(result):
    """Форматирует результат проверки письма"""
    
    if "error" in result:
        return f"❌ *{result['error']}*\n\n{result['message']}"
    
    details = result["details"]
    
    # Эмодзи для оценки
    total = result["total"]
    if total == 10:
        emoji = "🏆"
    elif total >= 8:
        emoji = "🎉"
    elif total >= 6:
        emoji = "📚"
    else:
        emoji = "💪"
    
    # Прогресс-бар
    bar_length = 10
    filled = int(total / 10 * bar_length)
    bar = "🟩" * filled + "⬜" * (bar_length - filled)
    
    text = f"{emoji} *Результат проверки письма*\n\n"
    text += f"📊 {bar} {total}/10\n\n"
    
    # Объём
    word_count = result["word_count"]
    volume_status = "✅" if details["volume_ok"] else "⚠️"
    text += f"📝 *Объём:* {word_count} слов {volume_status}\n"
    if not details["volume_ok"]:
        if word_count < 90:
            text += "⚠️ *Меньше 90 слов! Задание оценивается 0 баллов.*\n\n"
        else:
            text += "ℹ️ Больше 132 слов. Проверено 120 слов.\n\n"
    else:
        text += "\n"
    
    # К1
    text += f"📋 *К1 — Решение коммуникативной задачи:* {result['k1_score']}/3\n"
    text += f"   Ответы на вопросы: {details['answered_questions']}/{details['total_questions']}\n"
    for i, answer in enumerate(details["answers"]):
        icon = "✅" if answer["answered"] else "❌"
        text += f"   {icon} Вопрос {i+1}: {answer['question'][:50]}...\n"
    
    # Структура
    text += "\n   *Структура письма:*\n"
    text += f"   {'✅' if details['structure']['has_greeting'] else '❌'} Обращение\n"
    text += f"   {'✅' if details['structure']['has_thanks'] else '❌'} Благодарность\n"
    text += f"   {'✅' if details['structure']['has_emotion'] else '❌'} Эмоции\n"
    text += f"   {'✅' if details['structure']['has_future_contact'] else '❌'} Надежда на ответ\n"
    text += f"   {'✅' if details['structure']['has_closing'] else '❌'} Завершающая фраза\n"
    text += f"   {'✅' if details['structure']['has_signature'] else '❌'} Подпись\n"
    text += f"   {'✅' if details['structure']['has_paragraphs'] else '❌'} Абзацы\n\n"
    
    # К2
    text += f"📋 *К2 — Организация текста:* {result['k2_score']}/2\n\n"
    
    # К3
    text += f"📋 *К3 — Лексико-грамматическое оформление:* {result['k3_score']}/3\n"
    if details["grammar_errors"]:
        text += "   ❌ Найдено проблем:\n"
        for error in details["grammar_errors"][:3]:
            text += f"      • {error}\n"
        if len(details["grammar_errors"]) > 3:
            text += f"      ... и ещё {len(details['grammar_errors']) - 3} проблем\n"
    text += "\n"
    
    # К4
    text += f"📋 *К4 — Орфография и пунктуация:* {result['k4_score']}/2\n"
    if details["spelling_errors"]:
        text += "   ❌ Найдено проблем:\n"
        for error in details["spelling_errors"][:3]:
            text += f"      • {error}\n"
        if len(details["spelling_errors"]) > 3:
            text += f"      ... и ещё {len(details['spelling_errors']) - 3} проблем\n"
    text += "\n"
    
    # Итог
    text += f"⭐ *Итоговый балл: {total}/10*"
    
    return text

# ===== ОСНОВНЫЕ ОБРАБОТЧИКИ =====

async def start_letter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает задание — письмо"""
    if not context.user_data.get("authenticated"):
        await update.callback_query.answer("❌ Пожалуйста, войдите в аккаунт", show_alert=True)
        return
    
    # Загружаем задания по письму
    data = load_letter_tasks()
    if not data:
        await update.callback_query.answer("❌ Задания не загружены", show_alert=True)
        return
    
    tasks = data.get("tasks", [])
    if not tasks:
        await update.callback_query.answer("❌ Нет заданий", show_alert=True)
        return
    
    context.user_data["letter"] = {
        "tasks": tasks,
        "current": 0,
        "total": len(tasks),
        "results": []
    }
    
    await show_letter_task(update, context)

def load_letter_tasks():
    """Загружает задания по письму"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_paths = [
            os.path.join(base_dir, "oge_letter.json"),
            os.path.join("/app", "oge_letter.json"),
            os.path.join(os.getcwd(), "oge_letter.json")
        ]
        
        for path in json_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"✅ Загружен oge_letter.json: {len(data.get('tasks', []))} заданий")
                    return data
        
        # Если файла нет, создаём дефолтное задание
        default_tasks = {
            "tasks": [
                {
                    "id": "letter_1",
                    "from": "Paige@mail.uk",
                    "to": "Russian_friend@sdamgia.ru",
                    "subject": "Dear friend",
                    "email_text": "Last Friday was a busy day. We had classes till 3 pm and then we went to the museum. I always thought that museums were boring and I didn't feel excited about the excursion at all. To my surprise, I enjoyed it very much!",
                    "questions": [
                        "Do you think that visiting museums and exhibitions is boring or not, why?",
                        "When was the last time you were in a museum?",
                        "What kind of museum / exhibition would you like to visit, why?"
                    ]
                }
            ]
        }
        
        # Сохраняем дефолтное задание
        default_path = os.path.join(base_dir, "oge_letter.json")
        with open(default_path, "w", encoding="utf-8") as f:
            json.dump(default_tasks, f, ensure_ascii=False, indent=2)
        print(f"✅ Создан дефолтный oge_letter.json")
        return default_tasks
        
    except Exception as e:
        print(f"❌ Ошибка загрузки oge_letter.json: {e}")
        return None

async def show_letter_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текущее задание по письму"""
    session = context.user_data.get("letter")
    if not session:
        return
    
    current = session["current"]
    tasks = session["tasks"]
    
    if current >= session["total"]:
        await finish_letter_session(update, context)
        return
    
    task = tasks[current]
    
    # Формируем текст задания
    text = f"✉️ *Задание 35. Письмо*\n\n"
    text += f"Задание {current + 1} из {session['total']}\n\n"
    text += f"📧 *От:* {task['from']}\n"
    text += f"📧 *Кому:* {task['to']}\n"
    text += f"📌 *Тема:* {task['subject']}\n\n"
    text += f"*{task['email_text']}*\n\n"
    
    text += "❓ *Ответь на вопросы:*\n"
    for i, question in enumerate(task["questions"], 1):
        text += f"{i}. {question}\n"
    
    text += f"\n⏱️ *Время:* 30 минут\n"
    text += f"📝 *Объём:* 100-120 слов\n\n"
    text += "✏️ *Напиши своё письмо в чат:*"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data["current_letter_task"] = task
    context.user_data["awaiting_letter"] = True
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_letter_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ на письмо"""
    text = update.message.text.strip()
    
    if not text:
        await update.message.reply_text("❌ Пожалуйста, напиши письмо.")
        return
    
    task = context.user_data.get("current_letter_task")
    if not task:
        await update.message.reply_text("❌ Задание не найдено. Начни заново.")
        return
    
    # Проверяем письмо
    result = check_letter(text, task["questions"])
    
    # Форматируем результат
    result_text = format_letter_result(result)
    
    # Сохраняем результат в сессию
    session = context.user_data.get("letter")
    if session:
        session["results"].append({
            "task": task,
            "text": text,
            "result": result
        })
    
    # Отправляем результат
    keyboard = [
        [InlineKeyboardButton("➡️ Следующее задание", callback_data="letter_next")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    context.user_data["awaiting_letter"] = False

async def letter_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переход к следующему заданию"""
    session = context.user_data.get("letter")
    if not session:
        await update.callback_query.answer("❌ Сессия не найдена", show_alert=True)
        return
    
    session["current"] += 1
    await show_letter_task(update, context)

async def finish_letter_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершает сессию писем"""
    session = context.user_data.get("letter")
    if not session:
        return
    
    results = session.get("results", [])
    total = session["total"]
    
    # Считаем средний балл
    avg_score = 0
    if results:
        total_scores = []
        for r in results:
            if "total" in r["result"]:
                total_scores.append(r["result"]["total"])
        if total_scores:
            avg_score = sum(total_scores) / len(total_scores)
    
    text = "✉️ *Все письма выполнены!*\n\n"
    text += f"📊 *Выполнено:* {len(results)} из {total}\n"
    text += f"⭐ *Средний балл:* {avg_score:.1f}/10\n\n"
    
    if avg_score >= 9:
        text += "🏆 *Отличный результат! Ты готов к письму на ОГЭ!*"
    elif avg_score >= 7:
        text += "📚 *Хороший результат! Продолжай тренироваться.*"
    else:
        text += "💪 *Нужно ещё немного практики. Попробуй ещё раз!*"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти заново", callback_data="start_letter")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    del context.user_data["letter"]
    context.user_data["awaiting_letter"] = False