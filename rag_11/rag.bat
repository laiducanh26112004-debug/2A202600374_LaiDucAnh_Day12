@echo off
REM RAG-11 Quick Start Script for Windows CMD

setlocal enabledelayedexpansion

if "%1"=="" goto show_menu
if /i "%1"=="start" goto start_app
if /i "%1"=="stop" goto stop_app
if /i "%1"=="logs" goto show_logs
if /i "%1"=="build" goto build_image
if /i "%1"=="shell" goto open_shell
if /i "%1"=="ingest" goto ingest_docs
if /i "%1"=="query" goto query_docs
if /i "%1"=="list" goto list_docs
if /i "%1"=="help" goto show_help

:show_menu
cls
echo.
echo ====== RAG-11 Quick Start Menu ======
echo.
echo Commands:
echo   start      - Start the app with Docker Compose
echo   stop       - Stop the app
echo   logs       - View live logs
echo   build      - Rebuild Docker image
echo   shell      - Open bash in container
echo   ingest     - Ingest documents
echo   query      - Ask a question
echo   list       - List ingested documents
echo   help       - Show this menu
echo.
echo Usage: rag.bat [command]
echo Example: rag.bat start
echo.
goto end

:start_app
cls
echo Starting RAG-11 with Docker Compose...
docker compose up -d
timeout /t 3
docker compose ps
goto end

:stop_app
cls
echo Stopping RAG-11...
docker compose down
goto end

:show_logs
cls
echo Showing live logs (Ctrl+C to exit)...
docker compose logs -f
goto end

:build_image
cls
echo Building Docker image...
docker build -t rag-11:latest .
goto end

:open_shell
cls
echo Opening bash in container...
docker compose exec rag-app bash
goto end

:ingest_docs
cls
echo.
echo Ingestion Options:
echo   1. Ingest a single file
echo   2. Ingest a directory
echo   3. Ingest multiple files
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    set /p file="Enter file path: "
    set /p title="Enter document title (optional): "
    docker compose exec rag-app python main.py ingest !file! --title "!title!"
) else if "%choice%"=="2" (
    set /p dir="Enter directory path: "
    docker compose exec rag-app python main.py ingest-dir !dir! --recursive
) else if "%choice%"=="3" (
    set /p files="Enter file paths (space-separated): "
    docker compose exec rag-app python main.py ingest-many !files!
)
goto end

:query_docs
cls
set /p question="Ask a question: "
docker compose exec rag-app python main.py query "!question!"
goto end

:list_docs
cls
docker compose exec rag-app python main.py list
goto end

:show_help
cls
echo.
echo ====== RAG-11 Help ======
echo.
echo QUICK START:
echo   rag.bat start          Start the app
echo   Open http://localhost:5000 in your browser
echo.
echo DOCUMENT MANAGEMENT:
echo   rag.bat ingest         Interactive ingest menu
echo   rag.bat list           List all documents
echo.
echo QUERYING:
echo   rag.bat query          Ask a question
echo.
echo TROUBLESHOOTING:
echo   rag.bat logs           View error logs
echo   rag.bat shell          Access container bash
echo.
echo For more details, see DEPLOYMENT.md
echo.
goto end

:end
endlocal
pause
