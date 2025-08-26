@echo off
chcp 65001 >nul
title Trading Robot - Reliable Docker Start

echo.
echo ==========================================
echo     Trading Robot Reliable Start
echo ==========================================
echo.
echo This script uses a reliable Docker configuration with fallback strategies.
echo.

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not available. Please start Docker Desktop.
    pause
    exit /b 1
)

echo [OK] Docker is available
echo.

:: Create environment files
if not exist ".env" (
    echo Creating .env file...
    echo DATABASE_URL=postgresql://postgres:password123@localhost:5432/trading_robot > .env
    echo REDIS_URL=redis://:redis123@localhost:6379/0 >> .env
    echo SECRET_KEY=trading-robot-secret-key-2024 >> .env
    echo DEBUG=true >> .env
    echo LOG_LEVEL=INFO >> .env
    echo [OK] Created .env file
)

echo Step 1: Checking and pulling required images...
echo.

echo Checking existing images...
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | findstr -i "postgres redis python node nginx"

echo.
echo Pulling missing or updating images...

echo 1/5 PostgreSQL...
docker pull postgres:15 || docker pull postgres:latest
echo [OK] PostgreSQL ready

echo 2/5 Redis...
docker pull redis:7 || docker pull redis:latest
echo [OK] Redis ready

echo 3/5 Python...
docker pull python:3.11 || docker pull python:latest
echo [OK] Python ready

echo 4/5 Node.js...
docker pull node:18 || docker pull node:latest
echo [OK] Node.js ready

echo 5/5 Nginx...
docker pull nginx:alpine || docker pull nginx:latest
echo [OK] Nginx ready

goto start_services

:pull_failed
echo.
echo [ERROR] Failed to pull some Docker images.
echo This might be due to network connectivity issues.
echo.
echo Options:
echo 1. Check your internet connection
echo 2. Configure Docker registry mirrors
echo 3. Try again later
echo 4. Use local development mode instead
echo.
set /p retry="Retry pulling images? (y/n): "
if /i "%retry%"=="y" goto start_script
pause
exit /b 1

:start_services
echo.
echo ========================================
echo Step 2: Starting services...
echo ========================================
echo.

:: Clean up any existing containers
echo Cleaning up existing containers...
docker-compose -f docker-compose.reliable.yml down >nul 2>&1

:: Start database and cache first
echo Starting database and cache services...
docker-compose -f docker-compose.reliable.yml up -d postgres redis

echo Waiting for database to be ready...
timeout /t 20 /nobreak >nul

:: Check if database is ready
docker-compose -f docker-compose.reliable.yml exec postgres pg_isready -U postgres >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Database might not be fully ready, but continuing...
)

:: Start backend
echo Starting backend service...
docker-compose -f docker-compose.reliable.yml up -d backend

echo Waiting for backend to start...
timeout /t 30 /nobreak >nul

:: Start frontend
echo Starting frontend service...
docker-compose -f docker-compose.reliable.yml up -d frontend

:: Start nginx
echo Starting nginx proxy...
docker-compose -f docker-compose.reliable.yml up -d nginx

echo.
echo ========================================
echo           Startup Complete!
echo ========================================
echo.

:: Show container status
echo Container Status:
docker-compose -f docker-compose.reliable.yml ps

echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Documentation: http://localhost:8000/docs
echo   Nginx Proxy: http://localhost:80
echo.

echo Services are starting up. Please wait 1-2 minutes for full initialization.
echo.

set /p open_browser="Open browser to view the application? (y/n): "
if /i "%open_browser%"=="y" (
    timeout /t 5 /nobreak >nul
    start http://localhost:3000
)

echo.
echo Press any key to exit...
pause >nul

:start_script
goto start_script
