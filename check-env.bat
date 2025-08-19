@echo off
chcp 65001 >nul
title Trading Robot - 环境检查

echo.
echo ==========================================
echo     🔍 Trading Robot 环境检查
echo ==========================================
echo.

set all_good=1

:: 检查Docker
echo 📦 检查Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker已安装
    docker --version
) else (
    echo ❌ Docker未安装
    echo    下载地址: https://www.docker.com/products/docker-desktop
    set all_good=0
)

:: 检查Docker Compose
echo.
echo 📦 检查Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose可用
    docker-compose --version
) else (
    echo ❌ Docker Compose不可用
    set all_good=0
)

:: 检查Docker是否运行
echo.
echo 🔄 检查Docker服务状态...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker服务正在运行
) else (
    echo ❌ Docker服务未运行，请启动Docker Desktop
    set all_good=0
)

echo.
echo ==========================================
echo     🛠️ 开发环境检查 (可选)
echo ==========================================
echo.

:: 检查Python
echo 🐍 检查Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python已安装
    python --version
) else (
    echo ⚠️ Python未安装 (开发模式需要)
    echo    下载地址: https://www.python.org/downloads/
)

:: 检查Node.js
echo.
echo 📗 检查Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js已安装
    node --version
    npm --version
) else (
    echo ⚠️ Node.js未安装 (开发模式需要)
    echo    下载地址: https://nodejs.org/
)

:: 检查Git
echo.
echo 📚 检查Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git已安装
    git --version
) else (
    echo ⚠️ Git未安装 (可选)
    echo    下载地址: https://git-scm.com/downloads
)

echo.
echo ==========================================
echo     📊 系统资源检查
echo ==========================================
echo.

:: 检查内存
echo 💾 检查系统内存...
for /f "tokens=2 delims==" %%i in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do set total_memory=%%i
set /a memory_gb=%total_memory:~0,-9%
if %memory_gb% geq 8 (
    echo ✅ 系统内存: %memory_gb%GB (推荐8GB+)
) else (
    echo ⚠️ 系统内存: %memory_gb%GB (推荐8GB+)
)

:: 检查磁盘空间
echo.
echo 💿 检查磁盘空间...
for /f "tokens=3" %%i in ('dir /-c ^| find "bytes free"') do set free_space=%%i
set free_space=%free_space:,=%
set /a free_gb=%free_space:~0,-9%
if %free_gb% geq 20 (
    echo ✅ 可用磁盘空间: %free_gb%GB (推荐20GB+)
) else (
    echo ⚠️ 可用磁盘空间: %free_gb%GB (推荐20GB+)
)

echo.
echo ==========================================
echo     📋 检查结果
echo ==========================================
echo.

if %all_good% equ 1 (
    echo ✅ 环境检查通过！可以使用Docker模式启动
    echo.
    echo 🚀 推荐启动方式:
    echo    双击运行: quick-start.bat
    echo.
) else (
    echo ❌ 环境检查未通过，请安装缺失的软件
    echo.
    echo 📦 必需软件:
    echo    - Docker Desktop: https://www.docker.com/products/docker-desktop
    echo.
)

echo 🛠️ 开发模式需要额外安装:
echo    - Python 3.11+: https://www.python.org/downloads/
echo    - Node.js 18+: https://nodejs.org/
echo.

echo 按任意键退出...
pause >nul
