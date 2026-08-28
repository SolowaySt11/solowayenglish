# ===== ОГЭ: ПИСЬМО (ЗАДАНИЕ 35) =====

import re
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ===== КОНСТАНТЫ =====

GREETINGS = [
    "dear", "hi", "hello", "hey", "good morning", "good afternoon", "good evening"
]

THANK_YOU_PHRASES = [
    "thank you for", "thanks for", "i'm grateful for", "i appreciate"
]

EMOTION_PHRASES = [
    "i'm glad", "i am glad", "i'm happy", "i am happy", "i was glad", 
    "i was happy", "it was great", "it was nice", "i enjoyed"
]

FUTURE_CONTACT_PHRASES = [
    "write soon", "write back soon", "hope to hear from you", 
    "looking forward to", "waiting for your reply", "hope you'll write",
    "keep in touch", "stay in touch", "i look forward"
]

CLOSING_PHRASES = [
    "best wishes", "with love", "yours sincerely", "yours faithfully",
    "all the best", "take care", "see you soon", "warm regards",
    "kind regards", "lots of love", "love", "cheers", "yours",
    "sincerely", "regards"
]

# ===== ФУНКЦИИ ПРОВЕРКИ =====

def count_words(text):
    if not text:
        return 0
    text = text.strip()
    words = re.findall(r"[a-zA-Zа-яА-Я0-9\-']+", text)
    return len(words)

def check_letter_structure(text):
    text_lower = text.lower()
    
    has_greeting = any(greeting in text_lower for greeting in GREETINGS)
    has_thanks = any(phrase in text_lower for phrase in THANK_YOU_PHRASES)
    has_emotion = any(phrase in text_lower for phrase in EMOTION_PHRASES)
    has_future_contact = any(phrase in text_lower for phrase in FUTURE_CONTACT_PHRASES)
    has_closing = any(phrase in text_lower for phrase in CLOSING_PHRASES)
    
    lines = text.split('\n')
    has_signature = False
    if lines:
        last_line = lines[-1].strip().lower()
        if re.match(r'^[a-z]+\s*[a-z]*$', last_line) and len(last_line) > 2:
            has_signature = True
    
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    has_paragraphs = len(paragraphs) >= 3
    
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
    text_lower = text.lower()
    answers = []
    
    for question in questions:
        keywords = question.lower().replace('?', '').split()
        found = any(keyword in text_lower for keyword in keywords[:3])
        answers.append({
            "question": question,
            "answered": found
        })
    
    return answers

def check_grammar_and_vocabulary(text):
    errors = []
    
    words = re.findall(r'[a-zA-Z]+', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    for word, count in word_freq.items():
        if count > 5:
            errors.append(f"Повтор слова '{word}' ({count} раз)")
    
    has_verb_to_be = any(verb in text.lower() for verb in ['is', 'am', 'are', 'was', 'were'])
    if not has_verb_to_be:
        errors.append("Нет глаголов to be")
    
    has_conjunctions = any(conj in text.lower() for conj in ['and', 'but', 'because', 'so', 'however'])
    if not has_conjunctions:
        errors.append("Нет союзов (and, but, because, so, however)")
    
    return errors

def check_spelling(text):
    errors = []
    
    sentences = re.split(r'[.!?]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence[0].islower():
            errors.append("Предложение начинается со строчной буквы")
            break
    
    if not re.search(r'[.!?]$', text.strip()):
        errors.append("Нет точки в конце письма")
    
    if ',' not in text:
        errors.append("Нет запятых")
    
    common_mistakes = {
        r'teh': 'the',
        r'wich': 'which',
        r'thier': 'their'
    }
    
    for mistake, correction in common_mistakes.items():
        if re.search(mistake, text.lower()):
            errors.append(f"Ошибка: '{mistake}' → '{correction}'")
    
    return errors

def check_letter(text, questions):
    word_count = count_words(text)
    volume_ok = 90 <= word_count <= 132
    
    if word_count < 90:
        return {
            "error": True,
            "word_count": word_count,
            "message": f"В письме {word_count} слов. Минимум 90 слов. Задание оценивается 0 баллов.",
            "k1_score": 0,
            "k2_score": 0,
            "k3_score": 0,
            "k4_score": 0,
            "total": 0,
            "details": {
                "answered_questions": 0,
                "total_questions": len(questions),
                "volume_ok": False
            }
        }
    
    if word_count > 132:
        words = text.split()
        text = ' '.join(words[:120])
        word_count = 120
    
    structure = check_letter_structure(text)
    answers = check_questions_answered(text, questions)
    answered_count = sum(1 for a in answers if a["answered"])
    grammar_errors = check_grammar_and_vocabulary(text)
    spelling_errors = check_spelling(text)
    
    # К1
    k1_score = 0
    if answered_count == 3:
        if structure["has_greeting"] and structure["has_closing"] and structure["has_signature"]:
            k1_score = 3
        else:
            k1_score = 2
    elif answered_count >= 2:
        if structure["has_greeting"] and structure["has_closing"]:
            k1_score = 2
        else:
            k1_score = 1
    elif answered_count >= 1:
        k1_score = 1
    else:
        k1_score = 0
    
    if not structure["has_greeting"] and k1_score > 1:
        k1_score -= 1
    if not structure["has_closing"] and k1_score > 1:
        k1_score -= 1
    
    if k1_score <= 0:
        return {
            "error": True,
            "word_count": word_count,
            "message": "Задание оценивается 0 баллов по всем критериям (К1 = 0).",
            "k1_score": 0,
            "k2_score": 0,
            "k3_score": 0,
            "k4_score": 0,
            "total": 0,
            "details": {
                "answered_questions": answered_count,
                "total_questions": len(questions),
                "volume_ok": volume_ok
            }
        }
    
    # К2
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
    
    # К3
    grammar_count = len(grammar_errors)
    if grammar_count >= 5:
        k3_score = 0
    elif grammar_count >= 4:
        k3_score = 1
    elif grammar_count >= 2:
        k3_score = 2
    else:
        k3_score = 3
    
    # К4
    spelling_count = len(spelling_errors)
    if spelling_count >= 5:
        k4_score = 0
    elif spelling_count >= 3:
        k4_score = 1
    else:
        k4_score = 2
    
    total = k1_score + k2_score + k3_score + k4_score
    
    return {
        "error": False,
        "word_count": word_count,
        "k1_score": k1_score,
        "k2_score": k2_score,
        "k3_score": k3_score,
        "k4_score": k4_score,
        "total": total,
        "details": {
            "answered_questions": answered_count,
            "total_questions": len(questions),
            "structure": structure,
            "answers": answers,
            "grammar_errors": grammar_errors,
            "grammar_errors_count": grammar_count,
            "spelling_errors": spelling_errors,
            "spelling_errors_count": spelling_count,
            "volume_ok": volume_ok
        }
    }

def format_letter_result(result):
    """Форматирует результат БЕЗ использования Markdown"""
    
    if result.get("error"):
        text = "❌ РЕЗУЛЬТАТ ПРОВЕРКИ ПИСЬМА\n\n"
        text += f"📝 Объём: {result.get('word_count', 0)} слов\n\n"
        text += result.get("message", "Ошибка проверки")
        return text
    
    details = result["details"]
    total = result["total"]
    
    if total == 10:
        emoji = "🏆"
    elif total >= 8:
        emoji = "🎉"
    elif total >= 6:
        emoji = "📚"
    else:
        emoji = "💪"
    
    bar = "█" * (total) + "░" * (10 - total)
    
    text = f"{emoji} РЕЗУЛЬТАТ ПРОВЕРКИ ПИСЬМА\n\n"
    text += f"📊 {bar} {total}/10\n\n"
    
    text += f"📝 Объём: {result['word_count']} слов\n\n"
    
    # К1
    text += f"📋 К1 — Решение коммуникативной задачи: {result['k1_score']}/3\n"
    text += f"   Ответы на вопросы: {details['answered_questions']}/{details['total_questions']}\n"
    
    for i, answer in enumerate(details.get("answers", []), 1):
        icon = "✅" if answer["answered"] else "❌"
        q_text = answer['question'][:50] + "..." if len(answer['question']) > 50 else answer['question']
        text += f"   {icon} Вопрос {i}: {q_text}\n"
    
    # Структура
    if "structure" in details:
        text += "\n   Структура письма:\n"
        s = details["structure"]
        text += f"   {'✅' if s.get('has_greeting') else '❌'} Обращение\n"
        text += f"   {'✅' if s.get('has_thanks') else '❌'} Благодарность\n"
        text += f"   {'✅' if s.get('has_emotion') else '❌'} Эмоции\n"
        text += f"   {'✅' if s.get('has_future_contact') else '❌'} Надежда на ответ\n"
        text += f"   {'✅' if s.get('has_closing') else '❌'} Завершающая фраза\n"
        text += f"   {'✅' if s.get('has_signature') else '❌'} Подпись\n"
        text += f"   {'✅' if s.get('has_paragraphs') else '❌'} Абзацы\n"
    
    text += "\n"
    
    # К2
    text += f"📋 К2 — Организация текста: {result['k2_score']}/2\n\n"
    
    # К3
    text += f"📋 К3 — Лексико-грамматическое оформление: {result['k3_score']}/3\n"
    if details.get("grammar_errors"):
        text += "   ❌ Найдено проблем:\n"
        for error in details["grammar_errors"][:3]:
            text += f"      • {error}\n"
        if len(details["grammar_errors"]) > 3:
            text += f"      ... и ещё {len(details['grammar_errors']) - 3} проблем\n"
    text += "\n"
    
    # К4
    text += f"📋 К4 — Орфография и пунктуация: {result['k4_score']}/2\n"
    if details.get("spelling_errors"):
        text += "   ❌ Найдено проблем:\n"
        for error in details["spelling_errors"][:3]:
            text += f"      • {error}\n"
        if len(details["spelling_errors"]) > 3:
            text += f"      ... и ещё {len(details['spelling_errors']) - 3} проблем\n"
    text += "\n"
    
    # Итог
    text += f"⭐ Итоговый балл: {total}/10"
    
    return text

# ===== ОСНОВНЫЕ ОБРАБОТЧИКИ =====

async def start_letter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("authenticated"):
        await update.callback_query.answer("❌ Пожалуйста, войдите в аккаунт", show_alert=True)
        return
    
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
        
        default_path = os.path.join(base_dir, "oge_letter.json")
        with open(default_path, "w", encoding="utf-8") as f:
            json.dump(default_tasks, f, ensure_ascii=False, indent=2)
        print(f"✅ Создан дефолтный oge_letter.json")
        return default_tasks
        
    except Exception as e:
        print(f"❌ Ошибка загрузки oge_letter.json: {e}")
        return None

async def show_letter_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("letter")
    if not session:
        return
    
    current = session["current"]
    tasks = session["tasks"]
    
    if current >= session["total"]:
        await finish_letter_session(update, context)
        return
    
    task = tasks[current]
    
    text = "✉️ ЗАДАНИЕ 35. ПИСЬМО\n\n"
    text += f"Задание {current + 1} из {session['total']}\n\n"
    text += f"📧 От: {task['from']}\n"
    text += f"📧 Кому: {task['to']}\n"
    text += f"📌 Тема: {task['subject']}\n\n"
    text += f"{task['email_text']}\n\n"
    
    text += "❓ Ответь на вопросы:\n"
    for i, question in enumerate(task["questions"], 1):
        text += f"{i}. {question}\n"
    
    text += f"\n⏱️ Время: 30 минут\n"
    text += f"📝 Объём: 100-120 слов\n\n"
    text += "✏️ Напиши своё письмо в чат:"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data["current_letter_task"] = task
    context.user_data["awaiting_letter"] = True
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup
    )

async def handle_letter_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if not text:
        await update.message.reply_text("❌ Пожалуйста, напиши письмо.")
        return
    
    task = context.user_data.get("current_letter_task")
    if not task:
        await update.message.reply_text("❌ Задание не найдено. Начни заново.")
        return
    
    result = check_letter(text, task["questions"])
    result_text = format_letter_result(result)
    
    session = context.user_data.get("letter")
    if session:
        session["results"].append({
            "task": task,
            "text": text,
            "result": result
        })
    
    keyboard = [
        [InlineKeyboardButton("➡️ Следующее задание", callback_data="letter_next")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        result_text,
        reply_markup=reply_markup
    )
    
    context.user_data["awaiting_letter"] = False

async def letter_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("letter")
    if not session:
        await update.callback_query.answer("❌ Сессия не найдена", show_alert=True)
        return
    
    session["current"] += 1
    await show_letter_task(update, context)

async def finish_letter_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("letter")
    if not session:
        return
    
    results = session.get("results", [])
    total = session["total"]
    
    avg_score = 0
    if results:
        total_scores = []
        for r in results:
            if "total" in r["result"]:
                total_scores.append(r["result"]["total"])
        if total_scores:
            avg_score = sum(total_scores) / len(total_scores)
    
    text = "✉️ ВСЕ ПИСЬМА ВЫПОЛНЕНЫ!\n\n"
    text += f"📊 Выполнено: {len(results)} из {total}\n"
    text += f"⭐ Средний балл: {avg_score:.1f}/10\n\n"
    
    if avg_score >= 9:
        text += "🏆 Отличный результат! Ты готов к письму на ОГЭ!"
    elif avg_score >= 7:
        text += "📚 Хороший результат! Продолжай тренироваться."
    else:
        text += "💪 Нужно ещё немного практики. Попробуй ещё раз!"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти заново", callback_data="start_letter")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup
    )
    
    del context.user_data["letter"]
    context.user_data["awaiting_letter"] = False