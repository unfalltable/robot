@echo off
chcp 65001 >nul
title Trading Robot - Simple Start

echo.
echo ==========================================
echo     Trading Robot Simple Start
echo ==========================================
echo.
echo This uses simplified Docker configuration to avoid network issues.
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

echo Starting basic services with simple configuration...
echo.

:: Use simple docker-compose file
docker-compose -f docker-compose.simple.yml down >nul 2>&1
docker-compose -f docker-compose.simple.yml up -d postgres redis

echo Waiting for database to start...
timeout /t 10 /nobreak >nul

echo Starting backend container...
docker-compose -f docker-compose.simple.yml up -d backend

echo.
echo Services started with simple configuration.
echo.
echo To complete the setup, you need to:
echo.
echo 1. Install backend dependencies:
echo    docker exec -it trading_robot_backend pip install -r requirements.txt
echo.
echo 2. Initialize database:
echo    docker exec -it trading_robot_backend python scripts/init_database.py
echo.
echo 3. Start backend server:
echo    docker exec -it trading_robot_backend uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 4. Start frontend locally:
echo    cd frontend
echo    npm install
echo    npm run dev
echo.

set /p auto_setup="Run automatic setup? (y/n): "
if /i "%auto_setup%"=="y" (
    echo.
    echo Running automatic setup...
    
    echo Installing backend dependencies...
    docker exec trading_robot_backend pip install -r requirements.txt
    
    echo Initializing database...
    docker exec trading_robot_backend python scripts/init_database.py
    
    echo Starting backend server in background...
    start "Backend Server" docker exec -it trading_robot_backend uvicorn app.main:app --host 0.0.0.0 --port 8000
    
    echo Starting frontend...
    start "Frontend" cmd /k "cd frontend && npm install && npm run dev"
    
    echo.
    echo [OK] Setup complete!
    echo Backend: http://localhost:8000
    echo Frontend: http://localhost:3000
)

echo.
echo Press any key to exit...
pause >nul
