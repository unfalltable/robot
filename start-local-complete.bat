@echo off
chcp 65001 >nul
title Trading Robot - Complete Local Setup

echo.
echo ==========================================
echo     Trading Robot Complete Local Setup
echo ==========================================
echo.
echo This will set up the trading robot to run completely locally
echo without Docker dependencies.
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

:: Create local environment configuration
echo Creating local environment configuration...

if not exist ".env.local" (
    echo # Local Development Configuration > .env.local
    echo DATABASE_URL=sqlite:///./trading_robot.db >> .env.local
    echo REDIS_URL=redis://localhost:6379/0 >> .env.local
    echo SECRET_KEY=local-development-secret-key >> .env.local
    echo DEBUG=true >> .env.local
    echo LOG_LEVEL=DEBUG >> .env.local
    echo ENVIRONMENT=local >> .env.local
    echo [OK] Created .env.local file
) else (
    echo [OK] .env.local file already exists
)

:: Copy to .env if it doesn't exist
if not exist ".env" (
    copy ".env.local" ".env" >nul
    echo [OK] Created .env file from local configuration
)

echo.
echo Setting up backend...

:: Install backend dependencies
echo Installing Python dependencies...
cd backend
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy sqlite3 redis celery python-multipart jinja2 aiofiles

:: Create a simple database initialization script for SQLite
echo Creating local database initialization...
if not exist "init_local_db.py" (
    echo import sqlite3 > init_local_db.py
    echo import os >> init_local_db.py
    echo. >> init_local_db.py
    echo # Create SQLite database >> init_local_db.py
    echo conn = sqlite3.connect('trading_robot.db'^) >> init_local_db.py
    echo cursor = conn.cursor(^) >> init_local_db.py
    echo. >> init_local_db.py
    echo # Create basic tables >> init_local_db.py
    echo cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT^)''''^) >> init_local_db.py
    echo cursor.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, symbol TEXT, price REAL, quantity REAL, timestamp DATETIME^)''''^) >> init_local_db.py
    echo. >> init_local_db.py
    echo conn.commit(^) >> init_local_db.py
    echo conn.close(^) >> init_local_db.py
    echo print("Local database initialized successfully!"^) >> init_local_db.py
)

:: Initialize local database
echo Initializing local SQLite database...
python init_local_db.py

cd ..

echo.
echo Setting up frontend...
cd frontend

:: Check if package.json exists
if not exist "package.json" (
    echo [WARNING] package.json not found in frontend directory
    echo Creating basic Next.js setup...
    npm init -y
    npm install next react react-dom
) else (
    echo Installing frontend dependencies...
    npm install
)

cd ..

echo.
echo ========================================
echo           Setup Complete!
echo ========================================
echo.
echo Local development environment is ready!
echo.
echo To start the services:
echo.
echo 1. Backend (in one terminal):
echo    cd backend
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 2. Frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.

set /p auto_start="Auto start backend and frontend now? (y/n): "
if /i "%auto_start%"=="y" (
    echo.
    echo Starting backend server...
    start "Trading Robot Backend" cmd /k "cd backend && echo Starting backend server... && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    timeout /t 3 /nobreak >nul
    
    echo Starting frontend server...
    start "Trading Robot Frontend" cmd /k "cd frontend && echo Starting frontend server... && npm run dev"
    
    echo.
    echo [OK] Services are starting!
    echo.
    echo Access URLs:
    echo   Backend API: http://localhost:8000
    echo   API Docs: http://localhost:8000/docs
    echo   Frontend: http://localhost:3000
    echo.
    echo Note: It may take a few moments for the services to fully start.
)

echo.
echo Press any key to exit...
pause >nul
