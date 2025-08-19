// 基础类型定义

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// 交易相关类型
export enum OrderSide {
  BUY = 'buy',
  SELL = 'sell'
}

export enum OrderType {
  MARKET = 'market',
  LIMIT = 'limit',
  STOP = 'stop',
  STOP_LIMIT = 'stop_limit'
}

export enum OrderStatus {
  PENDING = 'pending',
  OPEN = 'open',
  FILLED = 'filled',
  CANCELLED = 'cancelled',
  REJECTED = 'rejected'
}

export interface Order {
  id: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  amount: number;
  price?: number;
  stop_price?: number;
  status: OrderStatus;
  filled_amount: number;
  remaining_amount: number;
  created_at: string;
  updated_at: string;
}

export interface Position {
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  realized_pnl: number;
  margin: number;
  percentage: number;
  created_at: string;
}

export interface Account {
  id: string;
  name: string;
  exchange: string;
  balance: number;
  available_balance: number;
  margin_balance: number;
  total_pnl: number;
  daily_pnl: number;
  positions: Position[];
  created_at: string;
}

// 策略相关类型
export enum StrategyStatus {
  STOPPED = 'stopped',
  RUNNING = 'running',
  PAUSED = 'paused',
  ERROR = 'error'
}

export interface StrategyParameter {
  name: string;
  type: 'number' | 'string' | 'boolean' | 'select';
  value: any;
  default_value: any;
  description: string;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
}

export interface Strategy {
  id: string;
  name: string;
  description: string;
  status: StrategyStatus;
  symbol: string;
  parameters: StrategyParameter[];
  performance: {
    total_return: number;
    daily_return: number;
    max_drawdown: number;
    sharpe_ratio: number;
    win_rate: number;
    total_trades: number;
  };
  created_at: string;
  updated_at: string;
  started_at?: string;
  stopped_at?: string;
}

// 市场数据类型
export interface MarketData {
  symbol: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  timeframe: string;
}

export interface TickerData {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  high_24h: number;
  low_24h: number;
  timestamp: string;
}

// 新闻数据类型
export interface NewsItem {
  id: string;
  title: string;
  content: string;
  source: string;
  url?: string;
  timestamp: string;
  sentiment?: number;
  relevance?: number;
  keywords: string[];
}

// 大户交易类型
export interface WhaleTransaction {
  id: string;
  transaction_hash: string;
  from_address: string;
  to_address: string;
  amount: number;
  currency: string;
  timestamp: string;
  exchange_from?: string;
  exchange_to?: string;
}

// 图表数据类型
export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface CandlestickData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 系统监控类型
export interface SystemHealth {
  status: 'healthy' | 'warning' | 'error';
  uptime: number;
  memory_usage: number;
  cpu_usage: number;
  active_strategies: number;
  active_connections: number;
  last_update: string;
}

export interface DataSourceHealth {
  name: string;
  status: 'connected' | 'disconnected' | 'error';
  last_update: string;
  error_message?: string;
}

// 用户界面类型
export interface DashboardWidget {
  id: string;
  type: 'chart' | 'table' | 'metric' | 'news' | 'orders';
  title: string;
  position: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
  config: any;
}

export interface DashboardLayout {
  id: string;
  name: string;
  widgets: DashboardWidget[];
  is_default: boolean;
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: 'market_data' | 'news' | 'whale_alert' | 'order_update' | 'strategy_update';
  symbol?: string;
  timestamp: string;
  data: any;
}

// 表单类型
export interface StrategyFormData {
  name: string;
  description: string;
  symbol: string;
  parameters: Record<string, any>;
}

export interface OrderFormData {
  symbol: string;
  side: OrderSide;
  type: OrderType;
  amount: number;
  price?: number;
  stop_price?: number;
}

// 分页类型
export interface PaginationParams {
  page: number;
  page_size: number;
  total?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

// 过滤和排序类型
export interface FilterParams {
  symbol?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  [key: string]: any;
}

export interface SortParams {
  field: string;
  order: 'asc' | 'desc';
}

// 通知类型
export interface Notification {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// 设置类型
export interface UserSettings {
  theme: 'light' | 'dark';
  language: 'zh' | 'en';
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    trading_alerts: boolean;
    system_alerts: boolean;
  };
  dashboard: {
    default_layout: string;
    auto_refresh: boolean;
    refresh_interval: number;
  };
}

// API配置类型
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
}

// 错误类型
export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export interface ValidationError {
  field: string;
  message: string;
}
