@echo off
chcp 65001 >nul
title Trading Robot - 服务状态

echo.
echo ==========================================
echo     📊 Trading Robot 服务状态
echo ==========================================
echo.

echo 📋 容器状态:
docker-compose ps

echo.
echo 🔍 健康检查:
curl -s http://localhost:8000/health 2>nul
if %errorlevel% equ 0 (
    echo ✅ 后端服务正常
) else (
    echo ❌ 后端服务异常
)

curl -s http://localhost:3000 2>nul
if %errorlevel% equ 0 (
    echo ✅ 前端服务正常
) else (
    echo ❌ 前端服务异常
)

echo.
echo 📊 资源使用:
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo.
echo 🌐 访问地址:
echo   前端: http://localhost:3000
echo   API:  http://localhost:8000/docs
echo   监控: http://localhost:3001
echo.

echo 按任意键退出...
pause >nul
