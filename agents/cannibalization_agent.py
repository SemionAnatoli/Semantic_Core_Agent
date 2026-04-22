from loguru import logger
from agents.state import PipelineState


def _find_keyword_overlaps(clusters: list[dict]) -> list[dict]:
    keyword_map: dict[str, list[str]] = {}

    for cluster in clusters:
        for kw in cluster.get("keywords", []):
            kw_norm = kw.lower().strip()
            if kw_norm not in keyword_map:
                keyword_map[kw_norm] = []
            keyword_map[kw_norm].append(cluster["name"])

    conflicts = []
    for kw, cluster_names in keyword_map.items():
        if len(cluster_names) > 1:
            conflicts.append({
                "type": "keyword_overlap",
                "keyword": kw,
                "clusters": cluster_names,
                "severity": "high",
                "recommendation": (
                    f"Запрос '{kw}' встречается в {len(cluster_names)} кластерах: "
                    f"{', '.join(cluster_names)}. "
                    f"Оставить только в одном — самом релевантном."
                )
            })
    return conflicts


def _find_url_conflicts(clusters: list[dict]) -> list[dict]:
    url_map: dict[str, list[str]] = {}

    for cluster in clusters:
        url = cluster.get("recommended_url", "").strip()
        if not url or url == "—":
            continue
        if url not in url_map:
            url_map[url] = []
        url_map[url].append(cluster["name"])

    conflicts = []
    for url, cluster_names in url_map.items():
        if len(cluster_names) > 1:
            conflicts.append({
                "type": "url_conflict",
                "url": url,
                "clusters": cluster_names,
                "severity": "critical",
                "recommendation": (
                    f"URL {url} назначен {len(cluster_names)} кластерам: "
                    f"{', '.join(cluster_names)}. "
                    f"Объединить кластеры или назначить разные URL."
                )
            })
    return conflicts


def _find_intent_conflicts(clusters: list[dict]) -> list[dict]:
    conflicts = []
    checked = set()
    stop_words = {"для", "и", "в", "с", "или", "на", "по", "под", "при", "о", "об"}

    for i, c1 in enumerate(clusters):
        for j, c2 in enumerate(clusters):
            if i >= j:
                continue
            pair = (min(i, j), max(i, j))
            if pair in checked:
                continue
            checked.add(pair)

            if c1.get("intent") != c2.get("intent"):
                continue

            words1 = set(c1["name"].lower().split()) - stop_words
            words2 = set(c2["name"].lower().split()) - stop_words
            overlap = words1 & words2

            if len(overlap) >= 2:
                conflicts.append({
                    "type": "intent_similarity",
                    "clusters": [c1["name"], c2["name"]],
                    "shared_words": list(overlap),
                    "intent": c1.get("intent"),
                    "severity": "medium",
                    "recommendation": (
                        f"Кластеры '{c1['name']}' и '{c2['name']}' "
                        f"имеют одинаковый интент и похожие темы. "
                        f"Проверить: не будут ли эти страницы конкурировать."
                    )
                })

    return conflicts


def cannibalization_agent(state: PipelineState) -> PipelineState:
    logger.info("cannibalization agent started")

    clusters = state.get("clusters", [])
    all_issues = []

    kw_issues = _find_keyword_overlaps(clusters)
    all_issues.extend(kw_issues)

    url_issues = _find_url_conflicts(clusters)
    all_issues.extend(url_issues)

    intent_issues = _find_intent_conflicts(clusters)
    all_issues.extend(intent_issues)

    logger.info(f"keyword overlaps: {len(kw_issues)}, url conflicts: {len(url_issues)}, similar clusters: {len(intent_issues)}")

    state["cannibalization_issues"] = all_issues

    conflict_cluster_names = set()
    for issue in url_issues + kw_issues:
        for name in issue.get("clusters", []):
            conflict_cluster_names.add(name)

    for cluster in clusters:
        if cluster["name"] in conflict_cluster_names:
            cluster["cannibalization_risk"] = "high"
            cluster["priority_score"] = max(0, cluster["priority_score"] - 15)
        else:
            cluster["cannibalization_risk"] = "low"

    critical = [i for i in all_issues if i.get("severity") == "critical"]
    high_sev = [i for i in all_issues if i.get("severity") == "high"]
    medium   = [i for i in all_issues if i.get("severity") == "medium"]

    if all_issues:
        logger.warning(f"issues found: {len(all_issues)} (critical={len(critical)}, high={len(high_sev)}, medium={len(medium)})")
    else:
        logger.info("no cannibalization detected")

    state["logs"].append(
        f"cannibalization: {len(all_issues)} issues "
        f"(critical={len(critical)}, high={len(high_sev)}, medium={len(medium)})"
    )
    return state
