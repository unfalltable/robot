@echo off
chcp 65001 >nul
title Trading Robot - 快速启动

echo.
echo ==========================================
echo     🚀 Trading Robot 快速启动
echo ==========================================
echo.

:: 快速检查Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

:: 创建必要的配置文件
if not exist ".env" copy ".env.example" ".env" >nul 2>&1
if not exist "backend\monitoring.env" copy "backend\monitoring.env.example" "backend\monitoring.env" >nul 2>&1

echo 🚀 正在启动所有服务...
echo.

:: 一键启动所有服务
docker-compose up -d --build

echo.
echo ⏳ 等待服务启动完成...
timeout /t 20 /nobreak >nul

:: 初始化数据库
echo 🗄️ 初始化数据库...
docker-compose exec -T backend python scripts/init_database.py >nul 2>&1

echo.
echo ========================================
echo           ✅ 启动完成！
echo ========================================
echo.
echo 🌐 访问地址:
echo   前端: http://localhost:3000
echo   API:  http://localhost:8000/docs
echo   监控: http://localhost:3001
echo.

:: 自动打开浏览器
start http://localhost:3000

echo 按任意键退出...
pause >nul
