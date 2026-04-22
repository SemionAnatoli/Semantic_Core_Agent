import anthropic
from loguru import logger
from agents.state import PipelineState
from config.settings import ANTHROPIC_API_KEY, LLM_MODEL
from datetime import datetime


PAGE_STRUCTURES = {
    "commercial": [
        "Фильтры: характеристики, цена, материал",
        "Карточки товаров (сетка)",
        "Блок 'Популярные' / 'Новинки'",
        "SEO-текст (400–600 слов)",
        "FAQ: 4–5 вопросов о товаре",
        "Блок отзывов",
    ],
    "transactional": [
        "Заголовок с CTA (Заказать / Купить)",
        "Форма заказа / кнопка в корзину",
        "Условия доставки и оплаты",
        "Гарантии",
        "Отзывы покупателей",
    ],
    "informational": [
        "Введение (проблема читателя)",
        "Основной контент (1500–2500 слов)",
        "Подзаголовки H2/H3",
        "Список / таблица сравнений",
        "Вывод + CTA (перейти в каталог)",
    ],
    "comparison": [
        "Таблица сравнения вариантов",
        "Плюсы и минусы каждого",
        "Для кого подходит каждый вариант",
        "Вывод + рекомендация",
        "CTA в каталог",
    ],
    "local": [
        "H1 с гео (Купить X в Москве)",
        "Преимущества доставки в регион",
        "Карта / адрес",
        "Каталог товаров",
        "Отзывы местных покупателей",
    ],
    "problem_based": [
        "Описание проблемы",
        "Критерии выбора решения",
        "Подборка подходящих товаров",
        "Экспертный блок",
        "FAQ по теме",
    ],
}


def _rule_based_brief(cluster: dict, business: str, geo: str) -> dict:
    name      = cluster["name"]
    main_kw   = cluster["main_keyword"]
    intent    = cluster.get("intent", "commercial")
    url       = cluster.get("recommended_url", "")
    keywords  = cluster.get("keywords", [])[:10]
    structure = PAGE_STRUCTURES.get(intent, PAGE_STRUCTURES["commercial"])
    year      = datetime.now().year

    if intent in ("commercial", "transactional"):
        title = f"{name} — купить в {geo} | {business.split(',')[0].strip().title()}"
    elif intent == "local":
        title = f"{name} в {geo} — цены, доставка, каталог"
    elif intent == "informational":
        title = f"{name} — подробный гайд {year}"
    else:
        title = f"{name} — {business.split(',')[0].strip()}"

    if intent in ("commercial", "transactional"):
        desc = (f"Купить {main_kw.lower()} в {geo}. "
                f"Большой выбор, доставка, выгодные цены. "
                f"Закажите онлайн на сайте {business.split(',')[0].strip()}.")
    else:
        desc = (f"{name}. "
                f"Полезная информация, советы экспертов. "
                f"Читайте на сайте {business.split(',')[0].strip()}.")

    lsi = list(set(keywords) - {main_kw})[:6]

    return {
        "cluster":            name,
        "url":                url,
        "intent":             intent,
        "title":              title[:65],
        "h1":                 name,
        "description":        desc[:160],
        "structure":          structure,
        "main_keyword":       main_kw,
        "secondary_keywords": keywords[:5],
        "lsi_words":          lsi,
        "word_count":         "400–600" if intent == "commercial" else "1500–2500",
        "generated_by":       "rules",
    }


def _llm_brief(cluster: dict, business: str, geo: str) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None

    client   = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    name     = cluster["name"]
    main_kw  = cluster["main_keyword"]
    intent   = cluster.get("intent", "commercial")
    keywords = cluster.get("keywords", [])[:10]

    prompt = f"""Ты SEO-копирайтер. Бизнес: {business}. Гео: {geo}.

Создай ТЗ на страницу для кластера.

Кластер: {name}
Главный ключ: {main_kw}
Все запросы: {', '.join(keywords)}
Интент: {intent}

Ответь строго в JSON:
{{
  "title": "Title до 65 символов",
  "h1": "Заголовок H1",
  "description": "Meta Description до 160 символов",
  "structure": ["Блок 1", "Блок 2", "Блок 3", "Блок 4", "Блок 5"],
  "main_keyword": "главный ключ для Title и H1",
  "secondary_keywords": ["ключ 1", "ключ 2", "ключ 3"],
  "lsi_words": ["lsi 1", "lsi 2", "lsi 3", "lsi 4"],
  "word_count": "рекомендуемый объём текста",
  "content_tips": "2-3 конкретных совета по контенту"
}}
Только JSON."""

    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        import json
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        data["cluster"]      = name
        data["url"]          = cluster.get("recommended_url", "")
        data["intent"]       = intent
        data["generated_by"] = "llm"
        return data
    except Exception as e:
        logger.error(f"llm brief error for '{name}': {e}")
        return None


def brief_agent(state: PipelineState) -> PipelineState:
    logger.info("brief agent started")

    clusters = state.get("clusters", [])
    business = state.get("business_description", "")
    geo      = state.get("geo", "Москва")

    briefs     = []
    llm_count  = 0
    rule_count = 0

    for cluster in clusters:
        if cluster.get("action") == "skip":
            continue

        score = cluster.get("priority_score", 0)

        if score >= 60 and ANTHROPIC_API_KEY:
            brief = _llm_brief(cluster, business, geo)
            if brief:
                briefs.append(brief)
                llm_count += 1
                continue

        brief = _rule_based_brief(cluster, business, geo)
        briefs.append(brief)
        rule_count += 1

    state["briefs"] = briefs

    logger.info(f"briefs generated: {len(briefs)} (llm={llm_count}, rules={rule_count})")

    if briefs:
        b = briefs[0]
        logger.info(f"example brief — {b['cluster']}: title={b['title']}")

    state["logs"].append(
        f"brief: {len(briefs)} briefs generated (llm={llm_count}, rules={rule_count})"
    )
    return state
