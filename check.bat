@echo off
title Trading Robot - Status Check

echo.
echo ==========================================
echo     Trading Robot - Status Check
echo ==========================================
echo.

echo Container Status:
docker-compose ps

echo.
echo Health Check:
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend: OK
) else (
    echo Backend: Not Ready
)

curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo Frontend: OK
) else (
    echo Frontend: Not Ready
)

echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Monitor:  http://localhost:3001
echo.

echo Press any key to exit...
pause >nul
