@echo off
chcp 65001 >nul
title Setup Docker Registry Mirror

echo.
echo ==========================================
echo     Docker Registry Mirror Setup
echo ==========================================
echo.

echo This will help configure Docker to use faster registry mirrors.
echo.

echo Step 1: Open Docker Desktop
echo Step 2: Click on Settings (gear icon)
echo Step 3: Go to "Docker Engine" section
echo Step 4: Replace the JSON configuration with:
echo.

echo {
echo   "builder": {
echo     "gc": {
echo       "defaultKeepStorage": "20GB",
echo       "enabled": true
echo     }
echo   },
echo   "experimental": false,
echo   "registry-mirrors": [
echo     "https://docker.mirrors.ustc.edu.cn",
echo     "https://hub-mirror.c.163.com",
echo     "https://mirror.baidubce.com"
echo   ]
echo }
echo.

echo Step 5: Click "Apply & Restart"
echo Step 6: Wait for Docker to restart
echo Step 7: Try running the startup script again
echo.

set /p open_docker="Open Docker Desktop settings now? (y/n): "
if /i "%open_docker%"=="y" (
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Docker Desktop is opening...
    echo Please follow the steps above to configure registry mirrors.
)

echo.
echo Press any key to continue...
pause >nul
