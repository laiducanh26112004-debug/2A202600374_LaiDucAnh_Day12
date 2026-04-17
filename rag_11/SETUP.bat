@echo off
REM ============================================
REM RAG-11 COMPLETE SETUP & RUN SCRIPT
REM ============================================
REM This script guides you through:
REM   1. Docker setup
REM   2. Building the image
REM   3. Running the container
REM   4. Ingesting documents
REM   5. Testing the API

setlocal enabledelayedexpansion

cls
echo.
echo ========================================
echo   RAG-11 COMPLETE SETUP ASSISTANT
echo ========================================
echo.
echo This script will help you:
echo   1. Check Docker installation
echo   2. Build the Docker image
echo   3. Start the container
echo   4. Ingest documents
echo   5. Test the system
echo.
pause
cls

REM ============================================
REM Step 1: Check Docker
REM ============================================
echo [STEP 1] Checking Docker Installation...
echo.
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH!
    echo.
    echo Solution:
    echo   1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
    echo   2. Install and restart your computer
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)
docker --version
echo [OK] Docker found!
echo.
pause
cls

REM ============================================
REM Step 2: Check docker-compose.yml
REM ============================================
echo [STEP 2] Checking docker-compose.yml...
echo.
if not exist "docker-compose.yml" (
    echo ERROR: docker-compose.yml not found!
    echo.
    echo Make sure you're in the rag_11 directory:
    echo   cd D:\BAI_TAP\code\vinvuong\rag_11
    echo.
    pause
    exit /b 1
)
echo [OK] docker-compose.yml found!
echo.
pause
cls

REM ============================================
REM Step 3: Check .env file
REM ============================================
echo [STEP 3] Checking .env file...
echo.
if not exist ".env" (
    echo WARNING: .env file not found!
    echo.
    echo I'll create a template. You MUST edit it with your GROQ_API_KEY:
    echo   1. Get key from: https://console.groq.com/keys
    echo   2. Edit .env and paste your key
    echo   3. Save the file
    echo.
    copy ".env.example" ".env"
    echo Created .env from template. Please edit it!
    echo.
    pause
)
echo [OK] .env file ready!
echo.
pause
cls

REM ============================================
REM Step 4: Build Docker image
REM ============================================
echo [STEP 4] Building Docker Image...
echo.
echo This may take 5-10 minutes on first build.
echo It downloads Python, ML models, and dependencies.
echo.
docker build -t rag-11:latest .
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed!
    echo Check the error messages above.
    echo.
    pause
    exit /b 1
)
echo.
echo [OK] Image built successfully!
echo.
pause
cls

REM ============================================
REM Step 5: Start the container
REM ============================================
echo [STEP 5] Starting Docker Container...
echo.
docker compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start container!
    echo.
    echo Troubleshooting:
    echo   1. Port 5000 already in use?
    echo      docker compose down
    echo   2. Check logs:
    echo      docker compose logs
    echo.
    pause
    exit /b 1
)
echo.
echo [OK] Container started!
echo Waiting for Flask to initialize (10 seconds)...
timeout /t 10
echo.
pause
cls

REM ============================================
REM Step 6: Verify container is running
REM ============================================
echo [STEP 6] Verifying Container...
echo.
docker compose ps
echo.
pause
cls

REM ============================================
REM Step 7: Test health endpoint
REM ============================================
echo [STEP 7] Testing API Health Endpoint...
echo.
curl http://localhost:5000/api/health
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Health check failed!
    echo.
    echo Troubleshooting:
    echo   1. Container not ready yet. Wait 10 more seconds.
    echo   2. Check logs: docker compose logs -f
    echo   3. Check port: netstat -ano ^| findstr :5000
    echo.
)
echo.
pause
cls

REM ============================================
REM Step 8: Open browser
REM ============================================
echo [STEP 8] Opening Web UI...
echo.
echo I'll open http://localhost:5000 in your default browser.
echo.
start http://localhost:5000
timeout /t 3
cls

REM ============================================
REM Step 9: Document ingestion menu
REM ============================================
:ingest_menu
cls
echo [STEP 9] Ingest Documents
echo.
echo Your container is running at http://localhost:5000
echo.
echo What would you like to do?
echo.
echo   1. Ingest documents from a folder
echo   2. Test a query
echo   3. View all documents
echo   4. View live logs
echo   5. Stop the container
echo   6. Exit
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    cls
    echo.
    echo Where are your documents?
    echo Examples:
    echo   ./data
    echo   ./docs
    echo   C:\Users\You\Downloads\documents
    echo.
    set /p folder="Enter folder path: "
    echo.
    echo Ingesting documents...
    docker compose exec rag-app python main.py ingest-dir !folder! --recursive
    echo.
    echo [OK] Done!
    echo.
    pause
    goto ingest_menu
)

if "%choice%"=="2" (
    cls
    echo.
    set /p question="Ask a question: "
    echo.
    docker compose exec rag-app python main.py query "!question!"
    echo.
    pause
    goto ingest_menu
)

if "%choice%"=="3" (
    cls
    echo.
    docker compose exec rag-app python main.py list
    echo.
    pause
    goto ingest_menu
)

if "%choice%"=="4" (
    cls
    echo Showing live logs (Press Ctrl+C to stop)...
    echo.
    docker compose logs -f
    goto ingest_menu
)

if "%choice%"=="5" (
    cls
    echo.
    echo Stopping container...
    docker compose down
    echo [OK] Stopped!
    echo.
    pause
    goto done
)

if "%choice%"=="6" (
    goto done
)

echo Invalid choice!
pause
goto ingest_menu

REM ============================================
REM Done
REM ============================================
:done
cls
echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Your RAG-11 app is ready!
echo.
echo COMMANDS YOU CAN USE:
echo.
echo Start:       docker compose up -d
echo Stop:        docker compose down
echo Logs:        docker compose logs -f
echo Ingest:      docker compose exec rag-app python main.py ingest-dir ./data --recursive
echo Query:       docker compose exec rag-app python main.py query "Your question"
echo List docs:   docker compose exec rag-app python main.py list
echo.
echo WEB UI:      http://localhost:5000
echo API:         http://localhost:5000/api
echo.
echo For more help, see:
echo   - QUICKREF.md
echo   - DEPLOYMENT.md
echo   - RAILWAY.md (for cloud deployment)
echo.
pause
