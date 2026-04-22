import json
import anthropic
from loguru import logger
from agents.state import PipelineState, Keyword
from config.settings import ANTHROPIC_API_KEY, LLM_MODEL

INTENT_RULES = {
    "купить":        "commercial",
    "цена":          "commercial",
    "стоимость":     "commercial",
    "заказать":      "transactional",
    "доставка":      "transactional",
    "как выбрать":   "informational",
    "что такое":     "informational",
    "почему":        "informational",
    "какой лучше":   "comparison",
    "или ":          "comparison",
    "что лучше":     "comparison",
    "в москве":      "local",
    "в спб":         "local",
    "рядом":         "local",
    "не скрипит":    "problem_based",
    "легко чистить": "problem_based",
    ".ru ":          "navigational",
    ".com ":         "navigational",
}


def _rule_based_intent(text: str) -> str | None:
    text_lower = text.lower()
    for pattern, intent in INTENT_RULES.items():
        if pattern in text_lower:
            return intent
    return None


def _llm_classify_batch(keywords: list[str], business_description: str) -> list[dict]:
    if not ANTHROPIC_API_KEY:
        logger.warning("no API key, skipping LLM intent classification")
        return []

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    keywords_str = "\n".join(f"{i+1}. {kw}" for i, kw in enumerate(keywords))

    prompt = f"""Ты SEO-аналитик. Бизнес: {business_description}.

Определи интент для каждого запроса. Используй только эти типы:
- commercial: хотят купить/сравнить товары (купить, цена, каталог)
- transactional: готовы совершить действие (заказать, оформить, добавить в корзину)
- informational: хотят узнать информацию (как выбрать, что такое, гайды)
- comparison: сравнивают варианты (или, vs, что лучше, отличие)
- navigational: ищут конкретный сайт/бренд (divan.ru, IKEA диваны)
- local: привязаны к гео (в Москве, рядом, с доставкой в СПб)
- problem_based: описывают проблему (не скрипит, легко чистится, занимает мало места)

Запросы:
{keywords_str}

Ответь строго в JSON формате (массив):
[
  {{"keyword": "...", "intent": "...", "confidence": 0.0-1.0}},
  ...
]
Только JSON, без пояснений."""

    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        logger.error(f"llm classification error: {e}")
        return []


BATCH_SIZE = 20


def intent_agent(state: PipelineState) -> PipelineState:
    logger.info("intent agent started")
    state["current_step"] = "intent"

    keywords = state["cleaned_keywords"]
    business = state["business_description"]

    needs_llm = []
    rule_count = 0

    for kw in keywords:
        intent = _rule_based_intent(kw["text"])
        if intent:
            kw["intent"] = intent
            kw["intent_confidence"] = 0.75
            rule_count += 1
        else:
            needs_llm.append(kw)

    logger.info(f"rules: {rule_count}, need llm: {len(needs_llm)}")

    llm_count = 0
    for i in range(0, len(needs_llm), BATCH_SIZE):
        batch = needs_llm[i:i + BATCH_SIZE]
        batch_texts = [kw["text"] for kw in batch]

        results = _llm_classify_batch(batch_texts, business)
        results_map = {r["keyword"]: r for r in results}

        for kw in batch:
            if kw["text"] in results_map:
                kw["intent"] = results_map[kw["text"]]["intent"]
                kw["intent_confidence"] = results_map[kw["text"]]["confidence"]
                llm_count += 1
            else:
                kw["intent"] = "commercial"
                kw["intent_confidence"] = 0.5

        logger.info(f"batch {i//BATCH_SIZE + 1}: {len(batch)} keywords processed")

    state["classified_keywords"] = keywords

    intent_stats: dict[str, int] = {}
    for kw in keywords:
        intent = kw.get("intent", "unknown")
        intent_stats[intent] = intent_stats.get(intent, 0) + 1

    logger.info(f"intent distribution: {intent_stats}")

    state["logs"].append(
        f"intent: {len(keywords)} keywords classified (rules={rule_count}, llm={llm_count})"
    )
    return state
