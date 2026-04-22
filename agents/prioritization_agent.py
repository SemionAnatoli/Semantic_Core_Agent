from loguru import logger
from agents.state import PipelineState, Cluster
from config.settings import SCORING_WEIGHTS


def _estimate_search_volume(cluster: Cluster) -> float:
    kw_count = len(cluster["keywords"])
    if kw_count >= 10:
        return 1.0
    elif kw_count >= 5:
        return 0.7
    elif kw_count >= 3:
        return 0.5
    return 0.3


def _estimate_business_value(cluster: Cluster, commercial_priority: dict) -> float:
    text = cluster["main_keyword"].lower()
    max_priority = max(commercial_priority.values()) if commercial_priority else 5

    for category, priority in commercial_priority.items():
        if category.lower() in text:
            return priority / max_priority

    if cluster["intent"] in ("commercial", "transactional"):
        return 0.5
    elif cluster["intent"] == "informational":
        return 0.2
    return 0.3


def _estimate_ranking_opportunity(cluster: Cluster) -> float:
    action = cluster["action"]
    if action == "update_page":
        return 0.8
    elif action == "create_page":
        return 0.6
    elif action == "create_blog":
        return 0.5
    return 0.3


def _estimate_intent_match(cluster: Cluster) -> float:
    intent_scores = {
        "commercial":    1.0,
        "transactional": 0.9,
        "local":         0.8,
        "problem_based": 0.6,
        "comparison":    0.5,
        "informational": 0.3,
        "navigational":  0.0,
    }
    return intent_scores.get(cluster["intent"], 0.5)


def _estimate_content_gap(cluster: Cluster) -> float:
    return 1.0 if cluster["existing_page"] is None else 0.2


def _estimate_cannibalization_risk(cluster: Cluster) -> float:
    if cluster["existing_page"] and cluster["action"] == "create_page":
        return 0.8
    return 0.1


def _calculate_priority_score(cluster: Cluster, commercial_priority: dict) -> float:
    w = SCORING_WEIGHTS

    score = (
        w["search_volume"]        * _estimate_search_volume(cluster)
        + w["business_value"]     * _estimate_business_value(cluster, commercial_priority)
        + w["ranking_opportunity"] * _estimate_ranking_opportunity(cluster)
        + w["intent_match"]       * _estimate_intent_match(cluster)
        + w["trend_growth"]       * 0.5
        + w["content_gap"]        * _estimate_content_gap(cluster)
        + w["keyword_difficulty"] * 0.5
        + w["cannibalization_risk"] * _estimate_cannibalization_risk(cluster)
    )

    return round(max(0, min(100, score * 100)), 1)


def prioritization_agent(state: PipelineState) -> PipelineState:
    logger.info("prioritization agent started")
    state["current_step"] = "prioritization"

    clusters = state["clusters"]
    commercial_priority = state.get("commercial_priority", {})

    for cluster in clusters:
        cluster["priority_score"] = _calculate_priority_score(cluster, commercial_priority)

    clusters.sort(key=lambda c: c["priority_score"], reverse=True)
    state["clusters"] = clusters

    high   = [c for c in clusters if c["priority_score"] >= 70]
    medium = [c for c in clusters if 40 <= c["priority_score"] < 70]
    low    = [c for c in clusters if c["priority_score"] < 40]

    logger.info(f"high priority (>=70): {len(high)}, medium (40-69): {len(medium)}, low (<40): {len(low)}")

    state["logs"].append(
        f"prioritization: high={len(high)}, mid={len(medium)}, low={len(low)}"
    )
    return state
