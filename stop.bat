@echo off
title Trading Robot - Stop Services

echo.
echo ==========================================
echo     Trading Robot - Stop Services
echo ==========================================
echo.

echo Stopping all services...
docker-compose down

echo.
echo All services stopped
echo.

echo Do you want to clean data volumes? (This will delete all data)
set /p clean_volumes="Enter y to clean data, any other key to skip: "
if /i "%clean_volumes%"=="y" (
    echo Cleaning data volumes...
    docker-compose down -v
    echo Data cleaned
)

echo.
echo Press any key to exit...
pause >nul
