@echo off
chcp 65001 >nul
title Trading Robot - Stop Reliable Services

echo.
echo ==========================================
echo     Trading Robot - Stop Services
echo ==========================================
echo.

echo Stopping all Trading Robot services...
echo.

:: Stop services using reliable configuration
docker-compose -f docker-compose.reliable.yml down

:: Also stop any services from other configurations
docker-compose down >nul 2>&1
docker-compose -f docker-compose.simple.yml down >nul 2>&1

echo.
echo [OK] All services stopped
echo.

echo Container status:
docker ps -a --filter "name=trading_robot"

echo.
set /p clean_data="Do you want to remove all data volumes? (This will delete all data) (y/n): "
if /i "%clean_data%"=="y" (
    echo.
    echo Removing data volumes...
    docker-compose -f docker-compose.reliable.yml down -v
    docker volume prune -f
    echo [OK] Data volumes removed
)

echo.
set /p clean_images="Do you want to remove Trading Robot images? (y/n): "
if /i "%clean_images%"=="y" (
    echo.
    echo Removing Trading Robot containers and images...
    docker container prune -f
    echo [OK] Containers cleaned
)

echo.
echo Press any key to exit...
pause >nul
