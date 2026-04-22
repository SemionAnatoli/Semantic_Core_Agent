from loguru import logger
from agents.state import PipelineState, Cluster
from config.settings import ACTIONS, INTENT_TYPES


def _find_existing_page(cluster: Cluster, target_pages: list[str]) -> str | None:
    main_kw_words = set(cluster["main_keyword"].lower().split())

    for page in target_pages:
        page_words = set(
            page.lower()
            .replace("/", " ")
            .replace("-", " ")
            .replace("_", " ")
            .split()
        )
        overlap = main_kw_words & page_words
        if len(overlap) >= max(1, len(main_kw_words) // 2):
            return page

    return None


def _decide_action(cluster: Cluster, existing_page: str | None) -> str:
    intent = cluster["intent"]

    if intent == "navigational":
        return "skip"
    if intent == "informational":
        return "create_blog"
    if intent == "problem_based":
        return "add_faq" if existing_page else "create_blog"
    if intent == "comparison":
        return "create_blog"

    # commercial / transactional / local
    return "update_page" if existing_page else "create_page"


def _build_gap_analysis(clusters: list[Cluster]) -> list[dict]:
    gap = []
    for c in clusters:
        gap.append({
            "cluster":      c["name"],
            "main_keyword": c["main_keyword"],
            "has_page":     "да" if c["existing_page"] else "нет",
            "existing_url": c["existing_page"] or "—",
            "intent":       c["intent"],
            "action":       ACTIONS.get(c["action"], c["action"]),
            "priority":     c["priority_score"],
            "reason":       c["reason"],
        })
    return gap


def _build_output_table(clusters: list[Cluster]) -> list[dict]:
    rows = []
    for c in clusters:
        score = c["priority_score"]
        if score >= 70:
            priority_label = f"ВЫСОКИЙ ({score})"
        elif score >= 40:
            priority_label = f"СРЕДНИЙ ({score})"
        else:
            priority_label = f"НИЗКИЙ ({score})"

        rows.append({
            "Кластер":         c["name"],
            "Главный ключ":    c["main_keyword"],
            "Все запросы":     " | ".join(c["keywords"][:5]),
            "Кол-во запросов": len(c["keywords"]),
            "Интент":          c["intent"],
            "Тип страницы":    INTENT_TYPES.get(c["intent"], c["intent"]),
            "URL страницы":    c.get("recommended_url") or c.get("existing_page") or "—",
            "Действие":        ACTIONS.get(c["action"], c["action"]),
            "Приоритет":       priority_label,
            "Причина":         c["reason"],
        })
    return rows


def mapping_agent(state: PipelineState) -> PipelineState:
    logger.info("mapping agent started")
    state["current_step"] = "mapping"

    clusters = state["clusters"]
    target_pages = state.get("target_pages", [])
    action_stats: dict[str, int] = {}

    for cluster in clusters:
        existing = _find_existing_page(cluster, target_pages)
        if existing:
            cluster["existing_page"] = existing

        action = _decide_action(cluster, cluster.get("existing_page"))
        cluster["action"] = action
        action_stats[action] = action_stats.get(action, 0) + 1

    state["clusters"] = clusters
    state["gap_analysis"] = _build_gap_analysis(clusters)
    state["output_table"] = _build_output_table(clusters)

    logger.info(f"action map: {action_stats}")

    state["logs"].append(
        f"mapping: {len(clusters)} clusters mapped. actions: {action_stats}"
    )
    return state
