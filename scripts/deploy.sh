#!/bin/bash

# Trading Robot 部署脚本
# 使用方法: ./deploy.sh [环境] [选项]
# 环境: dev, staging, prod
# 选项: --build, --migrate, --seed, --restart, --logs

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 设置环境变量
setup_environment() {
    local env=$1
    log_info "设置 $env 环境..."
    
    case $env in
        "dev")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.dev.yml"
            export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/trading_robot_dev"
            export DEBUG="true"
            export LOG_LEVEL="DEBUG"
            ;;
        "staging")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.staging.yml"
            export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/trading_robot_staging"
            export DEBUG="false"
            export LOG_LEVEL="INFO"
            ;;
        "prod")
            export COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
            export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/trading_robot"
            export DEBUG="false"
            export LOG_LEVEL="WARNING"
            ;;
        *)
            log_error "未知环境: $env"
            exit 1
            ;;
    esac
    
    # 加载环境变量文件
    if [ -f ".env.$env" ]; then
        log_info "加载环境变量文件: .env.$env"
        export $(cat .env.$env | grep -v '^#' | xargs)
    fi
    
    log_success "环境设置完成"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动基础服务
    docker-compose up -d postgres redis
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 10
    
    # 启动应用服务
    docker-compose up -d backend celery_worker celery_beat
    
    # 等待后端启动
    log_info "等待后端服务启动..."
    sleep 15
    
    # 启动前端和代理
    docker-compose up -d frontend nginx
    
    # 启动监控服务
    docker-compose up -d prometheus grafana elasticsearch kibana filebeat
    
    log_success "所有服务已启动"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    docker-compose down
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    
    stop_services
    start_services
    
    log_success "服务已重启"
}

# 数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    # 确保数据库服务运行
    docker-compose up -d postgres
    sleep 5
    
    # 运行迁移
    docker-compose exec backend python scripts/init_database.py
    
    log_success "数据库迁移完成"
}

# 数据种子
seed_data() {
    log_info "插入种子数据..."
    
    docker-compose exec backend python scripts/seed_data.py
    
    log_success "种子数据插入完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 启动测试依赖
    docker-compose up -d postgres redis
    sleep 5
    
    # 运行测试
    docker-compose exec backend python scripts/run_tests.py --all
    
    log_success "测试完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/health > /dev/null 2>&1; then
            log_success "健康检查通过"
            return 0
        fi
        
        log_info "健康检查失败，重试 $attempt/$max_attempts..."
        sleep 10
        ((attempt++))
    done
    
    log_error "健康检查失败"
    return 1
}

# 查看日志
view_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $service
    fi
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $backup_dir
    
    # 备份数据库
    docker-compose exec postgres pg_dump -U postgres trading_robot > $backup_dir/database.sql
    
    # 备份配置文件
    cp -r .env* $backup_dir/ 2>/dev/null || true
    
    log_success "数据备份完成: $backup_dir"
}

# 恢复数据
restore_data() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        exit 1
    fi
    
    log_info "恢复数据: $backup_file"
    
    # 恢复数据库
    docker-compose exec -T postgres psql -U postgres trading_robot < $backup_file
    
    log_success "数据恢复完成"
}

# 清理资源
cleanup() {
    log_info "清理资源..."
    
    # 停止并删除容器
    docker-compose down -v
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的卷
    docker volume prune -f
    
    log_success "资源清理完成"
}

# 监控状态
monitor_status() {
    log_info "服务状态监控..."
    
    echo "Docker容器状态:"
    docker-compose ps
    
    echo -e "\n服务健康状态:"
    curl -s http://localhost/health | jq '.' 2>/dev/null || echo "健康检查API不可用"
    
    echo -e "\n系统资源使用:"
    docker stats --no-stream
}

# 更新服务
update_services() {
    log_info "更新服务..."
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建镜像
    build_images
    
    # 重启服务
    restart_services
    
    # 运行迁移
    run_migrations
    
    # 健康检查
    health_check
    
    log_success "服务更新完成"
}

# 显示帮助信息
show_help() {
    echo "Trading Robot 部署脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 <环境> [选项]"
    echo ""
    echo "环境:"
    echo "  dev      开发环境"
    echo "  staging  预发布环境"
    echo "  prod     生产环境"
    echo ""
    echo "选项:"
    echo "  --build      构建镜像"
    echo "  --start      启动服务"
    echo "  --stop       停止服务"
    echo "  --restart    重启服务"
    echo "  --migrate    运行数据库迁移"
    echo "  --seed       插入种子数据"
    echo "  --test       运行测试"
    echo "  --logs       查看日志"
    echo "  --health     健康检查"
    echo "  --backup     备份数据"
    echo "  --restore    恢复数据"
    echo "  --cleanup    清理资源"
    echo "  --status     查看状态"
    echo "  --update     更新服务"
    echo "  --help       显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 dev --build --start"
    echo "  $0 prod --migrate --restart"
    echo "  $0 staging --logs backend"
}

# 主函数
main() {
    local environment=$1
    shift
    
    if [ -z "$environment" ] || [ "$environment" = "--help" ]; then
        show_help
        exit 0
    fi
    
    # 检查依赖
    check_dependencies
    
    # 设置环境
    setup_environment $environment
    
    # 处理选项
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                build_images
                ;;
            --start)
                start_services
                ;;
            --stop)
                stop_services
                ;;
            --restart)
                restart_services
                ;;
            --migrate)
                run_migrations
                ;;
            --seed)
                seed_data
                ;;
            --test)
                run_tests
                ;;
            --logs)
                view_logs $2
                shift
                ;;
            --health)
                health_check
                ;;
            --backup)
                backup_data
                ;;
            --restore)
                restore_data $2
                shift
                ;;
            --cleanup)
                cleanup
                ;;
            --status)
                monitor_status
                ;;
            --update)
                update_services
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
    
    log_success "部署脚本执行完成"
}

# 执行主函数
main "$@"
