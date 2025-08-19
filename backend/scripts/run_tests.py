#!/usr/bin/env python3
"""
测试运行脚本
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(command, cwd=None):
    """运行命令"""
    print(f"执行命令: {command}")
    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd or project_root,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def setup_test_environment():
    """设置测试环境"""
    print("设置测试环境...")
    
    # 设置环境变量
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:password@localhost:5432/trading_robot_test"
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # 使用不同的Redis数据库
    
    # 创建测试数据库
    print("创建测试数据库...")
    create_db_command = """
    psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS trading_robot_test;"
    psql -h localhost -U postgres -c "CREATE DATABASE trading_robot_test;"
    """
    
    if not run_command(create_db_command):
        print("警告: 无法创建测试数据库，请确保PostgreSQL正在运行")
    
    return True


def run_unit_tests():
    """运行单元测试"""
    print("\n" + "="*50)
    print("运行单元测试")
    print("="*50)
    
    command = "python -m pytest tests/unit/ -v --tb=short --cov=app --cov-report=term-missing"
    return run_command(command)


def run_integration_tests():
    """运行集成测试"""
    print("\n" + "="*50)
    print("运行集成测试")
    print("="*50)
    
    command = "python -m pytest tests/integration/ -v --tb=short"
    return run_command(command)


def run_e2e_tests():
    """运行端到端测试"""
    print("\n" + "="*50)
    print("运行端到端测试")
    print("="*50)
    
    command = "python -m pytest tests/e2e/ -v --tb=short -m 'not slow'"
    return run_command(command)


def run_performance_tests():
    """运行性能测试"""
    print("\n" + "="*50)
    print("运行性能测试")
    print("="*50)
    
    command = "python -m pytest tests/e2e/ -v --tb=short -m 'slow'"
    return run_command(command)


def run_linting():
    """运行代码检查"""
    print("\n" + "="*50)
    print("运行代码检查")
    print("="*50)
    
    # Flake8检查
    print("运行Flake8...")
    if not run_command("flake8 app/ --max-line-length=100 --ignore=E203,W503"):
        print("Flake8检查失败")
        return False
    
    # Black格式检查
    print("运行Black格式检查...")
    if not run_command("black --check app/ tests/"):
        print("Black格式检查失败")
        return False
    
    # isort导入排序检查
    print("运行isort检查...")
    if not run_command("isort --check-only app/ tests/"):
        print("isort检查失败")
        return False
    
    # mypy类型检查
    print("运行mypy类型检查...")
    if not run_command("mypy app/ --ignore-missing-imports"):
        print("mypy类型检查失败")
        return False
    
    return True


def run_security_tests():
    """运行安全测试"""
    print("\n" + "="*50)
    print("运行安全测试")
    print("="*50)
    
    # Bandit安全检查
    print("运行Bandit安全检查...")
    if not run_command("bandit -r app/ -f json -o bandit-report.json"):
        print("Bandit安全检查失败")
        return False
    
    # Safety依赖安全检查
    print("运行Safety依赖检查...")
    if not run_command("safety check --json --output safety-report.json"):
        print("Safety依赖检查失败")
        return False
    
    return True


def generate_test_report():
    """生成测试报告"""
    print("\n" + "="*50)
    print("生成测试报告")
    print("="*50)
    
    # 生成HTML覆盖率报告
    print("生成覆盖率报告...")
    run_command("python -m pytest tests/unit/ --cov=app --cov-report=html:htmlcov")
    
    # 生成JUnit XML报告
    print("生成JUnit报告...")
    run_command("python -m pytest tests/ --junitxml=test-results.xml")
    
    print("测试报告已生成:")
    print("- 覆盖率报告: htmlcov/index.html")
    print("- JUnit报告: test-results.xml")
    print("- Bandit报告: bandit-report.json")
    print("- Safety报告: safety-report.json")


def cleanup_test_environment():
    """清理测试环境"""
    print("\n清理测试环境...")
    
    # 删除测试数据库
    drop_db_command = "psql -h localhost -U postgres -c 'DROP DATABASE IF EXISTS trading_robot_test;'"
    run_command(drop_db_command)
    
    # 清理Redis测试数据
    redis_cleanup = "redis-cli -n 15 FLUSHDB"
    run_command(redis_cleanup)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Trading Robot测试运行器")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--e2e", action="store_true", help="只运行端到端测试")
    parser.add_argument("--performance", action="store_true", help="只运行性能测试")
    parser.add_argument("--lint", action="store_true", help="只运行代码检查")
    parser.add_argument("--security", action="store_true", help="只运行安全测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--no-setup", action="store_true", help="跳过环境设置")
    parser.add_argument("--no-cleanup", action="store_true", help="跳过环境清理")
    parser.add_argument("--report", action="store_true", help="生成测试报告")
    
    args = parser.parse_args()
    
    # 如果没有指定任何测试类型，默认运行所有测试
    if not any([args.unit, args.integration, args.e2e, args.performance, args.lint, args.security]):
        args.all = True
    
    success = True
    
    try:
        # 设置测试环境
        if not args.no_setup:
            if not setup_test_environment():
                print("测试环境设置失败")
                return 1
        
        # 运行测试
        if args.lint or args.all:
            if not run_linting():
                success = False
        
        if args.unit or args.all:
            if not run_unit_tests():
                success = False
        
        if args.integration or args.all:
            if not run_integration_tests():
                success = False
        
        if args.e2e or args.all:
            if not run_e2e_tests():
                success = False
        
        if args.performance:
            if not run_performance_tests():
                success = False
        
        if args.security or args.all:
            if not run_security_tests():
                success = False
        
        # 生成报告
        if args.report or args.all:
            generate_test_report()
        
        # 输出结果
        print("\n" + "="*50)
        if success:
            print("✅ 所有测试通过!")
        else:
            print("❌ 部分测试失败!")
        print("="*50)
        
    finally:
        # 清理测试环境
        if not args.no_cleanup:
            cleanup_test_environment()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
