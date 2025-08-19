import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Typography,
  Row,
  Col,
  Statistic,
  Tabs,
  List,
  Avatar,
  Tag,
  Space,
  Button,
  Select
} from 'antd';
import {
  ReloadOutlined,
  LineChartOutlined,
  NewsOutlined,
  DollarOutlined,
  TrendingUpOutlined
} from '@ant-design/icons';
import MainLayout from '../components/Layout/MainLayout';
import { MarketData, NewsItem, WhaleTransaction } from '../types';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

const DataCenter: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [whaleTransactions, setWhaleTransactions] = useState<WhaleTransaction[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('BTC/USDT');

  // 模拟市场数据
  const mockMarketData: MarketData[] = [
    {
      symbol: 'BTC/USDT',
      timestamp: '2024-01-01T10:00:00Z',
      open: 45000,
      high: 46500,
      low: 44800,
      close: 46200,
      volume: 1250.5,
      timeframe: '1h'
    },
    {
      symbol: 'ETH/USDT',
      timestamp: '2024-01-01T10:00:00Z',
      open: 2800,
      high: 2850,
      low: 2750,
      close: 2820,
      volume: 8500.2,
      timeframe: '1h'
    },
    {
      symbol: 'BNB/USDT',
      timestamp: '2024-01-01T10:00:00Z',
      open: 300,
      high: 305,
      low: 298,
      close: 302,
      volume: 15600.8,
      timeframe: '1h'
    }
  ];

  // 模拟新闻数据
  const mockNews: NewsItem[] = [
    {
      id: '1',
      title: 'Bitcoin突破46000美元，创本月新高',
      content: 'Bitcoin价格在今日突破46000美元关键阻力位，市场情绪乐观...',
      source: 'CoinDesk',
      url: 'https://example.com/news/1',
      timestamp: '2024-01-01T10:30:00Z',
      sentiment: 0.8,
      relevance: 0.9,
      keywords: ['bitcoin', 'price', 'breakout', 'bullish']
    },
    {
      id: '2',
      title: '以太坊2.0质押量突破3000万ETH',
      content: '以太坊2.0网络的质押量达到新的里程碑，显示出投资者对网络的信心...',
      source: 'CoinTelegraph',
      url: 'https://example.com/news/2',
      timestamp: '2024-01-01T09:45:00Z',
      sentiment: 0.7,
      relevance: 0.8,
      keywords: ['ethereum', 'staking', 'milestone', 'network']
    },
    {
      id: '3',
      title: '美国SEC考虑批准更多比特币ETF',
      content: 'SEC正在审查多个比特币ETF申请，可能会在未来几个月内做出决定...',
      source: 'Bloomberg',
      url: 'https://example.com/news/3',
      timestamp: '2024-01-01T08:20:00Z',
      sentiment: 0.6,
      relevance: 0.9,
      keywords: ['SEC', 'ETF', 'approval', 'regulation']
    }
  ];

  // 模拟大户交易数据
  const mockWhaleTransactions: WhaleTransaction[] = [
    {
      id: '1',
      transaction_hash: '0x1234567890abcdef...',
      from_address: '0xabcdef1234567890...',
      to_address: '0x9876543210fedcba...',
      amount: 1000,
      currency: 'BTC',
      timestamp: '2024-01-01T10:15:00Z',
      exchange_from: 'Binance',
      exchange_to: 'Coinbase'
    },
    {
      id: '2',
      transaction_hash: '0xfedcba0987654321...',
      from_address: '0x1111222233334444...',
      to_address: '0x5555666677778888...',
      amount: 5000,
      currency: 'ETH',
      timestamp: '2024-01-01T09:30:00Z',
      exchange_from: 'Kraken',
      exchange_to: 'Unknown'
    },
    {
      id: '3',
      transaction_hash: '0x9999888877776666...',
      from_address: '0xaaabbbcccdddeeef...',
      to_address: '0xfffeeeddccbbbaaa...',
      amount: 500,
      currency: 'BTC',
      timestamp: '2024-01-01T08:45:00Z',
      exchange_from: 'Unknown',
      exchange_to: 'Bitfinex'
    }
  ];

  useEffect(() => {
    setMarketData(mockMarketData);
    setNewsItems(mockNews);
    setWhaleTransactions(mockWhaleTransactions);
  }, []);

  // 刷新数据
  const handleRefresh = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      // 这里会调用API刷新数据
    } catch (error) {
      console.error('刷新数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 市场数据表格列
  const marketDataColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <Tag color="blue">{symbol}</Tag>,
    },
    {
      title: '开盘价',
      dataIndex: 'open',
      key: 'open',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '最高价',
      dataIndex: 'high',
      key: 'high',
      render: (price: number) => (
        <Text style={{ color: '#3f8600' }}>${price.toFixed(2)}</Text>
      ),
    },
    {
      title: '最低价',
      dataIndex: 'low',
      key: 'low',
      render: (price: number) => (
        <Text style={{ color: '#cf1322' }}>${price.toFixed(2)}</Text>
      ),
    },
    {
      title: '收盘价',
      dataIndex: 'close',
      key: 'close',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      render: (volume: number) => volume.toLocaleString(),
    },
    {
      title: '涨跌幅',
      key: 'change',
      render: (_, record: MarketData) => {
        const change = ((record.close - record.open) / record.open) * 100;
        return (
          <Text style={{ color: change >= 0 ? '#3f8600' : '#cf1322' }}>
            {change >= 0 ? '+' : ''}{change.toFixed(2)}%
          </Text>
        );
      },
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (time: string) => new Date(time).toLocaleString(),
    },
  ];

  // 大户交易表格列
  const whaleColumns = [
    {
      title: '金额',
      key: 'amount_display',
      render: (_, record: WhaleTransaction) => (
        <Space>
          <Text strong style={{ color: '#1890ff' }}>
            {record.amount.toLocaleString()} {record.currency}
          </Text>
        </Space>
      ),
    },
    {
      title: '方向',
      key: 'direction',
      render: (_, record: WhaleTransaction) => (
        <Space>
          <Tag color="orange">{record.exchange_from || '未知地址'}</Tag>
          <span>→</span>
          <Tag color="green">{record.exchange_to || '未知地址'}</Tag>
        </Space>
      ),
    },
    {
      title: '交易哈希',
      dataIndex: 'transaction_hash',
      key: 'transaction_hash',
      render: (hash: string) => (
        <Text code style={{ fontSize: 12 }}>
          {hash.substring(0, 10)}...{hash.substring(hash.length - 8)}
        </Text>
      ),
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (time: string) => new Date(time).toLocaleString(),
    },
  ];

  // 计算统计数据
  const stats = {
    totalSymbols: marketData.length,
    totalNews: newsItems.length,
    totalWhaleTransactions: whaleTransactions.length,
    avgSentiment: newsItems.reduce((sum, item) => sum + (item.sentiment || 0), 0) / newsItems.length,
  };

  return (
    <MainLayout>
      <div>
        {/* 标题和操作 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>数据中心</Title>
          <Space>
            <Select
              value={selectedSymbol}
              onChange={setSelectedSymbol}
              style={{ width: 120 }}
            >
              <Option value="BTC/USDT">BTC/USDT</Option>
              <Option value="ETH/USDT">ETH/USDT</Option>
              <Option value="BNB/USDT">BNB/USDT</Option>
            </Select>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={loading}
            >
              刷新
            </Button>
          </Space>
        </div>

        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="监控币种" 
                value={stats.totalSymbols} 
                prefix={<LineChartOutlined />}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="新闻数量" 
                value={stats.totalNews} 
                prefix={<NewsOutlined />}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="大户交易" 
                value={stats.totalWhaleTransactions} 
                prefix={<DollarOutlined />}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="平均情绪" 
                value={stats.avgSentiment} 
                precision={2}
                valueStyle={{ color: stats.avgSentiment >= 0.5 ? '#3f8600' : '#cf1322' }}
                prefix={<TrendingUpOutlined />}
              />
            </Card>
          </Col>
        </Row>

        {/* 主要内容 */}
        <Card>
          <Tabs defaultActiveKey="market">
            <TabPane tab="市场数据" key="market">
              <Table
                columns={marketDataColumns}
                dataSource={marketData}
                rowKey="symbol"
                loading={loading}
                pagination={false}
              />
            </TabPane>
            
            <TabPane tab="新闻资讯" key="news">
              <List
                dataSource={newsItems}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<Avatar icon={<NewsOutlined />} />}
                      title={
                        <Space>
                          <Text strong>{item.title}</Text>
                          <Tag color={item.sentiment && item.sentiment > 0.6 ? 'green' : item.sentiment && item.sentiment < 0.4 ? 'red' : 'orange'}>
                            情绪: {item.sentiment ? (item.sentiment * 100).toFixed(0) : 'N/A'}%
                          </Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size={4}>
                          <Text>{item.content}</Text>
                          <Space>
                            <Text type="secondary">{item.source}</Text>
                            <Text type="secondary">•</Text>
                            <Text type="secondary">{new Date(item.timestamp).toLocaleString()}</Text>
                            <Text type="secondary">•</Text>
                            <Text type="secondary">相关度: {item.relevance ? (item.relevance * 100).toFixed(0) : 'N/A'}%</Text>
                          </Space>
                          {item.keywords && (
                            <Space wrap>
                              {item.keywords.map(keyword => (
                                <Tag key={keyword} size="small">{keyword}</Tag>
                              ))}
                            </Space>
                          )}
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </TabPane>
            
            <TabPane tab="大户监控" key="whale">
              <Table
                columns={whaleColumns}
                dataSource={whaleTransactions}
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
          </Tabs>
        </Card>
      </div>
    </MainLayout>
  );
};

export default DataCenter;
