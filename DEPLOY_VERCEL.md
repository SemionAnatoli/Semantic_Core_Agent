# Деплой на Vercel

Проект подготовлен как статическое SPA в папке `web/`. Оно работает без API-ключей: вся демо-логика пайплайна выполняется в браузере.

Для Vercel добавлена явная Node-сборка: `npm run build` копирует `web/` в `dist/`. Это важно, потому что в репозитории также есть Python-часть и `requirements.txt`; без явной сборки Vercel может ошибочно искать FastAPI-приложение.

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
5. Build Command: `npm run build`.
6. Output Directory: `dist`.
7. Нажать `Deploy`.

Файл `vercel.json` уже настроен:

- Build Command: `npm run build`;
- Output Directory: `dist`;
- `/` открывает `dist/index.html`;
- `/dashboard` открывает тот же интерфейс.

## Вариант 2: через Vercel CLI

```bash
vercel
vercel --prod
```

Если CLI спросит настройки:

- Framework: `Other`;
- Build Command: `npm run build`;
- Output Directory: `dist`.

## Локальная проверка

Можно открыть файл напрямую:

```text
web/index.html
```

Или запустить любой статический сервер из корня проекта.

Проверить Vercel-сборку локально:

```bash
npm run build
```
