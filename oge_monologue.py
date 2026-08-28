# ===== ОГЭ: МОНОЛОГ =====

import re
import requests
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ===== КОНСТАНТЫ =====

INTRO_MARKERS = [
    "i want to talk about",
    "i would like to talk about",
    "i'd like to talk about",
    "let me tell you about",
    "today i want to tell you about",
    "i'm going to talk about",
    "my topic is",
    "the topic i chose is",
    "first of all",
    "to begin with",
    "it is a well-known fact",
    "i think that",
    "in my opinion",
]

CONCLUSION_MARKERS = [
    "in conclusion",
    "to sum up",
    "finally",
    "that's all",
    "that's what i wanted to say",
    "in summary",
    "to conclude",
    "all in all",
    "so that's it",
    "that is all i wanted to say",
    "to finish",
]

# ===== ФУНКЦИИ =====

def load_monologue_tasks():
    """Загружает задания по монологу"""
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
                    return json.load(f)
        
        print(f"❌ oge_monologue.json не найден. Проверены пути: {json_paths}")
        return None
    except Exception as e:
        print(f"❌ Ошибка загрузки oge_monologue.json: {e}")
        return None

def count_sentences(text):
    """Считает количество предложений в тексте"""
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

def count_words(text):
    """Считает количество слов в тексте"""
    return len(text.split())

def check_grammar_with_languagetool(text):
    """Проверяет грамматику через LanguageTool API"""
    try:
        response = requests.post(
            "https://api.languagetool.org/v2/check",
            data={"text": text, "language": "en-US"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("matches", [])
    except:
        pass
    return []

def check_monologue(text, plan_keywords, min_sentences=10, min_words=100):
    """Основная функция проверки монолога"""
    text_lower = text.lower()
    
    # 1. Объём
    sentence_count = count_sentences(text)
    word_count = count_words(text)
    volume_ok = sentence_count >= min_sentences and word_count >= min_words
    
    # 2. Вступление
    intro = any(marker in text_lower for marker in INTRO_MARKERS)
    
    # 3. Заключение
    conclusion = any(marker in text_lower for marker in CONCLUSION_MARKERS)
    
    # 4. Раскрытие пунктов плана
    points_covered = 0
    points_details = []
    for i, kw_list in enumerate(plan_keywords):
        covered = any(kw in text_lower for kw in kw_list)
        if covered:
            points_covered += 1
            points_details.append(f"Аспект {i+1}: ✅ раскрыт")
        else:
            points_details.append(f"Аспект {i+1}: ❌ не раскрыт")
    
    # 5. К1 — Решение коммуникативной задачи
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
    
    # 6. К2 — Организация высказывания
    if intro and conclusion:
        k2_score = 2
        k2_comment = "✅ Есть вступление и заключение"
    elif intro or conclusion:
        k2_score = 1
        k2_comment = "⚠️ Отсутствует вступление ИЛИ заключение"
    else:
        k2_score = 0
        k2_comment = "❌ Нет вступления и заключения"
    
    # 7. К3 — Языковое оформление
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
    
    # 8. Итоговый балл
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
        "grammar_errors": grammar_errors,
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
    """Форматирует результат проверки монолога в красивое сообщение"""
    
    # Эмодзи для оценки
    if result["percentage"] == 100:
        emoji = "🏆"
    elif result["percentage"] >= 80:
        emoji = "🎉"
    elif result["percentage"] >= 60:
        emoji = "📚"
    else:
        emoji = "💪"
    
    # Прогресс-бар
    bar_length = 10
    filled = int(result["percentage"] / 100 * bar_length)
    bar = "🟩" * filled + "⬜" * (bar_length - filled)
    
    text = f"{emoji} *Результат монолога*\n\n"
    text += f"📊 {bar} {result['percentage']}%\n\n"
    
    # Объём
    text += f"📝 *Объём:* {result['sentence_count']} предложений, {result['word_count']} слов\n"
    if result["volume_ok"]:
        text += "✅ Объём соответствует норме (10-12 фраз, ~100 слов)\n\n"
    else:
        text += "⚠️ Объём меньше рекомендуемого\n\n"
    
    # К1
    text += f"📋 *К1 — Решение коммуникативной задачи:* {result['k1_score']}/3\n"
    text += f"{result['k1_comment']}\n"
    for detail in result["points_details"]:
        text += f"  {detail}\n"
    text += "\n"
    
    # К2
    text += f"📋 *К2 — Организация высказывания:* {result['k2_score']}/2\n"
    text += f"{result['k2_comment']}\n\n"
    
    # К3
    text += f"📋 *К3 — Языковое оформление:* {result['k3_score']}/2\n"
    text += f"{result['k3_comment']}\n\n"
    
    # Итог
    text += f"⭐ *Итог: {result['total_score']}/{result['max_score']}*"
    
    # Если есть ошибки, показываем их
    if result["error_count"] > 0:
        text += "\n\n*❌ Найденные ошибки:*\n"
        for i, error in enumerate(result["grammar_errors"][:5], 1):
            message = error.get("message", "")
            replacements = error.get("replacements", [])
            if replacements:
                suggestion = replacements[0].get("value", "")
                text += f"{i}. {message} → *{suggestion}*\n"
            else:
                text += f"{i}. {message}\n"
        if result["error_count"] > 5:
            text += f"\n... и ещё {result['error_count'] - 5} ошибок"
    
    return text

# ===== ОСНОВНЫЕ ОБРАБОТЧИКИ =====

async def start_monologue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает задание — монолог"""
    data = load_monologue_tasks()
    if not data:
        await update.callback_query.answer("❌ Задания не загружены", show_alert=True)
        return
    
    tasks = data.get("tasks", [])
    if not tasks:
        await update.callback_query.answer("❌ Нет заданий", show_alert=True)
        return
    
    # Сохраняем все задания в сессию
    context.user_data["monologue"] = {
        "tasks": tasks,
        "current": 0,
        "total": len(tasks)
    }
    
    await show_monologue_task(update, context)

async def show_monologue_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текущее задание по монологу"""
    session = context.user_data.get("monologue")
    if not session:
        return
    
    current = session["current"]
    tasks = session["tasks"]
    
    if current >= session["total"]:
        await finish_monologue_session(update, context)
        return
    
    task = tasks[current]
    
    # Формируем текст задания
    text = f"🎤 *Монолог*\n\n"
    text += f"Задание {current + 1} из {session['total']}\n\n"
    text += f"*{task.get('instruction', '')}*\n\n"
    text += "📋 *План:*\n"
    for i, aspect in enumerate(task.get("plan", []), 1):
        text += f"{i}. {aspect}\n"
    
    text += f"\n⏱️ *Время на подготовку:* 1.5 минуты\n"
    text += f"⏱️ *Время ответа:* до 2 минут (10-12 фраз)\n\n"
    text += "✏️ *Напиши свой монолог в чат:*"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    # Сохраняем текущее задание в контексте для проверки
    context.user_data["current_monologue_task"] = task
    context.user_data["awaiting_monologue"] = True

async def handle_monologue_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ на монолог"""
    text = update.message.text.strip()
    
    if not text:
        await update.message.reply_text("❌ Пожалуйста, напиши свой монолог.")
        return
    
    task = context.user_data.get("current_monologue_task")
    if not task:
        await update.message.reply_text("❌ Задание не найдено. Начни заново.")
        return
    
    # Извлекаем ключевые слова для проверки
    plan_keywords = []
    for aspect in task.get("plan", []):
        # Генерируем ключевые слова из аспекта
        keywords = aspect.lower().replace("?", "").replace(",", "").split()
        plan_keywords.append(keywords)
    
    # Проверяем монолог
    result = check_monologue(
        text,
        plan_keywords,
        min_sentences=10,
        min_words=100
    )
    
    # Форматируем результат
    result_text = format_monologue_result(result)
    
    # Сохраняем результат в сессию
    session = context.user_data.get("monologue")
    if session:
        if "results" not in session:
            session["results"] = []
        session["results"].append({
            "task": task,
            "text": text,
            "result": result
        })
    
    # Отправляем результат
    keyboard = [
        [InlineKeyboardButton("➡️ Следующее задание", callback_data="monologue_next")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    context.user_data["awaiting_monologue"] = False

async def monologue_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переход к следующему заданию"""
    session = context.user_data.get("monologue")
    if not session:
        await update.callback_query.answer("❌ Сессия не найдена", show_alert=True)
        return
    
    session["current"] += 1
    await show_monologue_task(update, context)

async def finish_monologue_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершает сессию монологов"""
    session = context.user_data.get("monologue")
    if not session:
        return
    
    results = session.get("results", [])
    total = session["total"]
    
    # Считаем средний балл
    avg_score = 0
    if results:
        avg_score = sum(r["result"]["total_score"] for r in results) / len(results)
    
    text = "🎤 *Все монологи выполнены!*\n\n"
    text += f"📊 *Выполнено:* {len(results)} из {total}\n"
    text += f"⭐ *Средний балл:* {avg_score:.1f}/7\n\n"
    
    if avg_score >= 6:
        text += "🏆 *Отличный результат! Ты готов к монологу на ОГЭ!*"
    elif avg_score >= 4:
        text += "📚 *Хороший результат! Продолжай тренироваться.*"
    else:
        text += "💪 *Нужно ещё немного практики. Попробуй ещё раз!*"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти заново", callback_data="start_monologue")],
        [InlineKeyboardButton("🔙 Назад в ОГЭ", callback_data="oge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    del context.user_data["monologue"]
    context.user_data["awaiting_monologue"] = False