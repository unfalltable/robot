@echo off
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
echo 1. Quick Start (Recommended)
echo 2. Full Start (Detailed Process)
echo 3. Development Mode
echo 4. Check Service Status
echo 5. View Logs
echo 6. Stop Services
echo 7. Open Web Pages
echo 8. Help
echo 9. Exit
echo.

set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" (
    call quick-start.bat
    goto menu
) else if "%choice%"=="2" (
    call start.bat
    goto menu
) else if "%choice%"=="3" (
    call dev-start.bat
    goto menu
) else if "%choice%"=="4" (
    call status.bat
    goto menu
) else if "%choice%"=="5" (
    call logs.bat
    goto menu
) else if "%choice%"=="6" (
    call stop.bat
    goto menu
) else if "%choice%"=="7" (
    echo Opening web pages...
    start http://localhost:3000
    start http://localhost:8000/docs
    start http://localhost:3001
    goto menu
) else if "%choice%"=="8" (
    goto help
) else if "%choice%"=="9" (
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
echo     📚 Trading Robot 使用帮助
echo ==========================================
echo.
echo 🚀 启动方式:
echo   - 快速启动: 一键启动所有服务，适合日常使用
echo   - 完整启动: 显示详细启动过程，适合首次使用
echo   - 开发模式: 启动基础服务，手动启动应用，适合开发
echo.
echo 📱 访问地址:
echo   - 前端界面: http://localhost:3000
echo   - API文档:  http://localhost:8000/docs
echo   - 监控面板: http://localhost:3001 (admin/admin123)
echo.
echo 🔧 常用命令:
echo   - 查看状态: docker-compose ps
echo   - 查看日志: docker-compose logs -f [服务名]
echo   - 重启服务: docker-compose restart [服务名]
echo   - 停止服务: docker-compose down
echo.
echo 📋 服务说明:
echo   - backend: 后端API服务
echo   - frontend: 前端界面
echo   - postgres: 数据库
echo   - redis: 缓存和消息队列
echo   - celery_worker: 后台任务处理
echo   - nginx: 反向代理
echo   - prometheus: 监控数据收集
echo   - grafana: 监控面板
echo.
echo 🛠️ 故障排除:
echo   1. 端口被占用: 修改docker-compose.yml中的端口映射
echo   2. 服务启动失败: 查看日志 docker-compose logs [服务名]
echo   3. 数据库连接失败: 重启数据库 docker-compose restart postgres
echo   4. 内存不足: 关闭不必要的服务或增加系统内存
echo.
echo 📞 获取支持:
echo   - 查看README.md文件
echo   - 检查项目文档
echo   - 提交GitHub Issue
echo.

echo 按任意键返回主菜单...
pause >nul
goto menu
