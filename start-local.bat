@echo off
chcp 65001 >nul
title Trading Robot - Local Development Start

echo.
echo ==========================================
echo     Trading Robot Local Development
echo ==========================================
echo.
echo This script starts the application in local development mode
echo without Docker, useful when Docker has network issues.
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python and Node.js are available
echo.

:: Create environment file
if not exist ".env" (
    echo Creating .env file...
    copy ".env.example" ".env" >nul 2>&1
    echo [OK] Created .env file
)

echo Starting local development environment...
echo.

echo Instructions for manual setup:
echo.
echo 1. Database Setup (choose one):
echo    a) Install PostgreSQL locally and create database 'trading_robot'
echo    b) Use SQLite (modify DATABASE_URL in .env to use sqlite:///./trading_robot.db)
echo.
echo 2. Backend Setup:
echo    Open new terminal and run:
echo    cd backend
echo    pip install -r requirements.txt
echo    python scripts/init_database.py
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 3. Frontend Setup:
echo    Open new terminal and run:
echo    cd frontend
echo    npm install
echo    npm run dev
echo.

set /p auto_start="Auto start backend and frontend? (y/n): "
if /i "%auto_start%"=="y" (
    echo.
    echo Starting backend...
    start "Trading Robot Backend" cmd /k "cd backend && pip install -r requirements.txt && python scripts/init_database.py && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    timeout /t 3 /nobreak >nul
    
    echo Starting frontend...
    start "Trading Robot Frontend" cmd /k "cd frontend && npm install && npm run dev"
    
    echo.
    echo Services are starting...
    echo Backend will be available at: http://localhost:8000
    echo Frontend will be available at: http://localhost:3000
    echo API docs will be available at: http://localhost:8000/docs
)

echo.
echo Press any key to exit...
pause >nul
