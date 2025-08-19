@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🚀 Trading Robot 一键启动脚本
echo ========================================
echo.

:: 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: Docker未安装或未启动
    echo 请先安装Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: 检查Docker Compose是否可用
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: Docker Compose不可用
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过
echo.

:: 检查并创建环境配置文件
if not exist ".env" (
    echo 📝 创建环境配置文件...
    copy ".env.example" ".env" >nul
    echo ✅ 已创建 .env 文件，使用默认配置
) else (
    echo ✅ 环境配置文件已存在
)

if not exist "backend\monitoring.env" (
    echo 📝 创建监控配置文件...
    copy "backend\monitoring.env.example" "backend\monitoring.env" >nul
    echo ✅ 已创建监控配置文件
)

echo.
echo 🚀 开始启动服务...
echo.

:: 停止可能存在的旧容器
echo 🧹 清理旧容器...
docker-compose down >nul 2>&1

:: 构建并启动基础服务
echo 📦 启动数据库和缓存服务...
docker-compose up -d postgres redis
if %errorlevel% neq 0 (
    echo ❌ 基础服务启动失败
    pause
    exit /b 1
)

:: 等待数据库启动
echo ⏳ 等待数据库启动 (15秒)...
timeout /t 15 /nobreak >nul

:: 构建并启动后端服务
echo 🔧 构建并启动后端服务...
docker-compose up -d --build backend
if %errorlevel% neq 0 (
    echo ❌ 后端服务启动失败
    pause
    exit /b 1
)

:: 等待后端启动
echo ⏳ 等待后端服务启动 (10秒)...
timeout /t 10 /nobreak >nul

:: 运行数据库初始化
echo 🗄️ 初始化数据库...
docker-compose exec -T backend python scripts/init_database.py
if %errorlevel% neq 0 (
    echo ⚠️ 数据库初始化可能失败，但继续启动其他服务...
)

:: 启动任务队列
echo 📋 启动任务队列服务...
docker-compose up -d celery_worker celery_beat

:: 构建并启动前端
echo 🎨 构建并启动前端服务...
docker-compose up -d --build frontend

:: 启动代理服务
echo 🌐 启动Nginx代理...
docker-compose up -d nginx

:: 启动监控服务（可选）
echo 📊 启动监控服务...
docker-compose up -d prometheus grafana

echo.
echo ========================================
echo           🎉 启动完成！
echo ========================================
echo.
echo 📱 访问地址:
echo   前端界面: http://localhost:3000
echo   API文档:  http://localhost:8000/docs
echo   监控面板: http://localhost:3001 (admin/admin123)
echo.
echo 📋 常用命令:
echo   查看状态: docker-compose ps
echo   查看日志: docker-compose logs -f backend
echo   停止服务: docker-compose down
echo.

:: 检查服务健康状态
echo 🔍 检查服务状态...
timeout /t 5 /nobreak >nul

:: 检查后端健康状态
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端服务运行正常
) else (
    echo ⚠️ 后端服务可能还在启动中...
)

:: 显示容器状态
echo.
echo 📊 容器状态:
docker-compose ps

echo.
echo 🎯 提示: 
echo   - 首次启动可能需要几分钟下载镜像
echo   - 如果服务无法访问，请等待1-2分钟后重试
echo   - 遇到问题可以运行: docker-compose logs -f [服务名]
echo.

:: 询问是否打开浏览器
set /p open_browser="是否自动打开浏览器? (y/n): "
if /i "%open_browser%"=="y" (
    echo 🌐 正在打开浏览器...
    start http://localhost:3000
    start http://localhost:8000/docs
)

echo.
echo 按任意键退出...
pause >nul
