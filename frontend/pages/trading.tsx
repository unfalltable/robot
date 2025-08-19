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
  Typography,
  Row,
  Col,
  Statistic,
  Tabs,
  message,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  ReloadOutlined,
  DollarOutlined,
  TradingViewOutlined,
  LineChartOutlined
} from '@ant-design/icons';
import MainLayout from '../components/Layout/MainLayout';
import { Order, Position, OrderSide, OrderType, OrderStatus } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const Trading: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  // 模拟订单数据
  const mockOrders: Order[] = [
    {
      id: '1',
      symbol: 'BTC/USDT',
      side: 'buy',
      type: 'limit',
      amount: 0.1,
      price: 45000,
      status: 'filled',
      filled_amount: 0.1,
      remaining_amount: 0,
      created_at: '2024-01-01T10:00:00Z',
      updated_at: '2024-01-01T10:05:00Z'
    },
    {
      id: '2',
      symbol: 'ETH/USDT',
      side: 'sell',
      type: 'market',
      amount: 2.5,
      status: 'pending',
      filled_amount: 0,
      remaining_amount: 2.5,
      created_at: '2024-01-01T11:00:00Z',
      updated_at: '2024-01-01T11:00:00Z'
    },
    {
      id: '3',
      symbol: 'BNB/USDT',
      side: 'buy',
      type: 'limit',
      amount: 10,
      price: 300,
      status: 'open',
      filled_amount: 5,
      remaining_amount: 5,
      created_at: '2024-01-01T12:00:00Z',
      updated_at: '2024-01-01T12:30:00Z'
    }
  ];

  // 模拟持仓数据
  const mockPositions: Position[] = [
    {
      symbol: 'BTC/USDT',
      side: 'long',
      size: 0.1,
      entry_price: 45000,
      current_price: 46500,
      unrealized_pnl: 150,
      realized_pnl: 0,
      margin: 4500,
      percentage: 3.33,
      created_at: '2024-01-01T10:05:00Z'
    },
    {
      symbol: 'ETH/USDT',
      side: 'short',
      size: 1.0,
      entry_price: 2800,
      current_price: 2750,
      unrealized_pnl: 50,
      realized_pnl: 0,
      margin: 280,
      percentage: 1.79,
      created_at: '2024-01-01T09:30:00Z'
    }
  ];

  useEffect(() => {
    setOrders(mockOrders);
    setPositions(mockPositions);
  }, []);

  // 创建订单
  const handleCreateOrder = async (values: any) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newOrder: Order = {
        id: Date.now().toString(),
        symbol: values.symbol,
        side: values.side,
        type: values.type,
        amount: values.amount,
        price: values.price,
        stop_price: values.stop_price,
        status: 'pending',
        filled_amount: 0,
        remaining_amount: values.amount,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      setOrders(prev => [newOrder, ...prev]);
      setModalVisible(false);
      form.resetFields();
      message.success('订单创建成功');
    } catch (error) {
      message.error('订单创建失败');
    } finally {
      setLoading(false);
    }
  };

  // 取消订单
  const handleCancelOrder = async (orderId: string) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setOrders(prev => prev.map(order => 
        order.id === orderId 
          ? { ...order, status: 'cancelled' as OrderStatus }
          : order
      ));
      
      message.success('订单取消成功');
    } catch (error) {
      message.error('订单取消失败');
    } finally {
      setLoading(false);
    }
  };

  // 刷新数据
  const handleRefresh = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      // 这里会调用API刷新数据
      message.success('数据刷新成功');
    } catch (error) {
      message.error('数据刷新失败');
    } finally {
      setLoading(false);
    }
  };

  // 订单表格列
  const orderColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <Tag color="blue">{symbol}</Tag>,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      render: (side: OrderSide) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: OrderType) => {
        const typeMap = {
          market: '市价',
          limit: '限价',
          stop: '止损',
          stop_limit: '止损限价'
        };
        return typeMap[type];
      },
    },
    {
      title: '数量',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => amount.toFixed(4),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => price ? `$${price.toFixed(2)}` : '-',
    },
    {
      title: '已成交',
      dataIndex: 'filled_amount',
      key: 'filled_amount',
      render: (filled: number, record: Order) => 
        `${filled.toFixed(4)} / ${record.amount.toFixed(4)}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: OrderStatus) => {
        const statusConfig = {
          pending: { color: 'orange', text: '待成交' },
          open: { color: 'blue', text: '部分成交' },
          filled: { color: 'green', text: '已成交' },
          cancelled: { color: 'red', text: '已取消' },
          rejected: { color: 'red', text: '已拒绝' },
        };
        const config = statusConfig[status];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record: Order) => (
        <Space size="small">
          {(record.status === 'pending' || record.status === 'open') && (
            <Popconfirm
              title="确定要取消这个订单吗？"
              onConfirm={() => handleCancelOrder(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button size="small" danger icon={<DeleteOutlined />}>
                取消
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  // 持仓表格列
  const positionColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <Tag color="blue">{symbol}</Tag>,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      render: (side: 'long' | 'short') => (
        <Tag color={side === 'long' ? 'green' : 'red'}>
          {side === 'long' ? '多头' : '空头'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => size.toFixed(4),
    },
    {
      title: '开仓价格',
      dataIndex: 'entry_price',
      key: 'entry_price',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '当前价格',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '未实现盈亏',
      dataIndex: 'unrealized_pnl',
      key: 'unrealized_pnl',
      render: (pnl: number) => (
        <Text style={{ color: pnl >= 0 ? '#3f8600' : '#cf1322' }}>
          {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
        </Text>
      ),
    },
    {
      title: '收益率',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (percentage: number) => (
        <Text style={{ color: percentage >= 0 ? '#3f8600' : '#cf1322' }}>
          {percentage >= 0 ? '+' : ''}{percentage.toFixed(2)}%
        </Text>
      ),
    },
    {
      title: '保证金',
      dataIndex: 'margin',
      key: 'margin',
      render: (margin: number) => `$${margin.toFixed(2)}`,
    },
    {
      title: '开仓时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString(),
    },
  ];

  // 计算统计数据
  const stats = {
    totalOrders: orders.length,
    activeOrders: orders.filter(o => o.status === 'pending' || o.status === 'open').length,
    totalPositions: positions.length,
    totalPnl: positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0),
  };

  return (
    <MainLayout>
      <div>
        {/* 标题和操作 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>交易管理</Title>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setModalVisible(true)}
            >
              创建订单
            </Button>
          </Space>
        </div>

        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="总订单数" 
                value={stats.totalOrders} 
                prefix={<TradingViewOutlined />}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="活跃订单" 
                value={stats.activeOrders} 
                valueStyle={{ color: '#1890ff' }}
                prefix={<LineChartOutlined />}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="持仓数量" 
                value={stats.totalPositions} 
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="未实现盈亏" 
                value={stats.totalPnl} 
                precision={2}
                valueStyle={{ color: stats.totalPnl >= 0 ? '#3f8600' : '#cf1322' }}
                prefix={<DollarOutlined />}
                suffix="USDT"
              />
            </Card>
          </Col>
        </Row>

        {/* 主要内容 */}
        <Card>
          <Tabs defaultActiveKey="orders">
            <TabPane tab="订单管理" key="orders">
              <Table
                columns={orderColumns}
                dataSource={orders}
                rowKey="id"
                loading={loading}
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 条记录`,
                }}
              />
            </TabPane>
            <TabPane tab="持仓管理" key="positions">
              <Table
                columns={positionColumns}
                dataSource={positions}
                rowKey="symbol"
                loading={loading}
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 条记录`,
                }}
              />
            </TabPane>
          </Tabs>
        </Card>

        {/* 创建订单模态框 */}
        <Modal
          title="创建订单"
          open={modalVisible}
          onCancel={() => setModalVisible(false)}
          onOk={() => form.submit()}
          confirmLoading={loading}
          width={500}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateOrder}
          >
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

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="side"
                  label="方向"
                  rules={[{ required: true, message: '请选择交易方向' }]}
                >
                  <Select placeholder="请选择方向">
                    <Option value="buy">买入</Option>
                    <Option value="sell">卖出</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="type"
                  label="类型"
                  rules={[{ required: true, message: '请选择订单类型' }]}
                >
                  <Select placeholder="请选择类型">
                    <Option value="market">市价</Option>
                    <Option value="limit">限价</Option>
                    <Option value="stop">止损</Option>
                    <Option value="stop_limit">止损限价</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              name="amount"
              label="数量"
              rules={[{ required: true, message: '请输入交易数量' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                placeholder="请输入数量"
                min={0}
                step={0.0001}
                precision={4}
              />
            </Form.Item>

            <Form.Item
              name="price"
              label="价格"
              rules={[
                ({ getFieldValue }) => ({
                  required: ['limit', 'stop_limit'].includes(getFieldValue('type')),
                  message: '请输入价格',
                }),
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                placeholder="请输入价格"
                min={0}
                step={0.01}
                precision={2}
              />
            </Form.Item>

            <Form.Item
              name="stop_price"
              label="止损价格"
              rules={[
                ({ getFieldValue }) => ({
                  required: ['stop', 'stop_limit'].includes(getFieldValue('type')),
                  message: '请输入止损价格',
                }),
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                placeholder="请输入止损价格"
                min={0}
                step={0.01}
                precision={2}
              />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </MainLayout>
  );
};

export default Trading;
