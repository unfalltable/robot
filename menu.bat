@echo off
chcp 65001 >nul
title Trading Robot Control Panel

:menu
cls
echo.
echo ==========================================
echo     Trading Robot Control Panel
echo ==========================================
echo.
echo Please select an option:
echo.
echo === RECOMMENDED FOR END USERS ===
echo 1. Start Trading Robot (Recommended)
echo 2. Prepare Images First (Slow Network)
echo.
echo === ADVANCED OPTIONS ===
echo 3. Quick Start (Original)
echo 4. Full Start (Detailed Process)
echo 5. Development Mode
echo.
echo === MONITORING ===
echo 6. Check Service Status
echo 7. View Logs
echo 8. Stop Services
echo 9. Open Web Pages
echo.
echo === TROUBLESHOOTING ===
echo 10. Local Development (No Docker)
echo 11. Setup Docker Mirror
echo 12. Fix Docker Network Issues
echo.
echo 13. Help
echo 14. Exit
echo.

set /p choice="Enter your choice (1-14): "

if "%choice%"=="1" (
    call start-distribution.bat
    goto menu
) else if "%choice%"=="2" (
    call prepare-images.bat
    goto menu
) else if "%choice%"=="3" (
    call quick-start.bat
    goto menu
) else if "%choice%"=="4" (
    call start.bat
    goto menu
) else if "%choice%"=="5" (
    call dev-start.bat
    goto menu
) else if "%choice%"=="6" (
    call status.bat
    goto menu
) else if "%choice%"=="7" (
    call logs.bat
    goto menu
) else if "%choice%"=="8" (
    call stop.bat
    goto menu
) else if "%choice%"=="9" (
    echo Opening web pages...
    start http://localhost:3000
    start http://localhost:8000/docs
    start http://localhost:3001
    goto menu
) else if "%choice%"=="10" (
    call start-local.bat
    goto menu
) else if "%choice%"=="11" (
    call setup-docker-mirror.bat
    goto menu
) else if "%choice%"=="12" (
    call fix-docker-network.bat
    goto menu
) else if "%choice%"=="13" (
    goto help
) else if "%choice%"=="14" (
    exit /b 0
) else (
    echo Invalid choice, please try again
    timeout /t 2 /nobreak >nul
    goto menu
)

:help
cls
echo.
echo ==========================================
echo     Trading Robot Help Guide
echo ==========================================
echo.
echo Startup Options:
echo   - Quick Start: One-click start all services, suitable for daily use
echo   - Full Start: Show detailed startup process, suitable for first use
echo   - Development Mode: Start basic services, manually start apps, suitable for development
echo.
echo Access URLs:
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:8000/docs
echo   - Monitor:  http://localhost:3001 (admin/admin123)
echo.
echo Common Commands:
echo   - Check status: docker-compose ps
echo   - View logs: docker-compose logs -f [service_name]
echo   - Restart service: docker-compose restart [service_name]
echo   - Stop services: docker-compose down
echo.
echo Service Description:
echo   - backend: Backend API service
echo   - frontend: Frontend interface
echo   - postgres: Database
echo   - redis: Cache and message queue
echo   - celery_worker: Background task processing
echo   - nginx: Reverse proxy
echo   - prometheus: Monitoring data collection
echo   - grafana: Monitoring dashboard
echo.
echo Troubleshooting:
echo   1. Port occupied: Modify port mapping in docker-compose.yml
echo   2. Service startup failed: Check logs docker-compose logs [service_name]
echo   3. Database connection failed: Restart database docker-compose restart postgres
echo   4. Insufficient memory: Close unnecessary services or increase system memory
echo.
echo Get Support:
echo   - Check README.md file
echo   - Check project documentation
echo   - Submit GitHub Issue
echo.

echo Press any key to return to main menu...
pause >nul
goto menu
