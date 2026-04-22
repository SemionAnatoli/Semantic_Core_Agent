import json
import csv
from datetime import datetime
from pathlib import Path
from loguru import logger
from agents.state import PipelineState
from config.settings import SPREADSHEET_ID, GOOGLE_CREDENTIALS_PATH


def _save_to_csv(output_table: list[dict], output_dir: str = "data/output") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{output_dir}/semantic_core_{timestamp}.csv"

    if not output_table:
        logger.warning("empty table, csv not saved")
        return ""

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=output_table[0].keys())
        writer.writeheader()
        writer.writerows(output_table)

    logger.info(f"csv saved: {filepath}")
    return filepath


def _save_to_json(state: PipelineState, output_dir: str = "data/output") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{output_dir}/semantic_core_{timestamp}.json"

    result = {
        "meta": {
            "site_url":                  state["site_url"],
            "business":                  state["business_description"],
            "geo":                       state["geo"],
            "generated_at":              timestamp,
            "total_keywords_collected":  len(state.get("raw_keywords", [])),
            "total_keywords_cleaned":    len(state.get("cleaned_keywords", [])),
            "total_clusters":            len(state.get("clusters", [])),
        },
        "clusters":     state.get("clusters", []),
        "gap_analysis": state.get("gap_analysis", []),
        "output_table": state.get("output_table", []),
        "logs":         state.get("logs", []),
        "errors":       state.get("errors", []),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(f"json saved: {filepath}")
    return filepath


def _save_to_google_sheets(output_table: list[dict], gap_analysis: list[dict]) -> bool:
    if not SPREADSHEET_ID:
        logger.warning("SPREADSHEET_ID not set, skipping Google Sheets")
        return False

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)

        try:
            ws1 = sh.worksheet("Семантическое ядро")
            ws1.clear()
        except Exception:
            ws1 = sh.add_worksheet("Семантическое ядро", rows=1000, cols=20)

        if output_table:
            headers = list(output_table[0].keys())
            rows = [headers] + [[str(row.get(h, "")) for h in headers] for row in output_table]
            ws1.update(rows)
            logger.info(f"google sheets 'Семантическое ядро': {len(output_table)} rows")

        try:
            ws2 = sh.worksheet("Gap-анализ")
            ws2.clear()
        except Exception:
            ws2 = sh.add_worksheet("Gap-анализ", rows=500, cols=15)

        if gap_analysis:
            headers2 = list(gap_analysis[0].keys())
            rows2 = [headers2] + [[str(row.get(h, "")) for h in headers2] for row in gap_analysis]
            ws2.update(rows2)
            logger.info(f"google sheets 'Gap-анализ': {len(gap_analysis)} rows")

        return True

    except ImportError:
        logger.error("gspread not installed: pip install gspread google-auth")
        return False
    except Exception as e:
        logger.error(f"google sheets error: {e}")
        return False


def _print_summary(state: PipelineState) -> None:
    clusters = state.get("clusters", [])
    high   = [c for c in clusters if c["priority_score"] >= 70]
    medium = [c for c in clusters if 40 <= c["priority_score"] < 70]
    low    = [c for c in clusters if c["priority_score"] < 40]

    print("\n" + "=" * 60)
    print("  СЕМАНТИЧЕСКОЕ ЯДРО ГОТОВО")
    print("=" * 60)
    print(f"  Сайт:             {state['site_url']}")
    print(f"  Бизнес:           {state['business_description']}")
    print(f"  Запросов собрано: {len(state.get('raw_keywords', []))}")
    print(f"  После чистки:     {len(state.get('cleaned_keywords', []))}")
    print(f"  Кластеров:        {len(clusters)}")
    print(f"    Высокий:        {len(high)}")
    print(f"    Средний:        {len(medium)}")
    print(f"    Низкий:         {len(low)}")
    print("=" * 60)

    if high:
        print("\nТОП приоритеты:")
        for c in high[:5]:
            from config.settings import ACTIONS
            action = ACTIONS.get(c["action"], c["action"])
            print(f"  [{c['priority_score']}] {c['name']} -> {action}")
            print(f"       URL: {c.get('recommended_url', '—')}")
    print()


def output_agent(state: PipelineState) -> PipelineState:
    logger.info("output agent started")
    state["current_step"] = "output"

    output_table = state.get("output_table", [])
    gap_analysis = state.get("gap_analysis", [])

    csv_path  = _save_to_csv(output_table)
    json_path = _save_to_json(state)
    sheets_ok = _save_to_google_sheets(output_table, gap_analysis)

    _print_summary(state)

    state["logs"].append(
        f"output: csv={csv_path}, json={json_path}, sheets={'ok' if sheets_ok else 'skip'}"
    )
    return state
