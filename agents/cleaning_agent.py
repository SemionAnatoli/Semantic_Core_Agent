import re
from loguru import logger
from agents.state import PipelineState, Keyword

STOP_PATTERNS = [
    r"\bбесплатно\b", r"\bскачать\b", r"\bторрент\b",
    r"\bсвоими руками\b", r"\bсделать самому\b", r"\bчертежи\b",
    r"\bбу\b", r"\bаренда\b", r"\bнапрокат\b",
    r"\bремонт\b", r"\bреставрация\b",
]

MIN_WORDS = 2
MAX_WORDS = 8


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _is_stop(text: str) -> tuple[bool, str]:
    for p in STOP_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True, p
    return False, ""


def _deduplicate(keywords: list[Keyword]) -> list[Keyword]:
    seen = set()
    result = []
    for kw in keywords:
        norm = _normalize(kw["text"])
        if norm not in seen:
            seen.add(norm)
            kw["text"] = norm
            result.append(kw)
    return result


def cleaning_agent(state: PipelineState) -> PipelineState:
    logger.info("cleaning agent started")
    state["current_step"] = "cleaning"

    raw = state["raw_keywords"]
    before = len(raw)

    deduped = _deduplicate(raw)
    removed = {"dup": before - len(deduped), "stop": 0, "short": 0, "long": 0}

    cleaned = []
    for kw in deduped:
        text = kw["text"]
        is_stop, _ = _is_stop(text)
        if is_stop:
            removed["stop"] += 1
            continue
        if len(text.split()) < MIN_WORDS:
            removed["short"] += 1
            continue
        if len(text.split()) > MAX_WORDS:
            removed["long"] += 1
            continue
        cleaned.append(kw)

    state["cleaned_keywords"] = cleaned
    logger.info(f"cleaned: {before} -> {len(cleaned)} (removed: {removed})")
    state["logs"].append(f"cleaning: {before} -> {len(cleaned)}")
    return state
