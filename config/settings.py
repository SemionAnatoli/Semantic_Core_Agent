import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "config/google_service_account.json")
GSC_SITE_URL    = os.getenv("GSC_SITE_URL", "")
SPREADSHEET_ID  = os.getenv("SPREADSHEET_ID", "")

YANDEX_TOKEN   = os.getenv("YANDEX_TOKEN", "")
YANDEX_USER_ID = os.getenv("YANDEX_USER_ID", "")

KEYS_SO_API_KEY  = os.getenv("KEYS_SO_API_KEY", "")
SPYWORDS_API_KEY = os.getenv("SPYWORDS_API_KEY", "")
SERPAPI_KEY      = os.getenv("SERPAPI_KEY", "")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID  = os.getenv("TELEGRAM_ADMIN_ID", "")

LLM_MODEL      = "claude-opus-4-5"
LLM_MAX_TOKENS = 4096

SCORING_WEIGHTS = {
    "search_volume":        0.25,
    "business_value":       0.20,
    "ranking_opportunity":  0.20,
    "intent_match":         0.15,
    "trend_growth":         0.10,
    "content_gap":          0.10,
    "keyword_difficulty":  -0.20,
    "cannibalization_risk": -0.15,
}

INTENT_TYPES = {
    "commercial":    "Категория / листинг",
    "transactional": "Категория / карточка / лендинг",
    "informational": "Статья / гайд",
    "comparison":    "Статья / comparison page",
    "navigational":  "Не брать",
    "local":         "Гео-страница",
    "problem_based": "Гайд + товарная подборка",
}

ACTIONS = {
    "create_page": "Создать страницу",
    "update_page": "Обновить страницу",
    "create_blog": "Создать статью",
    "add_faq":     "Добавить в FAQ",
    "skip":        "Не брать в работу",
}
