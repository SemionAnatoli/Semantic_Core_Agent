from loguru import logger
from agents.state import PipelineState, Keyword


def _mock_gsc_data(site_url: str) -> list[Keyword]:
    logger.info(f"[GSC] загружаем данные для {site_url}")
    return [
        {"text": "диван для ежедневного сна", "source": "gsc", "volume": None,
         "clicks": 12, "impressions": 3200, "position": 14.7,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
        {"text": "маленький диван в комнату", "source": "gsc", "volume": None,
         "clicks": 8, "impressions": 1800, "position": 18.2,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
        {"text": "диван для кухни со спальным местом", "source": "gsc", "volume": None,
         "clicks": 5, "impressions": 2100, "position": 16.5,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
        {"text": "угловой диван недорого", "source": "gsc", "volume": None,
         "clicks": 45, "impressions": 890, "position": 7.3,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
    ]


def _mock_yandex_data(site_url: str) -> list[Keyword]:
    logger.info(f"[Яндекс] загружаем данные для {site_url}")
    return [
        {"text": "купить диван москва", "source": "yandex_webmaster", "volume": 4200,
         "clicks": 23, "impressions": 1200, "position": 11.0,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
        {"text": "диван кровать раскладной", "source": "yandex_webmaster", "volume": 3100,
         "clicks": 67, "impressions": 2300, "position": 5.4,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
    ]


def _mock_competitor_data(competitors: list[str]) -> list[Keyword]:
    logger.info(f"[конкуренты] анализируем: {competitors}")
    return [
        {"text": "диваны для кухни", "source": "competitor", "volume": 1800,
         "clicks": None, "impressions": None, "position": None,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
        {"text": "диваны для ежедневного сна", "source": "competitor", "volume": 2400,
         "clicks": None, "impressions": None, "position": None,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
        {"text": "модульный диван", "source": "competitor", "volume": 5600,
         "clicks": None, "impressions": None, "position": None,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
        {"text": "диван без подлокотников", "source": "competitor", "volume": 890,
         "clicks": None, "impressions": None, "position": None,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None},
    ]


def _seeds_to_keywords(seed_keywords: list[str]) -> list[Keyword]:
    return [
        {"text": kw, "source": "seed", "volume": None,
         "clicks": None, "impressions": None, "position": None,
         "intent": None, "intent_confidence": None, "cluster": None,
         "action": None, "priority_score": None, "recommended_url": None, "reason": None}
        for kw in seed_keywords
    ]


def research_agent(state: PipelineState) -> PipelineState:
    logger.info("research agent started")
    state["current_step"] = "research"
    all_keywords: list[Keyword] = []

    seeds = _seeds_to_keywords(state["seed_keywords"])
    all_keywords.extend(seeds)
    logger.info(f"seeds: {len(seeds)}")

    try:
        gsc = _mock_gsc_data(state["site_url"])
        all_keywords.extend(gsc)
        logger.info(f"gsc: {len(gsc)}")
    except Exception as e:
        state["errors"].append(f"gsc: {e}")

    try:
        yandex = _mock_yandex_data(state["site_url"])
        all_keywords.extend(yandex)
        logger.info(f"yandex: {len(yandex)}")
    except Exception as e:
        state["errors"].append(f"yandex: {e}")

    if state.get("competitors"):
        try:
            comp = _mock_competitor_data(state["competitors"])
            all_keywords.extend(comp)
            logger.info(f"competitors: {len(comp)}")
        except Exception as e:
            state["errors"].append(f"competitors: {e}")

    state["raw_keywords"] = all_keywords
    state["logs"].append(f"research: {len(all_keywords)} keywords collected")
    logger.info(f"total collected: {len(all_keywords)}")
    return state
