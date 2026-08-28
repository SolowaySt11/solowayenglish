# ===== ОГЭ: МОНОЛОГ =====

import re
import requests
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ===== КОНСТАНТЫ =====

INTRO_MARKERS = [
    "i want to talk about", "i would like to talk about", "i'd like to talk about",
    "let me tell you about", "today i want to tell you about", "i'm going to talk about",
    "my topic is", "the topic i chose is", "first of all", "to begin with",
    "it is a well-known fact", "i think that", "in my opinion",
]

CONCLUSION_MARKERS = [
    "in conclusion", "to sum up", "finally", "that's all", "that's what i wanted to say",
    "in summary", "to conclude", "all in all", "so that's it", "that is all i wanted to say",
    "to finish",
]

# ===== ФУНКЦИИ =====

def load_monologue_tasks():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_paths = [
            os.path.join(base_dir, "oge_monologue.json"),
            os.path.join("/app", "oge_monologue.json"),
            os.path.join(os.getcwd(), "oge_monologue.json")
        ]
        
        for path in json_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"✅ Загружен oge_monologue.json: {len(data.get('tasks', []))} заданий")
                    return data
        
        print(f"❌ oge_monologue.json не найден")
        return None
    except Exception as e:
        print(f"❌ Ошибка загрузки oge_monologue.json: {e}")
        return None

def count_sentences(text):
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

def count_words(text):
    return len(text.split())

def check_grammar_with_languagetool(text):
    try:
        response = requests.post(
            "https://api.languagetool.org/v2/check",
            data={"text": text, "language": "en-US"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("matches", [])
    except Exception as e:
        print(f"⚠️ Ошибка LanguageTool: {e}")
    return []

def check_monologue(text, plan_keywords, min_sentences=10, min_words=100):
    text_lower = text.lower()
    
    sentence_count = count_sentences(text)
    word_count = count_words(text)
    volume_ok = sentence_count >= min_sentences and word_count >= min_words
    
    intro = any(marker in text_lower for marker in INTRO_MARKERS)
    conclusion = any(marker in text_lower for marker in CONCLUSION_MARKERS)
    
    points_covered = 0
    points_details = []
    for i, kw_list in enumerate(plan_keywords):
        covered = any(kw in text_lower for kw in kw_list)
        if covered:
            points_covered += 1
            points_details.append(f"Аспект {i+1}: ✅ раскрыт")
        else:
            points_details.append(f"Аспект {i+1}: ❌ не раскрыт")
    
    # К1
    if points_covered == len(plan_keywords) and sentence_count >= 10 and word_count >= 100:
        k1_score = 3
        k1_comment = "✅ Все аспекты раскрыты, объём 10-12 фраз"
    elif points_covered >= len(plan_keywords) - 1 and sentence_count >= 8 and word_count >= 80:
        k1_score = 2
        k1_comment = "⚠️ Тема раскрыта не в полном объёме"
    elif points_covered >= len(plan_keywords) - 2 and sentence_count >= 6 and word_count >= 60:
        k1_score = 1
        k1_comment = "⚠️ Тема раскрыта в ограниченном объёме"
    else:
        k1_score = 0
        k1_comment = "❌ Цель общения не достигнута"
    
    # К2
    if intro and conclusion:
        k2_score = 2
        k2_comment = "✅ Есть вступление и заключение"
    elif intro or conclusion:
        k2_score = 1
        k2_comment = "⚠️ Отсутствует вступление ИЛИ заключение"
    else:
        k2_score = 0
        k2_comment = "❌ Нет вступления и заключения"
    
    # К3
    grammar_errors = check_grammar_with_languagetool(text)
    error_count = len(grammar_errors)
    
    if error_count <= 4:
        k3_score = 2
        k3_comment = f"✅ {error_count} ошибок — хороший уровень"
    elif error_count <= 5:
        k3_score = 1
        k3_comment = f"⚠️ {error_count} ошибок — средний уровень"
    else:
        k3_score = 0
        k3_comment = f"❌ {error_count} ошибок — много ошибок"
    
    total_score = k1_score + k2_score + k3_score
    max_score = 7
    
    return {
        "sentence_count": sentence_count,
        "word_count": word_count,
        "volume_ok": volume_ok,
        "intro": intro,
        "conclusion": conclusion,
        "points_covered": points_covered,
        "total_points": len(plan_keywords),
        "points_details": points_details,
        "error_count": error_count,
        "grammar_errors": grammar_errors[:5],
        "k1_score": k1_score,
        "k1_comment": k1_comment,
        "k2_score": k2_score,
        "k2_comment": k2_comment,
        "k3_score": k3_score,
        "k3_comment": k3_comment,
        "total_score": total_score,
        "max_score": max_score,
        "percentage": int(total_score / max_score * 100)
    }

def format_monologue_result(result):
    if result["percentage"] == 100:
        emoji = "🏆"
    elif result["percentage"] >= 80:
        emoji = "🎉"
    elif result["percentage"] >= 60:
        emoji = "📚"
    else:
        emoji = "💪"
    
    bar = "█" * (result["percentage"] // 10) + "░" * (10 - result["percentage"] // 10)
    
    text = f"{emoji} РЕЗУЛЬТАТ МОНОЛОГА\n\n"
    text += f"📊 {bar} {result['percentage']}%\n\n"
    text += f"📝 Объём: {result['sentence_count']} предложений, {result['word_count']} слов\n"
    
    if result["volume_ok"]:
        text += "✅ Объём соответствует норме\n\n"
    else:
        text += "⚠️ Объём меньше рекомендуемого\n\n"
    
    text += f"📋 К1 — Решение коммуникативной задачи: {result['k1_score']}/3\n"
    text += f"{result['k1_comment']}\n"
    for detail in result["points_details"]:
        text += f"  {detail}\n"
    text += "\n"
    
    text += f"📋 К2 — Организация высказывания: {result['k2_score']}/2\n"
    text += f"{result['k2_comment']}\n\n"
    
    text += f"📋 К3 — Языковое оформление: {result['k3_score']}/2\n"
    text += f"{result['k3_comment']}\n\n"
    
    text += f"⭐ Итог: {result['total_score']}/{result['max_score']}"
    
    if result["error_count"] > 0 and result["grammar_errors"]:
        text += "\n\n❌ Найденные ошибки:\n"
        for i, error in enumerate(result["grammar_errors"], 1):
            message = error.get("message", "")
            replacements = error.get("replacements", [])
            if replacements:
                suggestion = replacements[0].get("value", "")
                text += f"{i}. {message} → {suggestion}\n"
            else:
                text += f"{i}. {message}\n"
    
    return text

# ===== ОСНОВНЫЕ ОБРАБОТЧИКИ =====

async def start_monologue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("authenticated"):
        await update.callback_query.answer("❌ Пожалуйста, войдите в аккаунт", show_alert=True)
        return
    
    data = load_monologue_tasks()
    if not data:
        await update.callback_query.answer("❌ Задания не загружены", show_alert=True)
        return
    
    tasks = data.get("tasks", [])
    if not tasks:
        await update.callback_query.answer("❌ Нет заданий", show_alert=True)
        return
    
    # Показываем список заданий для выбора
    keyboard = []
    for i, task in enumerate(tasks):
        task_id = task.get("id", f"monologue_{i+1}")
        button_text = f"🎤 Вариант {i+1}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"monologue_select_{i}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎤 ВЫБЕРИ ВАРИАНТ МОНОЛОГА\n\n"
        "Выбери один из вариантов для тренировки:",
        reply_markup=reply_markup
    )

async def show_monologue_task(update: Update, context: ContextTypes.DEFAULT_TYPE, task_index=0):
    session = context.user_data.get("monologue")
    if not session:
        return
    
    tasks = session["tasks"]
    if task_index >= len(tasks):
        await finish_monologue_session(update, context)
        return
    
    task = tasks[task_index]
    session["current"] = task_index
    
    text = f"🎤 МОНОЛОГ\n\n"
    text += f"Вариант {task_index + 1} из {len(tasks)}\n\n"
    text += f"{task.get('instruction', '')}\n\n"
    text += "📋 План:\n"
    for i, aspect in enumerate(task.get("plan", []), 1):
        text += f"{i}. {aspect}\n"
    
    text += f"\n⏱️ Время на подготовку: 1.5 минуты\n"
    text += f"⏱️ Время ответа: до 2 минут (10-12 фраз)\n\n"
    text += "✏️ Напиши свой монолог в чат:"
    
    keyboard = [
        [InlineKeyboardButton("📋 К списку вариантов", callback_data="monologue_list")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data["current_monologue_task"] = task
    context.user_data["awaiting_monologue"] = True
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup
    )

async def handle_monologue_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if not text:
        await update.message.reply_text("❌ Пожалуйста, напиши свой монолог.")
        return
    
    task = context.user_data.get("current_monologue_task")
    if not task:
        await update.message.reply_text("❌ Задание не найдено. Начни заново.")
        return
    
    plan_keywords = []
    for aspect in task.get("plan", []):
        keywords = aspect.lower().replace("?", "").replace(",", "").split()
        plan_keywords.append(keywords)
    
    result = check_monologue(text, plan_keywords, min_sentences=10, min_words=100)
    result_text = format_monologue_result(result)
    
    session = context.user_data.get("monologue")
    if session:
        session["results"].append({
            "task": task,
            "text": text,
            "result": result
        })
    
    keyboard = [
        [InlineKeyboardButton("📋 К списку вариантов", callback_data="monologue_list")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        result_text,
        reply_markup=reply_markup
    )
    
    context.user_data["awaiting_monologue"] = False

async def monologue_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список вариантов монолога"""
    session = context.user_data.get("monologue")
    if not session:
        await update.callback_query.answer("❌ Сессия не найдена", show_alert=True)
        return
    
    tasks = session["tasks"]
    keyboard = []
    for i, task in enumerate(tasks):
        # Проверяем, выполнен ли этот вариант
        is_done = False
        for result in session.get("results", []):
            if result["task"].get("id") == task.get("id"):
                is_done = True
                break
        
        status = "✅" if is_done else "⬜"
        button_text = f"{status} Вариант {i+1}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"monologue_select_{i}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎤 ВЫБЕРИ ВАРИАНТ МОНОЛОГА\n\n"
        "✅ - уже выполнено\n"
        "⬜ - ещё не выполнено\n\n"
        "Выбери вариант для тренировки:",
        reply_markup=reply_markup
    )

async def monologue_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переход к следующему заданию (устарело, используем список)"""
    await monologue_list(update, context)

async def finish_monologue_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("monologue")
    if not session:
        return
    
    results = session.get("results", [])
    total = len(session["tasks"])
    
    avg_score = 0
    if results:
        avg_score = sum(r["result"]["total_score"] for r in results) / len(results)
    
    text = "🎤 ВСЕ МОНОЛОГИ ВЫПОЛНЕНЫ!\n\n"
    text += f"📊 Выполнено: {len(results)} из {total}\n"
    text += f"⭐ Средний балл: {avg_score:.1f}/7\n\n"
    
    if avg_score >= 6:
        text += "🏆 Отличный результат! Ты готов к монологу на ОГЭ!"
    elif avg_score >= 4:
        text += "📚 Хороший результат! Продолжай тренироваться."
    else:
        text += "💪 Нужно ещё немного практики. Попробуй ещё раз!"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти заново", callback_data="start_monologue")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup
    )
    
    del context.user_data["monologue"]
    context.user_data["awaiting_monologue"] = False