import sys
import io
import json
import csv
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TEST_INPUT = {
    "site_url": "mebel-dom.ru",
    "business_description": "интернет-магазин мебели, продаём диваны, кресла, пуфы",
    "seed_keywords": [
        "купить диван",
        "угловой диван",
        "диван кровать",
    ],
    "geo": "Москва",
    "language": "ru",
    "target_pages": [
        "/catalog/divany/",
        "/catalog/uglovye-divany/",
        "/catalog/divany-krovati/",
    ],
    "competitors": ["divan.ru", "hoff.ru"],
    "commercial_priority": {
        "диваны": 5,
        "кресла": 3,
        "пуфы": 2,
    }
}


def run_test():
    print("\n" + "█" * 60)
    print("  ТЕСТ ПАЙПЛАЙНА СЕМАНТИЧЕСКОГО ЯДРА")
    print("  Режим: без API (моки + правила)")
    print("█" * 60)

    state = {
        **TEST_INPUT,
        "raw_keywords": [],
        "cleaned_keywords": [],
        "classified_keywords": [],
        "clusters": [],
        "gap_analysis": [],
        "output_table": [],
        "errors": [],
        "logs": [],
        "current_step": "init",
    }

    print("\n" + "─" * 60)
    print("ШАГ 1: RESEARCH AGENT")
    print("─" * 60)
    from agents.research_agent import research_agent
    state = research_agent(state)
    print(f"  Результат: {len(state['raw_keywords'])} запросов собрано")
    for kw in state['raw_keywords']:
        src = kw['source']
        imp = f"показов: {kw['impressions']}" if kw.get('impressions') else ""
        print(f"    [{src}] {kw['text']} {imp}")

    print("\n" + "─" * 60)
    print("ШАГ 2: EXPANSION AGENT")
    print("─" * 60)
    from agents.expansion_agent import expansion_agent
    state = expansion_agent(state)
    total = len(state['raw_keywords'])
    print(f"  Результат: {total} запросов после расширения")
    print("  Примеры новых запросов:")
    expanded = [kw for kw in state['raw_keywords'] if 'modifier' in kw['source']]
    for kw in expanded[:10]:
        print(f"    {kw['text']}")
    print(f"    ... и ещё {len(expanded) - 10}")

    print("\n" + "─" * 60)
    print("ШАГ 3: CLEANING AGENT")
    print("─" * 60)
    from agents.cleaning_agent import cleaning_agent
    before = len(state['raw_keywords'])
    state = cleaning_agent(state)
    after = len(state['cleaned_keywords'])
    print(f"  Было:     {before}")
    print(f"  Осталось: {after}")
    print(f"  Удалено:  {before - after}")

    print("\n" + "─" * 60)
    print("ШАГ 4: INTENT AGENT")
    print("─" * 60)
    from agents.intent_agent import intent_agent
    state = intent_agent(state)
    intents = {}
    for kw in state['classified_keywords']:
        i = kw.get('intent', '?')
        intents[i] = intents.get(i, 0) + 1
    print("  Распределение интентов:")
    for intent, count in sorted(intents.items(), key=lambda x: -x[1]):
        bar = "█" * (count // 3)
        print(f"    {intent:<20} {count:>3}  {bar}")

    print("\n" + "─" * 60)
    print("ШАГ 5: CLUSTERING AGENT (без LLM — упрощённый режим)")
    print("─" * 60)
    state = _simple_clustering(state)
    print(f"  Сформировано кластеров: {len(state['clusters'])}")
    for c in state['clusters']:
        print(f"    [{c['intent']}] {c['name']} — {len(c['keywords'])} запросов")

    print("\n" + "─" * 60)
    print("ШАГ 6: PRIORITIZATION AGENT")
    print("─" * 60)
    from agents.prioritization_agent import prioritization_agent
    state = prioritization_agent(state)
    print("  Топ кластеров по приоритету:")
    for c in state['clusters'][:6]:
        score = c['priority_score']
        label = "HIGH" if score >= 70 else ("MID" if score >= 40 else "LOW")
        print(f"    [{label}] {score:>5} | {c['name']}")

    print("\n" + "─" * 60)
    print("ШАГ 7: MAPPING AGENT")
    print("─" * 60)
    from agents.mapping_agent import mapping_agent
    state = mapping_agent(state)
    actions = {}
    for c in state['clusters']:
        a = c['action']
        actions[a] = actions.get(a, 0) + 1
    print("  Карта действий:")
    labels = {
        'create_page': 'Создать страницу',
        'update_page': 'Обновить страницу',
        'create_blog': 'Написать статью',
        'add_faq':     'Добавить в FAQ',
        'skip':        'Не брать',
    }
    for action, count in actions.items():
        print(f"    {labels.get(action, action):<25} {count}")

    print("\n" + "─" * 60)
    print("ШАГ 8: CANNIBALIZATION AGENT")
    print("─" * 60)
    from agents.cannibalization_agent import cannibalization_agent
    state = cannibalization_agent(state)
    issues = state.get("cannibalization_issues", [])
    if issues:
        print(f"  Найдено проблем: {len(issues)}")
        for issue in issues[:3]:
            print(f"  [{issue['severity'].upper()}] {issue['recommendation'][:80]}...")
    else:
        print("  Каннибализация не обнаружена")

    print("\n" + "─" * 60)
    print("ШАГ 9: BRIEF GENERATOR — ТЗ для копирайтера")
    print("─" * 60)
    from agents.brief_agent import brief_agent
    state = brief_agent(state)
    briefs = state.get("briefs", [])
    print(f"  ТЗ создано: {len(briefs)}")
    if briefs:
        b = briefs[0]
        print(f"\n  Пример ТЗ — {b['cluster']}:")
        print(f"    Title:       {b['title']}")
        print(f"    H1:          {b['h1']}")
        print(f"    Description: {b['description'][:70]}...")
        print(f"    Структура:")
        for s in b.get("structure", [])[:4]:
            print(f"      - {s}")

    print("\n" + "─" * 60)
    print("ШАГ 10: OUTPUT — сохраняем результат")
    print("─" * 60)
    csv_path = _save_results(state)
    print(f"  CSV сохранён: {csv_path}")

    from utils.html_report import generate_html_report
    html_path = generate_html_report(state)
    print(f"  HTML-дашборд: {html_path}")

    _print_final_report(state)

    return state


CLUSTER_RULES = {
    "для сна":      ("Диваны для сна",            "commercial",    "/catalog/divany-dlya-sna/"),
    "для кухни":    ("Диваны для кухни",           "commercial",    "/catalog/divany-dlya-kuhni/"),
    "для офиса":    ("Диваны для офиса",           "commercial",    "/catalog/divany-dlya-ofisa/"),
    "угловой":      ("Угловые диваны",             "commercial",    "/catalog/uglovye-divany/"),
    "раскладной":   ("Раскладные диваны",          "commercial",    "/catalog/skladnye-divany/"),
    "кожаный":      ("Кожаные диваны",             "commercial",    "/catalog/kozhanye-divany/"),
    "в москве":     ("Купить диван в Москве",      "local",         "/catalog/divany-moskva/"),
    "в спб":        ("Купить диван в СПб",         "local",         "/catalog/divany-spb/"),
    "недорого":     ("Недорогие диваны",           "commercial",    "/catalog/nedorogie-divany/"),
    "как выбрать":  ("Как выбрать диван",          "informational", "/blog/kak-vybrat-divan/"),
    "или кровать":  ("Диван или кровать",          "comparison",    "/blog/divan-ili-krovat/"),
    "что лучше":    ("Что лучше: диван или кровать", "comparison",  "/blog/divan-ili-krovat/"),
    "не скрипит":   ("Диван который не скрипит",   "problem_based", "/blog/divan-ne-skripit/"),
    "легко чистит": ("Диван легко чистится",       "problem_based", "/blog/uhod-za-divanom/"),
    "маленький":    ("Маленькие диваны",           "commercial",    "/catalog/malenkie-divany/"),
    "с ящиком":     ("Диваны с ящиком",            "commercial",    "/catalog/divany-s-yashchikom/"),
    "кровать":      ("Диваны-кровати",             "commercial",    "/catalog/divany-krovati/"),
    "заказать":     ("Заказать диван онлайн",      "transactional", "/catalog/divany/"),
}


def _simple_clustering(state: dict) -> dict:
    keywords = state['classified_keywords']
    clusters_map = {}
    unmatched = []

    for kw in keywords:
        text = kw['text'].lower()
        matched = False
        for pattern, (name, intent, url) in CLUSTER_RULES.items():
            if pattern in text:
                if name not in clusters_map:
                    clusters_map[name] = {
                        "name": name,
                        "main_keyword": kw['text'],
                        "keywords": [],
                        "intent": intent,
                        "recommended_page_type": "category",
                        "recommended_url": url,
                        "action": "create_page",
                        "priority_score": 0.0,
                        "reason": f"pattern: '{pattern}'",
                        "existing_page": None,
                    }
                clusters_map[name]["keywords"].append(kw['text'])
                matched = True
                break
        if not matched:
            unmatched.append(kw)

    if unmatched:
        clusters_map["Купить диван (общий)"] = {
            "name": "Купить диван (общий)",
            "main_keyword": "купить диван",
            "keywords": [kw['text'] for kw in unmatched],
            "intent": "commercial",
            "recommended_page_type": "category",
            "recommended_url": "/catalog/divany/",
            "action": "update_page",
            "priority_score": 0.0,
            "reason": "Общие коммерческие запросы",
            "existing_page": "/catalog/divany/",
        }

    state['clusters'] = list(clusters_map.values())
    return state


def _save_results(state: dict) -> str:
    Path("data/output").mkdir(parents=True, exist_ok=True)
    filepath = "data/output/test_result.csv"

    rows = []
    for c in state['clusters']:
        score = c['priority_score']
        if score >= 70:
            priority_label = f"ВЫСОКИЙ ({score})"
        elif score >= 40:
            priority_label = f"СРЕДНИЙ ({score})"
        else:
            priority_label = f"НИЗКИЙ ({score})"

        actions = {
            'create_page': 'Создать страницу',
            'update_page': 'Обновить страницу',
            'create_blog': 'Написать статью',
            'add_faq':     'Добавить в FAQ',
            'skip':        'Не брать',
        }

        rows.append({
            "Кластер":      c['name'],
            "Главный ключ": c['main_keyword'],
            "Запросов":     len(c['keywords']),
            "Все запросы":  " | ".join(c['keywords'][:5]),
            "Интент":       c['intent'],
            "URL":          c.get('recommended_url', '—'),
            "Действие":     actions.get(c['action'], c['action']),
            "Приоритет":    priority_label,
            "Причина":      c['reason'],
        })

    rows.sort(key=lambda r: float(r['Приоритет'].split('(')[1].rstrip(')')), reverse=True)

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return filepath


def _print_final_report(state: dict):
    clusters = state['clusters']
    high   = [c for c in clusters if c['priority_score'] >= 70]
    medium = [c for c in clusters if 40 <= c['priority_score'] < 70]
    low    = [c for c in clusters if c['priority_score'] < 40]

    print("\n" + "█" * 60)
    print("  ИТОГОВЫЙ ОТЧЁТ")
    print("█" * 60)
    print(f"\n  Сайт:              {state['site_url']}")
    print(f"  Собрано запросов:  {len(state['raw_keywords'])}")
    print(f"  После чистки:      {len(state['cleaned_keywords'])}")
    print(f"  Кластеров итого:   {len(clusters)}")
    print(f"    Высокий приоритет: {len(high)}")
    print(f"    Средний приоритет: {len(medium)}")
    print(f"    Низкий приоритет:  {len(low)}")

    print("\n  ТОП-5 СТРАНИЦ ДЛЯ СОЗДАНИЯ:")
    create = sorted(
        [c for c in clusters if c['action'] == 'create_page'],
        key=lambda x: x['priority_score'],
        reverse=True
    )
    for i, c in enumerate(create[:5], 1):
        print(f"    {i}. {c['name']}")
        print(f"       URL: {c['recommended_url']}")
        print(f"       Запросов: {len(c['keywords'])}")
        print(f"       Приоритет: {c['priority_score']}")

    print("\n  Результат: data/output/test_result.csv")
    print("  Открой в Excel или Google Sheets\n")


if __name__ == "__main__":
    run_test()
