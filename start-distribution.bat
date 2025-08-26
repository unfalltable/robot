@echo off
chcp 65001 >nul
title Trading Robot - Distribution Start

echo.
echo ==========================================
echo     Trading Robot Distribution Start
echo ==========================================
echo.
echo This is the recommended startup method for end users.
echo.

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running or not installed.
    echo.
    echo Please:
    echo 1. Install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo 2. Make sure Docker Desktop is running
    echo 3. Try again
    echo.
    pause
    exit /b 1
)

echo [OK] Docker Desktop is available
echo.

:: Create environment files if they don't exist
if not exist ".env" (
    echo Creating environment configuration...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Environment file created from template
    ) else (
        echo DATABASE_URL=postgresql://postgres:password@postgres:5432/trading_robot > .env
        echo REDIS_URL=redis://:redis_password@redis:6379/0 >> .env
        echo SECRET_KEY=trading-robot-secret-key >> .env
        echo DEBUG=false >> .env
        echo [OK] Environment file created with defaults
    )
)

echo Starting Trading Robot services...
echo.

:: Clean up any existing containers
echo Cleaning up previous containers...
docker-compose down >nul 2>&1

echo Starting services step by step...
echo.

:: Start database and cache first
echo Step 1/4: Starting database and cache...
docker-compose up -d postgres redis
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start database services
    echo This might be due to:
    echo 1. Network connectivity issues
    echo 2. Port conflicts (5432, 6379 already in use)
    echo 3. Docker image download problems
    echo.
    echo Try running: docker-compose logs postgres redis
    pause
    exit /b 1
)

echo [OK] Database and cache started
echo Waiting for services to initialize...
timeout /t 20 /nobreak >nul

:: Start backend
echo.
echo Step 2/4: Starting backend API...
docker-compose up -d --build backend
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start backend service
    echo.
    echo This might be due to:
    echo 1. Python image download issues
    echo 2. Build process failures
    echo 3. Database connection problems
    echo.
    echo Try running: docker-compose logs backend
    pause
    exit /b 1
)

echo [OK] Backend started
echo Waiting for backend to initialize...
timeout /t 30 /nobreak >nul

:: Start task workers
echo.
echo Step 3/4: Starting task workers...
docker-compose up -d celery_worker celery_beat
echo [OK] Task workers started

:: Start frontend and proxy
echo.
echo Step 4/4: Starting frontend and proxy...
docker-compose up -d --build frontend nginx
if %errorlevel% neq 0 (
    echo [WARNING] Frontend or proxy startup issues
    echo Services may still be starting...
)

echo [OK] All services started

echo.
echo ========================================
echo           Startup Complete!
echo ========================================
echo.

:: Show container status
echo Container Status:
docker-compose ps

echo.
echo Access URLs:
echo   Frontend Application: http://localhost:3000
echo   API Documentation:    http://localhost:8000/docs
echo   Backend API:          http://localhost:8000
echo   Nginx Proxy:          http://localhost:80
echo.

echo Checking service health...
timeout /t 10 /nobreak >nul

:: Test backend health
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend service is healthy
) else (
    echo [INFO] Backend may still be starting up...
)

echo.
echo ========================================
echo     Trading Robot is Ready!
echo ========================================
echo.

set /p open_app="Open the application in browser? (y/n): "
if /i "%open_app%"=="y" (
    echo Opening application...
    start http://localhost:3000
    timeout /t 2 /nobreak >nul
    start http://localhost:8000/docs
)

echo.
echo Useful commands:
echo   View logs: docker-compose logs -f [service_name]
echo   Stop all:  docker-compose down
echo   Restart:   docker-compose restart [service_name]
echo.

echo Press any key to exit...
pause >nul
goto end

:pull_failed
echo.
echo [ERROR] Failed to download required Docker images.
echo.
echo This is usually due to network connectivity issues.
echo Please try:
echo 1. Check your internet connection
echo 2. Configure Docker registry mirrors
echo 3. Try again later
echo.
pause

:end
