@echo off
chcp 65001 >nul
title Trading Robot - Prepare Docker Images

echo.
echo ==========================================
echo     Trading Robot Image Preparation
echo ==========================================
echo.
echo This script pre-downloads all required Docker images
echo to ensure smooth startup for end users.
echo.

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not available
    pause
    exit /b 1
)

echo [OK] Docker is available
echo.

echo Downloading required Docker images...
echo This may take several minutes on first run.
echo.

echo 1/5 Downloading PostgreSQL...
echo Trying postgres:15...
docker pull postgres:15
if %errorlevel% neq 0 (
    echo [WARNING] postgres:15 failed, trying postgres:latest...
    docker pull postgres:latest
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download PostgreSQL image
        goto pull_failed
    )
)
echo [OK] PostgreSQL image ready

echo.
echo 2/5 Downloading Redis...
echo Trying redis:7...
docker pull redis:7
if %errorlevel% neq 0 (
    echo [WARNING] redis:7 failed, trying redis:latest...
    docker pull redis:latest
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download Redis image
        goto pull_failed
    )
)
echo [OK] Redis image ready

echo.
echo 3/5 Downloading Python...
echo Trying python:3.11...
docker pull python:3.11
if %errorlevel% neq 0 (
    echo [WARNING] python:3.11 failed, trying python:latest...
    docker pull python:latest
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download Python image
        goto pull_failed
    )
)
echo [OK] Python image ready

echo.
echo 4/5 Downloading Node.js...
echo Trying node:18...
docker pull node:18
if %errorlevel% neq 0 (
    echo [WARNING] node:18 failed, trying node:latest...
    docker pull node:latest
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download Node.js image
        goto pull_failed
    )
)
echo [OK] Node.js image ready

echo.
echo 5/5 Downloading Nginx...
echo Trying nginx:alpine...
docker pull nginx:alpine
if %errorlevel% neq 0 (
    echo [WARNING] nginx:alpine failed, trying nginx:latest...
    docker pull nginx:latest
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download Nginx image
        goto pull_failed
    )
)
echo [OK] Nginx image ready

echo.
echo ========================================
echo           Images Ready!
echo ========================================
echo.

echo All Docker images have been downloaded successfully.
echo You can now use any startup option without network delays.
echo.

echo Available images:
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo.
echo Recommended next steps:
echo 1. Run 'cmd /c menu.bat'
echo 2. Choose option 1 (Quick Start) or 4 (Reliable Start)
echo.

set /p start_now="Start Trading Robot now? (y/n): "
if /i "%start_now%"=="y" (
    echo.
    echo Starting Trading Robot...
    call start-reliable.bat
)

echo.
echo Press any key to exit...
pause >nul
goto end

:pull_failed
echo.
echo ========================================
echo           Download Failed
echo ========================================
echo.
echo Some images failed to download due to network issues.
echo.
echo Solutions:
echo 1. Check your internet connection
echo 2. Configure Docker registry mirrors (run setup-docker-mirror.bat)
echo 3. Try again later when network is more stable
echo 4. Use local development mode instead
echo.
pause

:end
