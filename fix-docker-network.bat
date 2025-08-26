@echo off
chcp 65001 >nul
title Trading Robot - Fix Docker Network Issues

echo.
echo ==========================================
echo     Docker Network Issue Troubleshooter
echo ==========================================
echo.

echo This script helps resolve common Docker network issues.
echo.

echo Checking Docker status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not running
    echo Please make sure Docker Desktop is installed and running
    pause
    exit /b 1
)

echo [OK] Docker is available
echo.

echo Available solutions:
echo.
echo 1. Restart Docker Desktop
echo 2. Clear Docker cache and restart
echo 3. Use local images (if available)
echo 4. Configure Docker registry mirror (for China users)
echo 5. Check network connectivity
echo 6. Exit
echo.

set /p choice="Select an option (1-6): "

if "%choice%"=="1" (
    echo.
    echo Restarting Docker Desktop...
    echo Please manually restart Docker Desktop from the system tray
    echo After restart, try running the startup script again
    pause
) else if "%choice%"=="2" (
    echo.
    echo Clearing Docker cache...
    docker system prune -f
    echo Docker cache cleared
    echo Please restart Docker Desktop and try again
    pause
) else if "%choice%"=="3" (
    echo.
    echo Checking for local images...
    docker images
    echo.
    echo If you see the required images above, you can try starting without --build flag
    pause
) else if "%choice%"=="4" (
    echo.
    echo To configure Docker registry mirror:
    echo 1. Open Docker Desktop
    echo 2. Go to Settings ^> Docker Engine
    echo 3. Add registry mirrors in the JSON configuration:
    echo.
    echo {
    echo   "registry-mirrors": [
    echo     "https://docker.mirrors.ustc.edu.cn",
    echo     "https://hub-mirror.c.163.com"
    echo   ]
    echo }
    echo.
    echo 4. Click "Apply & Restart"
    pause
) else if "%choice%"=="5" (
    echo.
    echo Testing network connectivity...
    ping -n 4 docker.io
    echo.
    echo Testing DNS resolution...
    nslookup docker.io
    pause
) else if "%choice%"=="6" (
    exit /b 0
) else (
    echo Invalid choice
    pause
)

echo.
echo Press any key to exit...
pause >nul
