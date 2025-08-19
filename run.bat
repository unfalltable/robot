@echo off
title Trading Robot Launcher

echo.
echo ==========================================
echo     Trading Robot Launcher
echo ==========================================
echo.

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not found
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Docker found - OK
echo.

:: Create config files if not exist
if not exist ".env" (
    echo Creating .env file...
    copy ".env.example" ".env" >nul 2>&1
)

if not exist "backend\monitoring.env" (
    echo Creating monitoring config...
    copy "backend\monitoring.env.example" "backend\monitoring.env" >nul 2>&1
)

echo Starting all services...
echo This may take a few minutes on first run...
echo.

:: Start all services
docker-compose up -d --build

echo.
echo Waiting for services to start...
timeout /t 20 /nobreak >nul

:: Initialize database
echo Initializing database...
docker-compose exec -T backend python scripts/init_database.py >nul 2>&1

echo.
echo ==========================================
echo     Startup Complete!
echo ==========================================
echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Monitor:  http://localhost:3001
echo.
echo Opening browser...
start http://localhost:3000

echo.
echo Press any key to exit...
pause >nul
