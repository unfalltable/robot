@echo off
chcp 65001 >nul
title Trading Robot - Start with Mirror

echo.
echo ==========================================
echo     Trading Robot Start with Mirrors
echo ==========================================
echo.

echo This script tries to start services using different image sources.
echo.

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not available
    pause
    exit /b 1
)

:: Create config files
if not exist ".env" copy ".env.example" ".env" >nul 2>&1
if not exist "backend\monitoring.env" copy "backend\monitoring.env.example" "backend\monitoring.env" >nul 2>&1

echo Step 1: Trying to pull images manually with timeout...
echo.

echo Pulling Redis image...
timeout 30 docker pull redis:7-alpine
if %errorlevel% neq 0 (
    echo [WARNING] Redis pull failed, trying alternative...
    timeout 30 docker pull redis:latest
)

echo.
echo Pulling PostgreSQL image...
timeout 30 docker pull postgres:15-alpine
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL pull failed, trying alternative...
    timeout 30 docker pull postgres:latest
)

echo.
echo Pulling Python image...
timeout 30 docker pull python:3.11-slim
if %errorlevel% neq 0 (
    echo [WARNING] Python pull failed, trying alternative...
    timeout 30 docker pull python:3.11
    if %errorlevel% neq 0 (
        echo [ERROR] Cannot pull Python image
        echo.
        echo Solutions:
        echo 1. Configure Docker registry mirror (run setup-docker-mirror.bat)
        echo 2. Use local development mode (option 8 in main menu)
        echo 3. Check your internet connection
        pause
        exit /b 1
    )
)

echo.
echo [OK] Images pulled successfully
echo.

echo Step 2: Starting services...
docker-compose down >nul 2>&1
docker-compose up -d postgres redis

echo Waiting for database...
timeout /t 15 /nobreak >nul

echo Starting backend...
docker-compose up -d --build backend

echo Starting other services...
docker-compose up -d celery_worker frontend nginx

echo.
echo ========================================
echo           Startup Complete!
echo ========================================
echo.

echo Checking service status...
timeout /t 5 /nobreak >nul
docker-compose ps

echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Monitor:  http://localhost:3001
echo.

set /p open_browser="Open browser? (y/n): "
if /i "%open_browser%"=="y" (
    start http://localhost:3000
)

echo.
echo Press any key to exit...
pause >nul
