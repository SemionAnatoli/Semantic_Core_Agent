@echo off
chcp 65001 >nul
cls

echo.
echo ████████████████████████████████████████████████████
echo   SEMANTIC CORE AGENT — запуск
echo ████████████████████████████████████████████████████
echo.

:: Переходим в папку скрипта
cd /d "%~dp0"

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден.
    echo Установите Python 3.10+ с сайта https://python.org
    pause
    exit /b 1
)

:: Проверяем зависимости
echo [1/3] Проверка зависимостей...
pip install -q anthropic langgraph langchain langchain-anthropic python-dotenv loguru pandas >nul 2>&1
echo       OK

:: Копируем .env если не существует
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo [!] Создан файл .env — добавьте ваши API ключи
    )
)

:: Запускаем пайплайн
echo [2/3] Запуск анализа...
echo.
python test_pipeline.py
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Пайплайн завершился с ошибкой.
    pause
    exit /b 1
)

:: Открываем отчёт
echo.
echo [3/3] Открываем отчёт в браузере...
if exist "data\output\report.html" (
    start "" "data\output\report.html"
    echo       Готово! Отчёт открыт в браузере.
) else (
    echo [!] Файл отчёта не найден.
)

echo.
echo ████████████████████████████████████████████████████
echo   АНАЛИЗ ЗАВЕРШЁН
echo   Отчёт: data\output\report.html
echo   Данные: data\output\test_result.csv
echo ████████████████████████████████████████████████████
echo.
pause
