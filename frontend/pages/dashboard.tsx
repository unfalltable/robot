import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Table,
  Tag,
  Space,
  Button,
  Alert,
  Spin,
  List,
  Avatar
} from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  ReloadOutlined,
  TradingViewOutlined,
  DatabaseOutlined,
  DollarOutlined,
  NewsOutlined,
  WhatsAppOutlined
} from '@ant-design/icons';
import MainLayout from '../components/Layout/MainLayout';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // 模拟数据
  const stats = {
    totalAssets: 125000.50,
    dailyPnl: 1250.75,
    activeStrategies: 2,
    todayTrades: 15,
  };

  const orders = [
    {
      id: '1',
      symbol: 'BTC/USDT',
      side: 'buy',
      amount: 0.1,
      price: 45000,
      status: 'filled'
    },
    {
      id: '2',
      symbol: 'ETH/USDT',
      side: 'sell',
      amount: 2.5,
      price: null,
      status: 'pending'
    }
  ];

  const newsItems = [
    {
      id: '1',
      title: 'Bitcoin突破45000美元关键阻力位',
      source: 'CoinDesk',
      timestamp: new Date().toISOString()
    },
    {
      id: '2',
      title: '以太坊2.0质押量创新高',
      source: 'CoinTelegraph',
      timestamp: new Date().toISOString()
    }
  ];

  const whaleTransactions = [
    {
      id: '1',
      amount: 1000,
      currency: 'BTC',
      exchange_from: 'Binance',
      exchange_to: 'Coinbase',
      timestamp: new Date().toISOString()
    }
  ];

  // 模拟数据加载
  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, []);

  // 刷新数据
  const handleRefresh = async () => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
    }, 1000);
  };

  // 最近订单表格列
  const orderColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
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
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors = {
          pending: 'orange',
          open: 'blue',
          filled: 'green',
          cancelled: 'red',
          rejected: 'red',
        };
        return <Tag color={colors[status as keyof typeof colors]}>{status}</Tag>;
      },
    },
  ];

  if (loading) {
    return (
      <MainLayout>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>加载仪表盘数据...</Text>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div>
        {/* 标题和操作 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>仪表盘</Title>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={refreshing}
            >
              刷新
            </Button>
          </Space>
        </div>

        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总资产"
                value={stats.totalAssets}
                precision={2}
                valueStyle={{ color: '#3f8600' }}
                prefix={<DollarOutlined />}
                suffix="USDT"
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="今日收益"
                value={stats.dailyPnl}
                precision={2}
                valueStyle={{ color: stats.dailyPnl >= 0 ? '#3f8600' : '#cf1322' }}
                prefix={stats.dailyPnl >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                suffix="USDT"
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="活跃策略"
                value={stats.activeStrategies}
                valueStyle={{ color: '#1890ff' }}
                prefix={<TradingViewOutlined />}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="今日交易"
                value={stats.todayTrades}
                valueStyle={{ color: '#722ed1' }}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
        </Row>

        {/* 主要内容区域 */}
        <Row gutter={[16, 16]}>
          {/* 最近订单 */}
          <Col xs={24} lg={16}>
            <Card title="最近订单" size="small">
              <Table
                columns={orderColumns}
                dataSource={orders}
                pagination={false}
                size="small"
                rowKey="id"
              />
            </Card>
          </Col>

          {/* 最新消息 */}
          <Col xs={24} lg={8}>
            <Card title="最新消息" size="small">
              <List
                size="small"
                dataSource={newsItems}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<Avatar icon={<NewsOutlined />} size="small" />}
                      title={
                        <Text ellipsis style={{ fontSize: 12 }}>
                          {item.title}
                        </Text>
                      }
                      description={
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {item.source} • {new Date(item.timestamp).toLocaleTimeString()}
                        </Text>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>

        {/* 大户交易 */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col span={24}>
            <Card title="大户交易监控" size="small">
              <List
                size="small"
                dataSource={whaleTransactions}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<Avatar icon={<WhatsAppOutlined />} size="small" />}
                      title={
                        <Space>
                          <Text strong>{item.amount.toLocaleString()} {item.currency}</Text>
                          <Tag color="blue">{item.exchange_from || '未知'} → {item.exchange_to || '未知'}</Tag>
                        </Space>
                      }
                      description={
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {new Date(item.timestamp).toLocaleString()}
                        </Text>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>
      </div>
    </MainLayout>
  );
};

export default Dashboard;