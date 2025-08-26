@echo off
chcp 65001 >nul
title Trading Robot - Service Status

echo.
echo ==========================================
echo     Trading Robot Service Status
echo ==========================================
echo.

echo Container Status:
docker-compose ps

echo.
echo Health Check:
curl -s http://localhost:8000/health 2>nul
if %errorlevel% equ 0 (
    echo [OK] Backend service is running
) else (
    echo [ERROR] Backend service is down
)

curl -s http://localhost:3000 2>nul
if %errorlevel% equ 0 (
    echo [OK] Frontend service is running
) else (
    echo [ERROR] Frontend service is down
)

echo.
echo Resource Usage:
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Monitor:  http://localhost:3001
echo.

echo Press any key to exit...
pause >nul
