"""
Общее состояние пайплайна — передаётся между всеми агентами.
Каждый агент читает нужные поля и добавляет свои результаты.
"""
from typing import TypedDict, List, Dict, Optional, Any


class Keyword(TypedDict):
    """Единица — поисковый запрос с метаданными."""
    text: str                        # сам запрос
    source: str                      # откуда пришёл: gsc / wordstat / expansion / competitor
    volume: Optional[int]            # частотность
    clicks: Optional[int]            # клики из GSC
    impressions: Optional[int]       # показы из GSC
    position: Optional[float]        # средняя позиция
    intent: Optional[str]            # commercial / informational / local / ...
    intent_confidence: Optional[float]
    cluster: Optional[str]           # название кластера
    action: Optional[str]            # create_page / update_page / create_blog / skip
    priority_score: Optional[float]  # 0–100
    recommended_url: Optional[str]   # рекомендуемый URL страницы
    reason: Optional[str]            # объяснение решения


class Cluster(TypedDict):
    """Кластер — группа запросов под одну страницу."""
    name: str
    main_keyword: str
    keywords: List[str]
    intent: str
    recommended_page_type: str       # category / blog / faq / geo
    recommended_url: str
    action: str                      # create_page / update_page / ...
    priority_score: float
    reason: str
    existing_page: Optional[str]     # URL если страница уже есть


class PipelineState(TypedDict):
    """Полное состояние пайплайна — живёт от старта до выгрузки."""

    # --- ВХОД ---
    site_url: str
    business_description: str
    seed_keywords: List[str]
    geo: str
    language: str
    target_pages: List[str]          # существующие страницы сайта
    competitors: List[str]           # URL конкурентов
    commercial_priority: Dict[str, int]  # {"диваны": 5, "кресла": 3}

    # --- ПРОМЕЖУТОЧНЫЕ ДАННЫЕ ---
    raw_keywords: List[Keyword]       # всё что насобирали
    cleaned_keywords: List[Keyword]   # после чистки
    classified_keywords: List[Keyword] # после определения интента

    # --- РЕЗУЛЬТАТ ---
    clusters: List[Cluster]           # финальные кластеры
    gap_analysis: List[Dict]          # что есть vs чего нет
    output_table: List[Dict]          # финальная таблица для Google Sheets

    # --- МЕТА ---
    errors: List[str]                 # ошибки по ходу работы
    logs: List[str]                   # лог действий агентов
    current_step: str                 # какой агент работает сейчас
