import json
import anthropic
from loguru import logger
from agents.state import PipelineState, Keyword, Cluster
from config.settings import ANTHROPIC_API_KEY, LLM_MODEL


def _group_by_entities(keywords: list[Keyword]) -> dict[str, list[Keyword]]:
    groups: dict[str, list[Keyword]] = {}
    for kw in keywords:
        words = kw["text"].split()
        key = " ".join(words[:2]) if len(words) >= 2 else words[0]
        if key not in groups:
            groups[key] = []
        groups[key].append(kw)
    return groups


def _llm_cluster(
    keywords: list[Keyword],
    business_description: str,
    existing_pages: list[str],
) -> list[Cluster]:
    if not ANTHROPIC_API_KEY:
        logger.warning("no API key, using fallback clustering")
        return _fallback_clustering(keywords)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    kw_list = "\n".join(
        f"- {kw['text']} [интент: {kw.get('intent', '?')}]"
        for kw in keywords
    )
    pages_list = "\n".join(f"- {p}" for p in existing_pages) if existing_pages else "- (нет данных)"

    prompt = f"""Ты SEO-архитектор. Бизнес: {business_description}.

Существующие страницы сайта:
{pages_list}

Список запросов (с интентами):
{kw_list}

Твоя задача: сгруппировать запросы в кластеры для SEO.
Правила:
1. Один кластер = один поисковый интент = одна страница
2. НЕ группируй по похожести слов — группируй по смыслу и интенту
3. "диван для кухни" и "диван для гостиной" — РАЗНЫЕ кластеры
4. Кластер должен быть закрываем одной страницей
5. Навигационные запросы — в отдельный кластер "navigational" (не брать)

Для каждого кластера определи:
- action: create_page / update_page / create_blog / add_faq / skip
- recommended_url: предлагаемый URL (транслит, slug)

Ответь строго в JSON:
[
  {{
    "name": "Диваны для ежедневного сна",
    "main_keyword": "диван для ежедневного сна",
    "keywords": ["диван для ежедневного сна", "диван кровать для сна", ...],
    "intent": "commercial",
    "recommended_page_type": "category",
    "recommended_url": "/catalog/divany-dlya-sna/",
    "action": "create_page",
    "priority_score": 0,
    "reason": "Отдельный интент, нет страницы, высокие показы",
    "existing_page": null
  }},
  ...
]
Только JSON, без пояснений."""

    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        clusters_data = json.loads(raw)

        clusters = []
        for c in clusters_data:
            clusters.append({
                "name": c.get("name", ""),
                "main_keyword": c.get("main_keyword", ""),
                "keywords": c.get("keywords", []),
                "intent": c.get("intent", "commercial"),
                "recommended_page_type": c.get("recommended_page_type", "category"),
                "recommended_url": c.get("recommended_url", ""),
                "action": c.get("action", "create_page"),
                "priority_score": 0.0,
                "reason": c.get("reason", ""),
                "existing_page": c.get("existing_page"),
            })
        return clusters

    except Exception as e:
        logger.error(f"llm clustering error: {e}")
        return _fallback_clustering(keywords)


def _fallback_clustering(keywords: list[Keyword]) -> list[Cluster]:
    groups = _group_by_entities(keywords)
    clusters = []
    for group_name, kws in groups.items():
        main_kw = kws[0]["text"]
        clusters.append({
            "name": group_name.title(),
            "main_keyword": main_kw,
            "keywords": [kw["text"] for kw in kws],
            "intent": kws[0].get("intent") or "commercial",
            "recommended_page_type": "category",
            "recommended_url": f"/catalog/{group_name.replace(' ', '-')}/",
            "action": "create_page",
            "priority_score": 0.0,
            "reason": "auto clustering",
            "existing_page": None,
        })
    return clusters


def clustering_agent(state: PipelineState) -> PipelineState:
    logger.info("clustering agent started")
    state["current_step"] = "clustering"

    keywords = state["classified_keywords"]
    business = state["business_description"]
    existing_pages = state.get("target_pages", [])

    to_cluster = [kw for kw in keywords if kw.get("intent") != "navigational"]
    navigational = [kw for kw in keywords if kw.get("intent") == "navigational"]

    logger.info(f"to cluster: {len(to_cluster)}, navigational (skip): {len(navigational)}")

    clusters = _llm_cluster(to_cluster, business, existing_pages)
    state["clusters"] = clusters

    logger.info(f"clusters formed: {len(clusters)}")
    for c in clusters:
        logger.info(f"  [{c['action']}] {c['name']} — {len(c['keywords'])} keywords")

    state["logs"].append(
        f"clustering: {len(to_cluster)} keywords -> {len(clusters)} clusters"
    )
    return state
