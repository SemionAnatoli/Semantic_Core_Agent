import anthropic
from loguru import logger
from agents.state import PipelineState, Keyword
from config.settings import ANTHROPIC_API_KEY, LLM_MODEL

MODIFIERS = {
    "commercial":      ["купить", "цена", "заказать", "недорого", "стоимость"],
    "geo":             ["в Москве", "в СПб", "с доставкой", "рядом"],
    "characteristics": ["раскладной", "кожаный", "маленький", "угловой"],
    "purpose":         ["для кухни", "для сна", "для офиса", "для гостиной"],
    "audience":        ["для детей", "для пожилых", "для маленькой квартиры"],
    "problem":         ["не скрипит", "легко чистится", "занимает мало места"],
    "comparison":      ["или кровать", "что лучше", "отличие"],
    "materials":       ["велюр", "кожа", "экокожа", "рогожка"],
    "size":            ["140 см", "160 см", "компактный"],
}


def _expand_with_modifiers(seed: str) -> list[Keyword]:
    results = []
    for mod_type, mods in MODIFIERS.items():
        for mod in mods[:3]:
            results.append({
                "text": f"{seed} {mod}",
                "source": f"expansion_modifier_{mod_type}",
                "volume": None, "clicks": None, "impressions": None,
                "position": None, "intent": None, "intent_confidence": None,
                "cluster": None, "action": None, "priority_score": None,
                "recommended_url": None, "reason": None,
            })
    return results


def _expand_with_llm(seeds: list[str], business: str, geo: str) -> list[Keyword]:
    if not ANTHROPIC_API_KEY:
        logger.warning("no ANTHROPIC_API_KEY, skipping LLM expansion")
        return []

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""Ты SEO-специалист. Бизнес: {business}. Гео: {geo}.

Стартовые ключи:
{chr(10).join(f"- {s}" for s in seeds)}

Сгенерируй 30 новых поисковых запросов: long-tail, вопросы, сценарии, проблемы, сравнения.
Выводи только список запросов, по одному на строке."""

    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        lines = response.content[0].text.strip().split("\n")
        results = []
        for line in lines:
            kw = line.strip().lstrip("- ").strip()
            if kw:
                results.append({
                    "text": kw, "source": "expansion_llm",
                    "volume": None, "clicks": None, "impressions": None,
                    "position": None, "intent": None, "intent_confidence": None,
                    "cluster": None, "action": None, "priority_score": None,
                    "recommended_url": None, "reason": None,
                })
        logger.info(f"llm generated: {len(results)}")
        return results
    except Exception as e:
        logger.error(f"llm expansion error: {e}")
        return []


def expansion_agent(state: PipelineState) -> PipelineState:
    logger.info("expansion agent started")
    state["current_step"] = "expansion"
    new_keywords: list[Keyword] = []

    for seed in state["seed_keywords"]:
        expanded = _expand_with_modifiers(seed)
        new_keywords.extend(expanded)

    llm_kws = _expand_with_llm(state["seed_keywords"], state["business_description"], state["geo"])
    new_keywords.extend(llm_kws)

    state["raw_keywords"] = state["raw_keywords"] + new_keywords
    state["logs"].append(f"expansion: +{len(new_keywords)}, total: {len(state['raw_keywords'])}")
    logger.info(f"after expansion: {len(state['raw_keywords'])}")
    return state
