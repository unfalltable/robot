@echo off
chcp 65001 >nul
title Trading Robot - 开发模式启动

echo.
echo ==========================================
echo     🛠️ Trading Robot 开发模式启动
echo ==========================================
echo.

:: 检查Python和Node.js
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装，请先安装Python 3.11+
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装，请先安装Node.js 18+
    pause
    exit /b 1
)

echo ✅ 开发环境检查通过
echo.

:: 创建配置文件
if not exist ".env" copy ".env.example" ".env" >nul 2>&1
if not exist "backend\monitoring.env" copy "backend\monitoring.env.example" "backend\monitoring.env" >nul 2>&1

echo 🚀 启动基础服务 (数据库、缓存)...
docker-compose up -d postgres redis

echo ⏳ 等待基础服务启动...
timeout /t 10 /nobreak >nul

echo 🗄️ 初始化数据库...
cd backend
python scripts\init_database.py
cd ..

echo.
echo ========================================
echo     开发服务启动说明
echo ========================================
echo.
echo 📋 基础服务已启动:
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo.
echo 🛠️ 手动启动开发服务:
echo.
echo 后端 (新终端):
echo   cd backend
echo   pip install -r requirements.txt
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 前端 (新终端):
echo   cd frontend
echo   npm install
echo   npm run dev
echo.
echo 任务队列 (新终端):
echo   cd backend
echo   celery -A app.tasks.monitoring_tasks worker --loglevel=info
echo.

set /p auto_start="是否自动启动后端和前端? (y/n): "
if /i "%auto_start%"=="y" (
    echo.
    echo 🚀 启动后端服务...
    start "Backend" cmd /k "cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    timeout /t 3 /nobreak >nul
    
    echo 🚀 启动前端服务...
    start "Frontend" cmd /k "cd frontend && npm install && npm run dev"
    
    echo.
    echo ✅ 开发服务启动中...
    echo 请等待服务完全启动后访问:
    echo   前端: http://localhost:3000
    echo   API:  http://localhost:8000/docs
)

echo.
echo 按任意键退出...
pause >nul
