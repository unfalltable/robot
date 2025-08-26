@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    Trading Robot Full Start Script
echo ========================================
echo.

:: Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not running
    echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not available
    pause
    exit /b 1
)

echo [OK] Docker environment check passed
echo.

:: Check and create environment configuration files
if not exist ".env" (
    echo Creating environment configuration file...
    copy ".env.example" ".env" >nul
    echo [OK] Created .env file with default configuration
) else (
    echo [OK] Environment configuration file exists
)

if not exist "backend\monitoring.env" (
    echo Creating monitoring configuration file...
    copy "backend\monitoring.env.example" "backend\monitoring.env" >nul
    echo [OK] Created monitoring configuration file
)

echo.
echo Starting services...
echo.

:: Stop any existing containers
echo Cleaning up old containers...
docker-compose down >nul 2>&1

:: Build and start basic services
echo Starting database and cache services...
docker-compose up -d postgres redis
if %errorlevel% neq 0 (
    echo [ERROR] Basic services startup failed
    pause
    exit /b 1
)

:: Wait for database to start
echo Waiting for database to start (15 seconds)...
timeout /t 15 /nobreak >nul

:: Build and start backend service
echo Building and starting backend service...
docker-compose up -d --build backend
if %errorlevel% neq 0 (
    echo [ERROR] Backend service startup failed
    pause
    exit /b 1
)

:: Wait for backend to start
echo Waiting for backend service to start (10 seconds)...
timeout /t 10 /nobreak >nul

:: Run database initialization
echo Initializing database...
docker-compose exec -T backend python scripts/init_database.py
if %errorlevel% neq 0 (
    echo [WARNING] Database initialization may have failed, but continuing with other services...
)

:: Start task queue
echo Starting task queue services...
docker-compose up -d celery_worker celery_beat

:: Build and start frontend
echo Building and starting frontend service...
docker-compose up -d --build frontend

:: Start proxy service
echo Starting Nginx proxy...
docker-compose up -d nginx

:: Start monitoring services (optional)
echo Starting monitoring services...
docker-compose up -d prometheus grafana

echo.
echo ========================================
echo           Startup Complete!
echo ========================================
echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Monitor:  http://localhost:3001 (admin/admin123)
echo.
echo Common Commands:
echo   Check status: docker-compose ps
echo   View logs: docker-compose logs -f backend
echo   Stop services: docker-compose down
echo.

:: Check service health status
echo Checking service status...
timeout /t 5 /nobreak >nul

:: Check backend health status
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend service is running normally
) else (
    echo [WARNING] Backend service may still be starting...
)

:: Display container status
echo.
echo Container Status:
docker-compose ps

echo.
echo Tips:
echo   - First startup may take several minutes to download images
echo   - If services are not accessible, please wait 1-2 minutes and retry
echo   - For troubleshooting, run: docker-compose logs -f [service_name]
echo.

:: Ask whether to open browser
set /p open_browser="Open browser automatically? (y/n): "
if /i "%open_browser%"=="y" (
    echo Opening browser...
    start http://localhost:3000
    start http://localhost:8000/docs
)

echo.
echo Press any key to exit...
pause >nul
