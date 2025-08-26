@echo off
chcp 65001 >nul
title Trading Robot - View Logs

echo.
echo ==========================================
echo     Trading Robot Log Viewer
echo ==========================================
echo.

echo Please select service logs to view:
echo.
echo 1. Backend Service (backend)
echo 2. Frontend Service (frontend)
echo 3. Database (postgres)
echo 4. Cache (redis)
echo 5. Task Queue (celery_worker)
echo 6. Scheduled Tasks (celery_beat)
echo 7. Proxy Service (nginx)
echo 8. All Services
echo 9. Live Logs (All Services)
echo.

set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" (
    docker-compose logs backend
) else if "%choice%"=="2" (
    docker-compose logs frontend
) else if "%choice%"=="3" (
    docker-compose logs postgres
) else if "%choice%"=="4" (
    docker-compose logs redis
) else if "%choice%"=="5" (
    docker-compose logs celery_worker
) else if "%choice%"=="6" (
    docker-compose logs celery_beat
) else if "%choice%"=="7" (
    docker-compose logs nginx
) else if "%choice%"=="8" (
    docker-compose logs
) else if "%choice%"=="9" (
    echo Press Ctrl+C to exit live log viewing
    docker-compose logs -f
) else (
    echo Invalid choice
)

echo.
echo Press any key to exit...
pause >nul
