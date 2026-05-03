# Деплой на Vercel

Проект подготовлен как статическое SPA в папке `web/`. Оно работает без Node-сборки и без API-ключей: вся демо-логика пайплайна выполняется в браузере.

## Что увидит работодатель

- форма запуска анализа сайта;
- pipeline из 10 шагов: Research, Expansion, Cleaning, Intent, Clustering, Mapping, Scoring, Risks, Briefs, Output;
- интерактивный дашборд с KPI, приоритетами, интентами и картой действий;
- таблица кластеров с поиском и фильтрами;
- drawer с деталями каждого кластера;
- анализ каннибализации;
- ТЗ для страниц: Title, H1, Description, структура, LSI;
- экспорт CSV и JSON;
- копирование action plan и ТЗ;
- переключение светлой / тёмной темы с сохранением выбора в браузере.

## Вариант 1: через GitHub + Vercel UI

1. Запушить репозиторий на GitHub.
2. В Vercel выбрать `Add New Project`.
3. Импортировать репозиторий.
4. Framework Preset: `Other`.
5. Build Command: оставить пустым.
6. Output Directory: оставить пустым.
7. Нажать `Deploy`.

Файл `vercel.json` уже настроен:

- `/` открывает `web/index.html`;
- `/dashboard` открывает тот же интерфейс;
- `/app.js` и `/styles.css` корректно отдаются из папки `web/`.

## Вариант 2: через Vercel CLI

```bash
vercel
vercel --prod
```

Если CLI спросит настройки:

- Framework: `Other`;
- Build Command: пусто;
- Output Directory: пусто.

## Локальная проверка

Можно открыть файл напрямую:

```text
web/index.html
```

Или запустить любой статический сервер из корня проекта.
