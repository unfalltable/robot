import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Typography,
  Row,
  Col,
  Statistic,
  Popconfirm,
  message,
  Drawer,
  Descriptions,
  Progress
} from 'antd';
import {
  PlusOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SettingOutlined
} from '@ant-design/icons';
import MainLayout from '../components/Layout/MainLayout';
import { Strategy, StrategyStatus, StrategyParameter } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;

const Strategies: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [form] = Form.useForm();

  // 模拟策略数据
  const mockStrategies: Strategy[] = [
    {
      id: '1',
      name: '网格交易策略',
      description: 'BTC网格交易，适合震荡行情',
      status: 'running',
      symbol: 'BTC/USDT',
      parameters: [
        { name: 'grid_size', type: 'number', value: 0.5, default_value: 0.5, description: '网格间距(%)', min: 0.1, max: 5.0, step: 0.1 },
        { name: 'grid_count', type: 'number', value: 10, default_value: 10, description: '网格数量', min: 5, max: 50, step: 1 },
        { name: 'base_amount', type: 'number', value: 1000, default_value: 1000, description: '基础金额(USDT)', min: 100, max: 10000, step: 100 }
      ],
      performance: {
        total_return: 12.5,
        daily_return: 2.3,
        max_drawdown: -5.2,
        sharpe_ratio: 1.8,
        win_rate: 68.5,
        total_trades: 156
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      started_at: '2024-01-01T08:00:00Z'
    },
    {
      id: '2',
      name: '动量策略',
      description: 'ETH动量交易，追踪趋势',
      status: 'stopped',
      symbol: 'ETH/USDT',
      parameters: [
        { name: 'momentum_period', type: 'number', value: 14, default_value: 14, description: '动量周期', min: 5, max: 50, step: 1 },
        { name: 'threshold', type: 'number', value: 2.0, default_value: 2.0, description: '触发阈值(%)', min: 0.5, max: 10.0, step: 0.5 },
        { name: 'position_size', type: 'number', value: 0.1, default_value: 0.1, description: '仓位大小', min: 0.01, max: 1.0, step: 0.01 }
      ],
      performance: {
        total_return: -3.2,
        daily_return: -0.8,
        max_drawdown: -8.1,
        sharpe_ratio: 0.9,
        win_rate: 45.2,
        total_trades: 89
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      stopped_at: '2024-01-02T10:00:00Z'
    },
    {
      id: '3',
      name: '均值回归策略',
      description: 'BNB均值回归，低买高卖',
      status: 'paused',
      symbol: 'BNB/USDT',
      parameters: [
        { name: 'lookback_period', type: 'number', value: 20, default_value: 20, description: '回看周期', min: 10, max: 100, step: 1 },
        { name: 'deviation_threshold', type: 'number', value: 1.5, default_value: 1.5, description: '偏离阈值', min: 0.5, max: 3.0, step: 0.1 },
        { name: 'max_position', type: 'number', value: 5000, default_value: 5000, description: '最大仓位(USDT)', min: 1000, max: 20000, step: 500 }
      ],
      performance: {
        total_return: 8.7,
        daily_return: 1.2,
        max_drawdown: -3.8,
        sharpe_ratio: 1.5,
        win_rate: 72.3,
        total_trades: 203
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
  ];

  useEffect(() => {
    setStrategies(mockStrategies);
  }, []);

  // 策略状态操作
  const handleStrategyAction = async (strategyId: string, action: 'start' | 'stop' | 'pause' | 'resume') => {
    setLoading(true);
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStrategies(prev => prev.map(strategy => {
        if (strategy.id === strategyId) {
          let newStatus: StrategyStatus;
          switch (action) {
            case 'start':
            case 'resume':
              newStatus = 'running';
              break;
            case 'stop':
              newStatus = 'stopped';
              break;
            case 'pause':
              newStatus = 'paused';
              break;
            default:
              newStatus = strategy.status;
          }
          return { ...strategy, status: newStatus };
        }
        return strategy;
      }));
      
      message.success(`策略${action === 'start' ? '启动' : action === 'stop' ? '停止' : action === 'pause' ? '暂停' : '恢复'}成功`);
    } catch (error) {
      message.error('操作失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除策略
  const handleDeleteStrategy = async (strategyId: string) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setStrategies(prev => prev.filter(s => s.id !== strategyId));
      message.success('策略删除成功');
    } catch (error) {
      message.error('删除失败');
    } finally {
      setLoading(false);
    }
  };

  // 查看策略详情
  const handleViewStrategy = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setDrawerVisible(true);
  };

  // 编辑策略
  const handleEditStrategy = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    form.setFieldsValue({
      name: strategy.name,
      description: strategy.description,
      symbol: strategy.symbol,
      ...strategy.parameters.reduce((acc, param) => {
        acc[param.name] = param.value;
        return acc;
      }, {} as Record<string, any>)
    });
    setModalVisible(true);
  };

  // 创建新策略
  const handleCreateStrategy = () => {
    setSelectedStrategy(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 保存策略
  const handleSaveStrategy = async (values: any) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (selectedStrategy) {
        // 更新策略
        setStrategies(prev => prev.map(s => 
          s.id === selectedStrategy.id 
            ? { ...s, ...values, updated_at: new Date().toISOString() }
            : s
        ));
        message.success('策略更新成功');
      } else {
        // 创建新策略
        const newStrategy: Strategy = {
          id: Date.now().toString(),
          name: values.name,
          description: values.description,
          status: 'stopped',
          symbol: values.symbol,
          parameters: [],
          performance: {
            total_return: 0,
            daily_return: 0,
            max_drawdown: 0,
            sharpe_ratio: 0,
            win_rate: 0,
            total_trades: 0
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        setStrategies(prev => [...prev, newStrategy]);
        message.success('策略创建成功');
      }
      
      setModalVisible(false);
    } catch (error) {
      message.error('保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Strategy) => (
        <Space direction="vertical" size={0}>
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{record.description}</Text>
        </Space>
      ),
    },
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <Tag color="blue">{symbol}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: StrategyStatus) => {
        const statusConfig = {
          running: { color: 'green', text: '运行中' },
          stopped: { color: 'red', text: '已停止' },
          paused: { color: 'orange', text: '已暂停' },
          error: { color: 'red', text: '错误' },
        };
        const config = statusConfig[status];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '总收益率',
      dataIndex: ['performance', 'total_return'],
      key: 'total_return',
      render: (value: number) => (
        <Text style={{ color: value >= 0 ? '#3f8600' : '#cf1322' }}>
          {value >= 0 ? '+' : ''}{value.toFixed(2)}%
        </Text>
      ),
    },
    {
      title: '胜率',
      dataIndex: ['performance', 'win_rate'],
      key: 'win_rate',
      render: (value: number) => `${value.toFixed(1)}%`,
    },
    {
      title: '交易次数',
      dataIndex: ['performance', 'total_trades'],
      key: 'total_trades',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record: Strategy) => (
        <Space size="small">
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewStrategy(record)}
          >
            查看
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditStrategy(record)}
          >
            编辑
          </Button>
          {record.status === 'running' ? (
            <Button
              size="small"
              icon={<PauseCircleOutlined />}
              onClick={() => handleStrategyAction(record.id, 'pause')}
              loading={loading}
            >
              暂停
            </Button>
          ) : record.status === 'paused' ? (
            <Button
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleStrategyAction(record.id, 'resume')}
              loading={loading}
            >
              恢复
            </Button>
          ) : (
            <Button
              size="small"
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={() => handleStrategyAction(record.id, 'start')}
              loading={loading}
            >
              启动
            </Button>
          )}
          {record.status === 'running' && (
            <Button
              size="small"
              danger
              icon={<StopOutlined />}
              onClick={() => handleStrategyAction(record.id, 'stop')}
              loading={loading}
            >
              停止
            </Button>
          )}
          <Popconfirm
            title="确定要删除这个策略吗？"
            onConfirm={() => handleDeleteStrategy(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              loading={loading}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 统计数据
  const stats = {
    total: strategies.length,
    running: strategies.filter(s => s.status === 'running').length,
    stopped: strategies.filter(s => s.status === 'stopped').length,
    paused: strategies.filter(s => s.status === 'paused').length,
  };

  return (
    <MainLayout>
      <div>
        {/* 标题和操作 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>策略管理</Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateStrategy}
          >
            创建策略
          </Button>
        </div>

        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic title="总策略数" value={stats.total} />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="运行中" 
                value={stats.running} 
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="已暂停" 
                value={stats.paused} 
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="已停止" 
                value={stats.stopped} 
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 策略列表 */}
        <Card>
          <Table
            columns={columns}
            dataSource={strategies}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
          />
        </Card>

        {/* 创建/编辑策略模态框 */}
        <Modal
          title={selectedStrategy ? '编辑策略' : '创建策略'}
          open={modalVisible}
          onCancel={() => setModalVisible(false)}
          onOk={() => form.submit()}
          confirmLoading={loading}
          width={600}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSaveStrategy}
          >
            <Form.Item
              name="name"
              label="策略名称"
              rules={[{ required: true, message: '请输入策略名称' }]}
            >
              <Input placeholder="请输入策略名称" />
            </Form.Item>
            
            <Form.Item
              name="description"
              label="策略描述"
              rules={[{ required: true, message: '请输入策略描述' }]}
            >
              <Input.TextArea placeholder="请输入策略描述" rows={3} />
            </Form.Item>
            
            <Form.Item
              name="symbol"
              label="交易对"
              rules={[{ required: true, message: '请选择交易对' }]}
            >
              <Select placeholder="请选择交易对">
                <Option value="BTC/USDT">BTC/USDT</Option>
                <Option value="ETH/USDT">ETH/USDT</Option>
                <Option value="BNB/USDT">BNB/USDT</Option>
                <Option value="ADA/USDT">ADA/USDT</Option>
                <Option value="SOL/USDT">SOL/USDT</Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>

        {/* 策略详情抽屉 */}
        <Drawer
          title="策略详情"
          placement="right"
          width={600}
          open={drawerVisible}
          onClose={() => setDrawerVisible(false)}
        >
          {selectedStrategy && (
            <div>
              <Descriptions title="基本信息" bordered column={1} size="small">
                <Descriptions.Item label="策略名称">{selectedStrategy.name}</Descriptions.Item>
                <Descriptions.Item label="策略描述">{selectedStrategy.description}</Descriptions.Item>
                <Descriptions.Item label="交易对">
                  <Tag color="blue">{selectedStrategy.symbol}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="当前状态">
                  <Tag color={selectedStrategy.status === 'running' ? 'green' : 'red'}>
                    {selectedStrategy.status === 'running' ? '运行中' : '已停止'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {new Date(selectedStrategy.created_at).toLocaleString()}
                </Descriptions.Item>
              </Descriptions>

              <Descriptions title="性能指标" bordered column={1} size="small" style={{ marginTop: 24 }}>
                <Descriptions.Item label="总收益率">
                  <Text style={{ color: selectedStrategy.performance.total_return >= 0 ? '#3f8600' : '#cf1322' }}>
                    {selectedStrategy.performance.total_return >= 0 ? '+' : ''}
                    {selectedStrategy.performance.total_return.toFixed(2)}%
                  </Text>
                </Descriptions.Item>
                <Descriptions.Item label="日收益率">
                  {selectedStrategy.performance.daily_return.toFixed(2)}%
                </Descriptions.Item>
                <Descriptions.Item label="最大回撤">
                  {selectedStrategy.performance.max_drawdown.toFixed(2)}%
                </Descriptions.Item>
                <Descriptions.Item label="夏普比率">
                  {selectedStrategy.performance.sharpe_ratio.toFixed(2)}
                </Descriptions.Item>
                <Descriptions.Item label="胜率">
                  <Progress 
                    percent={selectedStrategy.performance.win_rate} 
                    size="small" 
                    format={(percent) => `${percent?.toFixed(1)}%`}
                  />
                </Descriptions.Item>
                <Descriptions.Item label="总交易次数">
                  {selectedStrategy.performance.total_trades}
                </Descriptions.Item>
              </Descriptions>

              {selectedStrategy.parameters.length > 0 && (
                <Descriptions title="策略参数" bordered column={1} size="small" style={{ marginTop: 24 }}>
                  {selectedStrategy.parameters.map((param) => (
                    <Descriptions.Item key={param.name} label={param.description}>
                      {param.value} {param.type === 'number' && param.name.includes('percent') ? '%' : ''}
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              )}
            </div>
          )}
        </Drawer>
      </div>
    </MainLayout>
  );
};

export default Strategies;
