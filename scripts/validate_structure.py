#!/usr/bin/env python3
"""
验证项目结构和代码完整性
"""
import os
from pathlib import Path

def check_file_exists(file_path, description=""):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✓ {description or file_path}")
        return True
    else:
        print(f"✗ {description or file_path} - 文件不存在")
        return False

def check_directory_structure():
    """检查目录结构"""
    print("=== 检查项目目录结构 ===")
    
    required_dirs = [
        "backend",
        "backend/app",
        "backend/app/api",
        "backend/app/api/endpoints",
        "backend/app/core",
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/services",
        "backend/data_sources",
        "backend/config",
        "scripts"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - 目录不存在")
            all_exist = False
    
    return all_exist

def check_data_source_files():
    """检查数据源文件"""
    print("\n=== 检查数据源文件 ===")
    
    files = [
        ("backend/data_sources/__init__.py", "数据源包初始化"),
        ("backend/data_sources/base_data_source.py", "基础数据源"),
        ("backend/data_sources/market_data_source.py", "市场数据源"),
        ("backend/data_sources/news_data_source.py", "新闻数据源"),
        ("backend/data_sources/whale_monitor.py", "大户监控"),
    ]
    
    all_exist = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_service_files():
    """检查服务文件"""
    print("\n=== 检查服务文件 ===")
    
    files = [
        ("backend/app/services/data_service.py", "数据服务"),
        ("backend/app/services/strategy_manager.py", "策略管理器"),
        ("backend/app/services/trading_service.py", "交易服务"),
        ("backend/app/services/exchange_service.py", "交易所服务"),
        ("backend/app/services/risk_manager.py", "风险管理器"),
    ]
    
    all_exist = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_api_files():
    """检查API文件"""
    print("\n=== 检查API文件 ===")
    
    files = [
        ("backend/app/api/__init__.py", "API路由器"),
        ("backend/app/api/endpoints/data.py", "数据API端点"),
        ("backend/app/api/endpoints/strategies.py", "策略API端点"),
        ("backend/app/api/endpoints/trading.py", "交易API端点"),
        ("backend/app/api/endpoints/accounts.py", "账户API端点"),
    ]
    
    all_exist = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_config_files():
    """检查配置文件"""
    print("\n=== 检查配置文件 ===")
    
    files = [
        ("backend/requirements.txt", "Python依赖"),
        ("backend/config/data_sources.yaml", "数据源配置"),
        ("backend/app/core/config.py", "应用配置"),
        ("backend/app/core/database.py", "数据库配置"),
        ("backend/app/core/logging.py", "日志配置"),
    ]
    
    all_exist = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_main_files():
    """检查主要文件"""
    print("\n=== 检查主要文件 ===")
    
    files = [
        ("backend/app/main.py", "主应用入口"),
        ("README.md", "项目说明"),
        ("scripts/test_data_collection.py", "数据采集测试"),
        ("scripts/quick_test.py", "快速测试"),
    ]
    
    all_exist = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_file_content_samples():
    """检查文件内容示例"""
    print("\n=== 检查关键文件内容 ===")
    
    checks = []
    
    # 检查base_data_source.py
    try:
        with open("backend/data_sources/base_data_source.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "class BaseDataSource" in content and "class DataPoint" in content:
                print("✓ base_data_source.py - 包含核心类")
                checks.append(True)
            else:
                print("✗ base_data_source.py - 缺少核心类")
                checks.append(False)
    except Exception as e:
        print(f"✗ base_data_source.py - 读取失败: {e}")
        checks.append(False)
    
    # 检查data_service.py
    try:
        with open("backend/app/services/data_service.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "class DataService" in content and "class DataProcessor" in content:
                print("✓ data_service.py - 包含核心类")
                checks.append(True)
            else:
                print("✗ data_service.py - 缺少核心类")
                checks.append(False)
    except Exception as e:
        print(f"✗ data_service.py - 读取失败: {e}")
        checks.append(False)
    
    # 检查API路由
    try:
        with open("backend/app/api/__init__.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "data.router" in content and "api_router" in content:
                print("✓ API路由 - 包含数据端点")
                checks.append(True)
            else:
                print("✗ API路由 - 缺少数据端点")
                checks.append(False)
    except Exception as e:
        print(f"✗ API路由 - 读取失败: {e}")
        checks.append(False)
    
    return all(checks)

def main():
    """主函数"""
    print("=== 数字货币交易机器人 - 项目结构验证 ===\n")
    
    checks = [
        check_directory_structure(),
        check_data_source_files(),
        check_service_files(),
        check_api_files(),
        check_config_files(),
        check_main_files(),
        check_file_content_samples()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n=== 验证结果 ===")
    print(f"通过检查: {passed}/{total}")
    print(f"完成度: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 项目结构完整！")
        print("\n✅ 数据采集与处理模块已完成:")
        print("   - 基础数据源框架")
        print("   - OKX市场数据源")
        print("   - 加密货币新闻数据源")
        print("   - 大户监控数据源")
        print("   - 数据处理服务")
        print("   - 数据API端点")
        print("   - 配置文件和测试脚本")
        
        print("\n📋 下一步工作:")
        print("   1. 安装Python环境和依赖包")
        print("   2. 配置API密钥（OKX、Whale Alert等）")
        print("   3. 运行测试验证功能")
        print("   4. 开始Web可视化界面开发")
        
        return 0
    else:
        print(f"\n⚠️  发现 {total - passed} 个问题，请检查缺失的文件")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
