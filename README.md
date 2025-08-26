# 数字货币策略交易机器人

一个功能完整的数字货币自动交易系统，支持多种交易策略、实时数据监控、风险管理和可视化界面。

## ⚠️ 重要提醒：配置文件安全

**在使用本项目前，请注意以下安全事项：**

- 📁 **配置文件已被Git忽略**：`.env`、`backend/monitoring.env` 等配置文件不会被上传到版本控制
- 🔐 **保护您的API密钥**：请勿在代码中硬编码API密钥，使用环境变量配置
- 📋 **使用模板文件**：复制 `.env.example` 到 `.env` 并填入您的配置
- 🚫 **切勿分享配置文件**：配置文件包含敏感信息，请勿分享给他人

详细配置说明请参考：[CONFIGURATION.md](CONFIGURATION.md)

## 🎯 项目进展

### ✅ 已完成功能

#### 1. 项目架构设计与初始化
- ✅ 完整的项目结构设计
- ✅ 技术栈选型和环境配置
- ✅ Docker容器化配置
- ✅ 开发环境搭建

#### 2. 核心交易引擎开发
- ✅ 完整的数据模型设计（订单、持仓、交易、账户等）
- ✅ Pydantic数据验证模式
- ✅ 交易服务核心逻辑
- ✅ 多层次风险管理系统
- ✅ 订单生命周期管理

#### 3. OKX交易所接口集成
- ✅ 标准化交易所基础接口
- ✅ OKX API完整集成
- ✅ 账户管理、订单操作、市场数据获取
- ✅ 异步操作和错误处理

#### 4. 策略框架开发
- ✅ 可扩展的策略基础框架
- ✅ 网格交易策略实现
- ✅ 策略管理器和生命周期控制
- ✅ 交易信号生成和处理

### 🚧 进行中的任务
- 数据采集与处理模块
- Web可视化界面开发
- 数据库设计与实现
- 监控与告警系统
- 测试与部署

## 功能特性

### 核心功能
- 🤖 **智能交易引擎**: 支持多种交易策略的自动执行
- 📊 **实时数据监控**: 行情数据、资讯信息、大户动向监控
- 🎯 **策略管理**: 可视化策略配置和回测
- 🔒 **风险控制**: 多层次风险管理机制
- 📈 **交易分析**: 详细的交易记录和性能分析

### 交易所支持
- ✅ OKX (主要支持)
- 🔄 可扩展支持其他交易所

### 数据源支持
- 📊 实时行情数据
- 📰 新闻资讯监控
- 🐋 大户地址监控
- 📱 社交媒体情绪分析

## 技术架构

### 后端技术栈
- **Python 3.11+**: 主要开发语言
- **FastAPI**: 高性能Web框架
- **SQLAlchemy + PostgreSQL**: 数据持久化
- **Redis**: 缓存和消息队列
- **Celery**: 异步任务处理
- **WebSocket**: 实时数据推送

### 前端技术栈
- **React 18 + TypeScript**: 用户界面
- **Next.js**: 全栈框架
- **Ant Design**: UI组件库
- **Chart.js**: 数据可视化

### 数据处理
- **Pandas + NumPy**: 数据分析
- **APScheduler**: 定时任务
- **ccxt**: 交易所API统一接口

## 项目结构

```
robot/
├── backend/                 # 后端服务
│   ├── app/                # 主应用
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心模块
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   └── utils/         # 工具函数
│   ├── strategies/         # 交易策略
│   ├── data_sources/       # 数据源
│   ├── exchanges/          # 交易所接口
│   └── tests/             # 测试用例
├── frontend/               # 前端应用
│   ├── components/        # React组件
│   ├── pages/            # 页面
│   ├── hooks/            # 自定义Hooks
│   ├── utils/            # 工具函数
│   └── types/            # TypeScript类型
├── docs/                  # 文档
├── scripts/               # 部署脚本
└── docker/               # Docker配置
```

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd robot
```

2. 后端设置
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 前端设置
```bash
cd frontend
npm install
```

4. 数据库设置
```bash
# 创建数据库
createdb trading_robot

# 运行迁移
cd backend
alembic upgrade head
```

5. 启动服务
```bash
# 后端
cd backend
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

## 📋 开发进度

### 已完成功能 ✅

#### 1. 项目架构设计
- [x] 技术栈选择和架构设计
- [x] 目录结构规划
- [x] 开发环境配置

#### 2. 核心交易引擎
- [x] 交易模型定义（订单、持仓、账户等）
- [x] 交易服务基础框架
- [x] 风险管理器
- [x] 交易执行引擎

#### 3. OKX交易所集成
- [x] OKX API封装
- [x] 交易所服务实现
- [x] 订单管理和执行
- [x] 账户信息获取

#### 4. 策略框架开发
- [x] 抽象策略基类
- [x] 策略管理器
- [x] 策略生命周期管理
- [x] 信号处理机制
- [x] 策略API端点

#### 5. 数据采集与处理模块
- [x] 基础数据源框架
- [x] OKX市场数据源（WebSocket实时数据）
- [x] 加密货币新闻数据源（RSS聚合）
- [x] 大户监控数据源（Whale Alert集成）
- [x] 数据处理服务和缓存
- [x] 数据API端点
- [x] 配置文件和测试脚本

### 正在开发 🚧

#### 6. Web可视化界面
- [ ] React前端框架搭建
- [ ] 策略配置界面
- [ ] 交易监控面板
- [ ] 数据可视化图表

### 待开发 📝

#### 7. 数据库设计与实现
- [ ] 数据模型设计
- [ ] 数据库迁移
- [ ] 数据持久化
- [ ] 查询优化

#### 8. 监控与告警系统
- [ ] 系统监控
- [ ] 性能指标
- [ ] 告警机制
- [ ] 日志管理

#### 9. 测试与部署
- [ ] 单元测试
- [ ] 集成测试
- [ ] Docker容器化
- [ ] 部署脚本

## 配置说明

### 环境变量
创建 `.env` 文件并配置以下变量：

```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost/trading_robot

# Redis
REDIS_URL=redis://localhost:6379

# OKX API
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
OKX_SANDBOX=true  # 测试环境

# 安全
SECRET_KEY=your_secret_key
```

## 开发指南

### 添加新策略
1. 在 `backend/strategies/` 目录下创建策略文件
2. 继承 `BaseStrategy` 类
3. 实现必要的方法
4. 在策略管理器中注册

### 添加新数据源
1. 在 `backend/data_sources/` 目录下创建数据源文件
2. 继承 `BaseDataSource` 类
3. 实现数据获取和处理方法

### API文档
启动后端服务后，访问 `http://localhost:8000/docs` 查看API文档。

## 🧪 测试

### 运行所有测试
```bash
cd backend
python scripts/run_tests.py --all
```

### 分类测试
```bash
# 单元测试
python scripts/run_tests.py --unit

# 集成测试
python scripts/run_tests.py --integration

# 端到端测试
python scripts/run_tests.py --e2e

# 性能测试
python scripts/run_tests.py --performance

# 代码检查
python scripts/run_tests.py --lint

# 安全测试
python scripts/run_tests.py --security
```

## 🚀 部署

### 快速部署
```bash
# 开发环境
./scripts/deploy.sh dev --build --start --migrate --seed

# 预发布环境
./scripts/deploy.sh staging --build --start --migrate

# 生产环境
./scripts/deploy.sh prod --build --start --migrate
```

### Docker部署
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 健康检查
```bash
# 检查服务状态
./scripts/deploy.sh dev --status

# 健康检查
curl http://localhost/health

# 监控面板
open http://localhost:3001  # Grafana
open http://localhost:5601  # Kibana
```

## 📊 监控与运维

### 系统监控
- **Prometheus**: 指标收集和存储
- **Grafana**: 可视化仪表板
- **AlertManager**: 告警管理

### 日志管理
- **Elasticsearch**: 日志存储和搜索
- **Kibana**: 日志可视化和分析
- **Filebeat**: 日志收集

### 性能优化
- 数据库索引优化
- Redis缓存策略
- 异步处理优化
- 连接池配置

## 🔒 安全措施

### API安全
- JWT认证
- API限流
- CORS配置
- HTTPS强制

### 数据安全
- 数据加密
- 敏感信息脱敏
- 访问控制
- 审计日志

## 🤝 贡献

欢迎贡献代码！请阅读贡献指南了解详情。

### 开发流程
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 免责声明

本软件仅供学习和研究使用，不构成投资建议。数字货币交易存在高风险，可能导致本金损失。请在充分了解风险的情况下使用本软件，开发者不承担任何投资损失责任。

## 许可证

MIT License
