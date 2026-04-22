"""
Telegram-бот — управление агентом семантического ядра.

Команды:
  /start    — приветствие и инструкция
  /analyze  — запустить анализ сайта
  /status   — статус текущего анализа
  /result   — получить последний отчёт
  /help     — справка

Сценарий:
  1. Пользователь пишет /analyze
  2. Бот задаёт вопросы: сайт, ключи, конкуренты
  3. Запускает пайплайн
  4. Отправляет сводку + CSV файл
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, ConversationHandler, filters
)
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID
from loguru import logger

logging.basicConfig(level=logging.WARNING)

# ── Состояния диалога ────────────────────────────────────────
ASK_SITE, ASK_BUSINESS, ASK_KEYWORDS, ASK_GEO, ASK_COMPETITORS, CONFIRM = range(6)

# Хранилище сессий пользователей
user_sessions: dict[int, dict] = {}


# ============================================================
# ХЕЛПЕРЫ
# ============================================================

def _is_admin(user_id: int) -> bool:
    if not TELEGRAM_ADMIN_ID:
        return True  # Если не задан — доступ для всех
    return str(user_id) == str(TELEGRAM_ADMIN_ID)


def _format_clusters_summary(clusters: list[dict]) -> str:
    """Краткая сводка кластеров для Telegram."""
    high   = [c for c in clusters if c.get("priority_score", 0) >= 70]
    medium = [c for c in clusters if 40 <= c.get("priority_score", 0) < 70]
    low    = [c for c in clusters if c.get("priority_score", 0) < 40]
    create = [c for c in clusters if c.get("action") == "create_page"]
    update = [c for c in clusters if c.get("action") == "update_page"]
    blog   = [c for c in clusters if c.get("action") == "create_blog"]

    top5 = sorted(clusters, key=lambda c: c.get("priority_score", 0), reverse=True)[:5]
    top5_text = ""
    action_icons = {
        "create_page": "🆕", "update_page": "✏️",
        "create_blog": "📝", "add_faq": "❓", "skip": "⏭️"
    }
    for c in top5:
        icon = action_icons.get(c.get("action","skip"), "•")
        score = c.get("priority_score", 0)
        top5_text += f"\n  {icon} *{c['name']}* — {score} баллов"
        top5_text += f"\n      `{c.get('recommended_url','—')}`"

    return (
        f"📊 *Результат анализа готов!*\n\n"
        f"🔢 Всего кластеров: *{len(clusters)}*\n"
        f"🔴 Высокий приоритет: *{len(high)}*\n"
        f"🟡 Средний приоритет: *{len(medium)}*\n"
        f"⚫ Низкий приоритет: *{len(low)}*\n\n"
        f"📋 *Карта действий:*\n"
        f"  🆕 Создать страниц: *{len(create)}*\n"
        f"  ✏️ Обновить страниц: *{len(update)}*\n"
        f"  📝 Написать статей: *{len(blog)}*\n\n"
        f"🔥 *Топ-5 приоритетов:*{top5_text}"
    )


# ============================================================
# КОМАНДЫ
# ============================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие."""
    user = update.effective_user
    text = (
        f"👋 Привет, *{user.first_name}*!\n\n"
        f"Я агент по расширению семантического ядра.\n\n"
        f"*Что я умею:*\n"
        f"• Собрать семантику сайта\n"
        f"• Расширить ядро через модификаторы и LLM\n"
        f"• Очистить мусор и определить интент\n"
        f"• Сгруппировать запросы в кластеры\n"
        f"• Показать что создать, что обновить\n"
        f"• Сгенерировать ТЗ для копирайтера\n"
        f"• Выявить каннибализацию\n\n"
        f"*Команды:*\n"
        f"/analyze — запустить анализ\n"
        f"/result — последний отчёт\n"
        f"/help — справка"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Справка*\n\n"
        "/analyze — начать новый анализ\n"
        "/result  — получить последний отчёт\n"
        "/start   — главное меню\n\n"
        "После /analyze бот задаст несколько вопросов и запустит анализ.",
        parse_mode="Markdown"
    )


# ============================================================
# ДИАЛОГ АНАЛИЗА
# ============================================================

async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога — запрашиваем сайт."""
    user_id = update.effective_user.id
    user_sessions[user_id] = {}

    await update.message.reply_text(
        "🚀 *Запускаем анализ!*\n\n"
        "Шаг 1/5 — Введите URL сайта:\n"
        "_(например: mebel-dom.ru)_",
        parse_mode="Markdown"
    )
    return ASK_SITE


async def got_site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id]["site_url"] = update.message.text.strip()

    await update.message.reply_text(
        "✅ Сайт сохранён.\n\n"
        "Шаг 2/5 — Опишите бизнес одной строкой:\n"
        "_(например: интернет-магазин мебели, продаём диваны и кресла)_",
        parse_mode="Markdown"
    )
    return ASK_BUSINESS


async def got_business(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id]["business_description"] = update.message.text.strip()

    await update.message.reply_text(
        "✅ Бизнес сохранён.\n\n"
        "Шаг 3/5 — Введите стартовые ключевые слова через запятую:\n"
        "_(например: купить диван, угловой диван, диван кровать)_",
        parse_mode="Markdown"
    )
    return ASK_KEYWORDS


async def got_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    raw = update.message.text.strip()
    keywords = [k.strip() for k in raw.split(",") if k.strip()]
    user_sessions[user_id]["seed_keywords"] = keywords

    await update.message.reply_text(
        f"✅ Ключей: {len(keywords)} шт.\n\n"
        "Шаг 4/5 — Укажите город/регион:\n"
        "_(например: Москва)_",
        parse_mode="Markdown"
    )
    return ASK_GEO


async def got_geo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id]["geo"] = update.message.text.strip()

    await update.message.reply_text(
        "✅ Гео сохранено.\n\n"
        "Шаг 5/5 — Введите URL конкурентов через запятую\n"
        "_(или напишите 'нет' чтобы пропустить)_",
        parse_mode="Markdown"
    )
    return ASK_COMPETITORS


async def got_competitors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    raw = update.message.text.strip()

    if raw.lower() in ("нет", "no", "-", "skip"):
        competitors = []
    else:
        competitors = [c.strip() for c in raw.split(",") if c.strip()]

    user_sessions[user_id]["competitors"] = competitors
    session = user_sessions[user_id]

    # Показываем сводку перед запуском
    kw_list = ", ".join(session.get("seed_keywords", [])[:3])
    comp_list = ", ".join(competitors[:3]) if competitors else "не указаны"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Запустить анализ", callback_data="run_analysis")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")],
    ])

    await update.message.reply_text(
        f"📋 *Проверьте данные:*\n\n"
        f"🌐 Сайт: `{session.get('site_url','—')}`\n"
        f"💼 Бизнес: {session.get('business_description','—')}\n"
        f"🔑 Ключи: {kw_list}...\n"
        f"📍 Гео: {session.get('geo','—')}\n"
        f"🏢 Конкуренты: {comp_list}\n\n"
        f"Всё верно?",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return CONFIRM


async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "cancel":
        await query.edit_message_text("❌ Анализ отменён.")
        return ConversationHandler.END

    # Запускаем анализ
    await query.edit_message_text(
        "⏳ *Анализ запущен...*\n\n"
        "Это займёт 1–3 минуты.\n"
        "Я пришлю результат когда готово.",
        parse_mode="Markdown"
    )

    session = user_sessions.get(user_id, {})
    session.setdefault("language", "ru")
    session.setdefault("target_pages", [])
    session.setdefault("commercial_priority", {})

    # Запускаем пайплайн в фоне
    asyncio.create_task(
        _run_pipeline_and_notify(context, user_id, session)
    )
    return ConversationHandler.END


async def _run_pipeline_and_notify(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    session: dict
):
    """Запускает пайплайн и отправляет результат пользователю."""
    try:
        # Импорт здесь чтобы не блокировать старт бота
        from test_pipeline import run_test
        import sys, io

        # Подменяем stdout чтобы не ломать бота
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        # Запускаем полный тест
        state = {
            **session,
            "raw_keywords": [], "cleaned_keywords": [], "classified_keywords": [],
            "clusters": [], "gap_analysis": [], "output_table": [],
            "errors": [], "logs": [], "current_step": "init",
        }

        from agents.research_agent      import research_agent
        from agents.expansion_agent     import expansion_agent
        from agents.cleaning_agent      import cleaning_agent
        from agents.intent_agent        import intent_agent
        from agents.prioritization_agent import prioritization_agent
        from agents.mapping_agent       import mapping_agent
        from agents.cannibalization_agent import cannibalization_agent
        from agents.brief_agent         import brief_agent
        from utils.html_report          import generate_html_report
        from test_pipeline              import _simple_clustering

        state = research_agent(state)
        state = expansion_agent(state)
        state = cleaning_agent(state)
        state = intent_agent(state)
        state = _simple_clustering(state)
        state = prioritization_agent(state)
        state = mapping_agent(state)
        state = cannibalization_agent(state)
        state = brief_agent(state)

        sys.stdout = old_stdout

        # Генерируем HTML-отчёт
        html_path = generate_html_report(state)

        # Текстовая сводка
        summary = _format_clusters_summary(state["clusters"])

        # Каннибализация
        issues = state.get("cannibalization_issues", [])
        if issues:
            summary += f"\n\n⚠️ *Найдено {len(issues)} проблем каннибализации*"
            critical = [i for i in issues if i.get("severity") == "critical"]
            if critical:
                summary += f"\n🚨 Критических: {len(critical)}"

        await context.bot.send_message(
            chat_id=user_id,
            text=summary,
            parse_mode="Markdown"
        )

        # Отправляем HTML файл
        with open(html_path, "rb") as f:
            await context.bot.send_document(
                chat_id=user_id,
                document=f,
                filename=f"semantic_core_{session.get('site_url','report')}.html",
                caption="📊 Полный отчёт — откройте в браузере"
            )

        # Если есть ТЗ — отправляем первые 3
        briefs = state.get("briefs", [])
        if briefs:
            brief_text = "📝 *Пример ТЗ для копирайтера:*\n\n"
            for b in briefs[:2]:
                brief_text += (
                    f"*{b['cluster']}*\n"
                    f"Title: `{b['title']}`\n"
                    f"H1: `{b['h1']}`\n"
                    f"Desc: _{b['description']}_\n"
                    f"Структура: {', '.join(b['structure'][:3])}...\n\n"
                )
            await context.bot.send_message(
                chat_id=user_id,
                text=brief_text,
                parse_mode="Markdown"
            )

    except Exception as e:
        sys.stdout = old_stdout
        logger.error(f"Ошибка пайплайна для {user_id}: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ Ошибка при анализе: {e}\n\nПопробуйте снова /analyze"
        )


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено. Напишите /analyze чтобы начать заново.")
    return ConversationHandler.END


# ============================================================
# ЗАПУСК БОТА
# ============================================================

def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не задан в .env")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Диалог анализа
    conv = ConversationHandler(
        entry_points=[CommandHandler("analyze", cmd_analyze)],
        states={
            ASK_SITE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, got_site)],
            ASK_BUSINESS:    [MessageHandler(filters.TEXT & ~filters.COMMAND, got_business)],
            ASK_KEYWORDS:    [MessageHandler(filters.TEXT & ~filters.COMMAND, got_keywords)],
            ASK_GEO:         [MessageHandler(filters.TEXT & ~filters.COMMAND, got_geo)],
            ASK_COMPETITORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_competitors)],
            CONFIRM:         [CallbackQueryHandler(confirm_callback)],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
    )

    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("help",   cmd_help))
    app.add_handler(conv)

    print("🤖 Telegram-бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()
