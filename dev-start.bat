@echo off
chcp 65001 >nul
title Trading Robot - Development Mode

echo.
echo ==========================================
echo     Trading Robot Development Mode
echo ==========================================
echo.

:: Check Python and Node.js
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not installed, please install Python 3.11+
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not installed, please install Node.js 18+
    pause
    exit /b 1
)

echo [OK] Development environment check passed
echo.

:: Create configuration files
if not exist ".env" copy ".env.example" ".env" >nul 2>&1
if not exist "backend\monitoring.env" copy "backend\monitoring.env.example" "backend\monitoring.env" >nul 2>&1

echo Starting basic services (database, cache)...
docker-compose up -d postgres redis

echo Waiting for basic services to start...
timeout /t 10 /nobreak >nul

echo Initializing database...
cd backend
python scripts\init_database.py
cd ..

echo.
echo ========================================
echo     Development Service Instructions
echo ========================================
echo.
echo Basic services started:
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo.
echo Manual startup for development services:
echo.
echo Backend (new terminal):
echo   cd backend
echo   pip install -r requirements.txt
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Frontend (new terminal):
echo   cd frontend
echo   npm install
echo   npm run dev
echo.
echo Task Queue (new terminal):
echo   cd backend
echo   celery -A app.tasks.monitoring_tasks worker --loglevel=info
echo.

set /p auto_start="Auto start backend and frontend? (y/n): "
if /i "%auto_start%"=="y" (
    echo.
    echo Starting backend service...
    start "Backend" cmd /k "cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

    timeout /t 3 /nobreak >nul

    echo Starting frontend service...
    start "Frontend" cmd /k "cd frontend && npm install && npm run dev"

    echo.
    echo Development services starting...
    echo Please wait for services to fully start, then access:
    echo   Frontend: http://localhost:3000
    echo   API Docs: http://localhost:8000/docs
)

echo.
echo Press any key to exit...
pause >nul
