@echo off
chcp 65001 >nul
title Trading Robot - 查看日志

echo.
echo ==========================================
echo     📝 Trading Robot 日志查看
echo ==========================================
echo.

echo 请选择要查看的服务日志:
echo.
echo 1. 后端服务 (backend)
echo 2. 前端服务 (frontend)
echo 3. 数据库 (postgres)
echo 4. 缓存 (redis)
echo 5. 任务队列 (celery_worker)
echo 6. 定时任务 (celery_beat)
echo 7. 代理服务 (nginx)
echo 8. 所有服务
echo 9. 实时日志 (所有服务)
echo.

set /p choice="请输入选择 (1-9): "

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
    echo 按 Ctrl+C 退出实时日志查看
    docker-compose logs -f
) else (
    echo 无效选择
)

echo.
echo 按任意键退出...
pause >nul
