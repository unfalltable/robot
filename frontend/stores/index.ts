import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { 
  Strategy, 
  Order, 
  Position, 
  Account, 
  MarketData, 
  NewsItem, 
  WhaleTransaction,
  SystemHealth,
  UserSettings,
  Notification
} from '../types';

// 策略状态
interface StrategyState {
  strategies: Strategy[];
  activeStrategy: Strategy | null;
  loading: boolean;
  error: string | null;
  
  setStrategies: (strategies: Strategy[]) => void;
  setActiveStrategy: (strategy: Strategy | null) => void;
  addStrategy: (strategy: Strategy) => void;
  updateStrategy: (id: string, updates: Partial<Strategy>) => void;
  removeStrategy: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useStrategyStore = create<StrategyState>()(
  devtools(
    (set, get) => ({
      strategies: [],
      activeStrategy: null,
      loading: false,
      error: null,

      setStrategies: (strategies) => set({ strategies }),
      
      setActiveStrategy: (strategy) => set({ activeStrategy: strategy }),
      
      addStrategy: (strategy) => set((state) => ({
        strategies: [...state.strategies, strategy]
      })),
      
      updateStrategy: (id, updates) => set((state) => ({
        strategies: state.strategies.map(s => 
          s.id === id ? { ...s, ...updates } : s
        ),
        activeStrategy: state.activeStrategy?.id === id 
          ? { ...state.activeStrategy, ...updates }
          : state.activeStrategy
      })),
      
      removeStrategy: (id) => set((state) => ({
        strategies: state.strategies.filter(s => s.id !== id),
        activeStrategy: state.activeStrategy?.id === id ? null : state.activeStrategy
      })),
      
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
    }),
    { name: 'strategy-store' }
  )
);

// 交易状态
interface TradingState {
  orders: Order[];
  positions: Position[];
  account: Account | null;
  loading: boolean;
  error: string | null;
  
  setOrders: (orders: Order[]) => void;
  addOrder: (order: Order) => void;
  updateOrder: (id: string, updates: Partial<Order>) => void;
  removeOrder: (id: string) => void;
  setPositions: (positions: Position[]) => void;
  updatePosition: (symbol: string, updates: Partial<Position>) => void;
  setAccount: (account: Account | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useTradingStore = create<TradingState>()(
  devtools(
    (set, get) => ({
      orders: [],
      positions: [],
      account: null,
      loading: false,
      error: null,

      setOrders: (orders) => set({ orders }),
      
      addOrder: (order) => set((state) => ({
        orders: [order, ...state.orders]
      })),
      
      updateOrder: (id, updates) => set((state) => ({
        orders: state.orders.map(o => 
          o.id === id ? { ...o, ...updates } : o
        )
      })),
      
      removeOrder: (id) => set((state) => ({
        orders: state.orders.filter(o => o.id !== id)
      })),
      
      setPositions: (positions) => set({ positions }),
      
      updatePosition: (symbol, updates) => set((state) => ({
        positions: state.positions.map(p => 
          p.symbol === symbol ? { ...p, ...updates } : p
        )
      })),
      
      setAccount: (account) => set({ account }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
    }),
    { name: 'trading-store' }
  )
);

// 市场数据状态
interface MarketDataState {
  marketData: Record<string, MarketData[]>;
  currentPrices: Record<string, number>;
  newsItems: NewsItem[];
  whaleTransactions: WhaleTransaction[];
  loading: boolean;
  error: string | null;
  
  setMarketData: (symbol: string, data: MarketData[]) => void;
  addMarketData: (symbol: string, data: MarketData) => void;
  setCurrentPrice: (symbol: string, price: number) => void;
  setNewsItems: (news: NewsItem[]) => void;
  addNewsItem: (news: NewsItem) => void;
  setWhaleTransactions: (transactions: WhaleTransaction[]) => void;
  addWhaleTransaction: (transaction: WhaleTransaction) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useMarketDataStore = create<MarketDataState>()(
  devtools(
    (set, get) => ({
      marketData: {},
      currentPrices: {},
      newsItems: [],
      whaleTransactions: [],
      loading: false,
      error: null,

      setMarketData: (symbol, data) => set((state) => ({
        marketData: { ...state.marketData, [symbol]: data }
      })),
      
      addMarketData: (symbol, data) => set((state) => {
        const existing = state.marketData[symbol] || [];
        const updated = [...existing, data].slice(-1000); // 保留最近1000条
        return {
          marketData: { ...state.marketData, [symbol]: updated }
        };
      }),
      
      setCurrentPrice: (symbol, price) => set((state) => ({
        currentPrices: { ...state.currentPrices, [symbol]: price }
      })),
      
      setNewsItems: (news) => set({ newsItems: news }),
      
      addNewsItem: (news) => set((state) => ({
        newsItems: [news, ...state.newsItems].slice(0, 100) // 保留最近100条
      })),
      
      setWhaleTransactions: (transactions) => set({ whaleTransactions: transactions }),
      
      addWhaleTransaction: (transaction) => set((state) => ({
        whaleTransactions: [transaction, ...state.whaleTransactions].slice(0, 50) // 保留最近50条
      })),
      
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
    }),
    { name: 'market-data-store' }
  )
);

// 系统状态
interface SystemState {
  health: SystemHealth | null;
  notifications: Notification[];
  isConnected: boolean;
  lastUpdate: string | null;
  
  setHealth: (health: SystemHealth | null) => void;
  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
  markNotificationRead: (id: string) => void;
  setConnected: (connected: boolean) => void;
  setLastUpdate: (timestamp: string) => void;
}

export const useSystemStore = create<SystemState>()(
  devtools(
    (set, get) => ({
      health: null,
      notifications: [],
      isConnected: false,
      lastUpdate: null,

      setHealth: (health) => set({ health }),
      
      setNotifications: (notifications) => set({ notifications }),
      
      addNotification: (notification) => set((state) => ({
        notifications: [notification, ...state.notifications]
      })),
      
      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter(n => n.id !== id)
      })),
      
      markNotificationRead: (id) => set((state) => ({
        notifications: state.notifications.map(n => 
          n.id === id ? { ...n, read: true } : n
        )
      })),
      
      setConnected: (connected) => set({ isConnected: connected }),
      setLastUpdate: (timestamp) => set({ lastUpdate: timestamp }),
    }),
    { name: 'system-store' }
  )
);

// 用户设置状态
interface SettingsState {
  settings: UserSettings;
  updateSettings: (updates: Partial<UserSettings>) => void;
  resetSettings: () => void;
}

const defaultSettings: UserSettings = {
  theme: 'light',
  language: 'zh',
  timezone: 'Asia/Shanghai',
  notifications: {
    email: true,
    push: true,
    trading_alerts: true,
    system_alerts: true,
  },
  dashboard: {
    default_layout: 'default',
    auto_refresh: true,
    refresh_interval: 5000,
  },
};

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        settings: defaultSettings,

        updateSettings: (updates) => set((state) => ({
          settings: { ...state.settings, ...updates }
        })),
        
        resetSettings: () => set({ settings: defaultSettings }),
      }),
      {
        name: 'user-settings',
        partialize: (state) => ({ settings: state.settings }),
      }
    ),
    { name: 'settings-store' }
  )
);

// 导出所有store
export {
  useStrategyStore,
  useTradingStore,
  useMarketDataStore,
  useSystemStore,
  useSettingsStore,
};
