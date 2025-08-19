import React, { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge, Button, Space, Typography } from 'antd';
import {
  DashboardOutlined,
  TradingViewOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LineChartOutlined,
  DatabaseOutlined,
  MonitorOutlined,
} from '@ant-design/icons';
import { useRouter } from 'next/router';
import { useSystemStore, useSettingsStore } from '../../stores';
import { useWebSocket } from '../../utils/websocket';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const { isConnected, notifications, setConnected } = useSystemStore();
  const { settings } = useSettingsStore();
  const { connect, disconnect, subscribe } = useWebSocket();

  // WebSocket连接管理
  useEffect(() => {
    const connectWS = async () => {
      try {
        await connect();
        setConnected(true);
      } catch (error) {
        console.error('WebSocket连接失败:', error);
        setConnected(false);
      }
    };

    connectWS();

    // 订阅系统状态更新
    const unsubscribe = subscribe('system_status', (data) => {
      console.log('系统状态更新:', data);
    });

    return () => {
      unsubscribe();
      disconnect();
    };
  }, [connect, disconnect, subscribe, setConnected]);

  // 菜单项配置
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/strategies',
      icon: <TradingViewOutlined />,
      label: '策略管理',
    },
    {
      key: '/trading',
      icon: <LineChartOutlined />,
      label: '交易管理',
    },
    {
      key: '/data',
      icon: <DatabaseOutlined />,
      label: '数据中心',
    },
    {
      key: '/monitoring',
      icon: <MonitorOutlined />,
      label: '系统监控',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  // 用户菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '用户设置',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  // 处理菜单点击
  const handleMenuClick = ({ key }: { key: string }) => {
    router.push(key);
  };

  // 处理用户菜单点击
  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'profile':
        router.push('/profile');
        break;
      case 'settings':
        router.push('/user-settings');
        break;
      case 'logout':
        // 处理退出登录
        localStorage.removeItem('auth_token');
        router.push('/login');
        break;
    }
  };

  // 获取当前选中的菜单项
  const getSelectedKeys = () => {
    const pathname = router.pathname;
    return [pathname];
  };

  // 连接状态指示器
  const ConnectionStatus = () => (
    <Space>
      <div
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          backgroundColor: isConnected ? '#52c41a' : '#ff4d4f',
        }}
      />
      <Text type="secondary" style={{ fontSize: 12 }}>
        {isConnected ? '已连接' : '连接断开'}
      </Text>
    </Space>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={240}
        style={{
          background: '#fff',
          borderRight: '1px solid #f0f0f0',
        }}
      >
        {/* Logo */}
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-start',
            padding: collapsed ? 0 : '0 24px',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          {!collapsed && (
            <Text strong style={{ fontSize: 16 }}>
              交易机器人
            </Text>
          )}
          {collapsed && (
            <Text strong style={{ fontSize: 14 }}>
              TR
            </Text>
          )}
        </div>

        {/* 菜单 */}
        <Menu
          mode="inline"
          selectedKeys={getSelectedKeys()}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ border: 'none' }}
        />
      </Sider>

      <Layout>
        {/* 顶部导航 */}
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Space>
            {/* 折叠按钮 */}
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
            />

            {/* 连接状态 */}
            <ConnectionStatus />
          </Space>

          <Space>
            {/* 通知 */}
            <Badge count={notifications.filter(n => !n.read).length} size="small">
              <Button
                type="text"
                icon={<BellOutlined />}
                onClick={() => router.push('/notifications')}
              />
            </Badge>

            {/* 用户菜单 */}
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: handleUserMenuClick,
              }}
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar size="small" icon={<UserOutlined />} />
                <Text>管理员</Text>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        {/* 主内容区 */}
        <Content
          style={{
            margin: 24,
            padding: 24,
            background: '#fff',
            borderRadius: 8,
            minHeight: 'calc(100vh - 112px)',
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
