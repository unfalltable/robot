@echo off
chcp 65001 >nul
title Trading Robot - Quick Start

echo.
echo ==========================================
echo     Trading Robot Quick Start
echo ==========================================
echo.

:: Quick Docker check
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not installed, please install Docker Desktop first
    pause
    exit /b 1
)

:: Create necessary configuration files
if not exist ".env" copy ".env.example" ".env" >nul 2>&1
if not exist "backend\monitoring.env" copy "backend\monitoring.env.example" "backend\monitoring.env" >nul 2>&1

echo Starting all services...
echo.

:: One-click start all services
docker-compose up -d --build

echo.
echo Waiting for services to start...
timeout /t 20 /nobreak >nul

:: Initialize database
echo Initializing database...
docker-compose exec -T backend python scripts/init_database.py >nul 2>&1

echo.
echo ========================================
echo           Startup Complete!
echo ========================================
echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Monitor:  http://localhost:3001
echo.

:: Auto open browser
start http://localhost:3000

echo Press any key to exit...
pause >nul
