import { io, Socket } from 'socket.io-client';
import { WebSocketMessage } from '../types';

// WebSocket配置
const WS_CONFIG = {
  url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
  reconnectAttempts: 5,
  reconnectDelay: 1000,
  timeout: 20000,
};

// WebSocket事件类型
export type WSEventType = 
  | 'market_data'
  | 'news'
  | 'whale_alert'
  | 'order_update'
  | 'strategy_update'
  | 'system_status';

// WebSocket回调函数类型
export type WSCallback = (data: any) => void;

// WebSocket管理器类
class WebSocketManager {
  private socket: Socket | null = null;
  private callbacks: Map<WSEventType, Set<WSCallback>> = new Map();
  private reconnectAttempts = 0;
  private isConnecting = false;
  private connectionPromise: Promise<void> | null = null;

  constructor() {
    // 初始化回调映射
    this.initializeCallbacks();
  }

  private initializeCallbacks() {
    const eventTypes: WSEventType[] = [
      'market_data',
      'news', 
      'whale_alert',
      'order_update',
      'strategy_update',
      'system_status'
    ];
    
    eventTypes.forEach(type => {
      this.callbacks.set(type, new Set());
    });
  }

  // 连接WebSocket
  async connect(): Promise<void> {
    if (this.socket?.connected) {
      return Promise.resolve();
    }

    if (this.isConnecting && this.connectionPromise) {
      return this.connectionPromise;
    }

    this.isConnecting = true;
    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        this.socket = io(WS_CONFIG.url, {
          timeout: WS_CONFIG.timeout,
          transports: ['websocket', 'polling'],
          upgrade: true,
          rememberUpgrade: true,
        });

        // 连接成功
        this.socket.on('connect', () => {
          console.log('WebSocket连接成功');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve();
        });

        // 连接错误
        this.socket.on('connect_error', (error) => {
          console.error('WebSocket连接错误:', error);
          this.isConnecting = false;
          reject(error);
        });

        // 断开连接
        this.socket.on('disconnect', (reason) => {
          console.log('WebSocket断开连接:', reason);
          this.handleDisconnect(reason);
        });

        // 重连
        this.socket.on('reconnect', (attemptNumber) => {
          console.log(`WebSocket重连成功 (尝试 ${attemptNumber})`);
          this.reconnectAttempts = 0;
        });

        this.socket.on('reconnect_error', (error) => {
          console.error('WebSocket重连失败:', error);
          this.reconnectAttempts++;
        });

        // 注册数据事件监听器
        this.registerDataListeners();

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  // 注册数据事件监听器
  private registerDataListeners() {
    if (!this.socket) return;

    // 市场数据
    this.socket.on('market_data', (data: WebSocketMessage) => {
      this.notifyCallbacks('market_data', data);
    });

    // 新闻数据
    this.socket.on('news', (data: WebSocketMessage) => {
      this.notifyCallbacks('news', data);
    });

    // 大户交易
    this.socket.on('whale_alert', (data: WebSocketMessage) => {
      this.notifyCallbacks('whale_alert', data);
    });

    // 订单更新
    this.socket.on('order_update', (data: WebSocketMessage) => {
      this.notifyCallbacks('order_update', data);
    });

    // 策略更新
    this.socket.on('strategy_update', (data: WebSocketMessage) => {
      this.notifyCallbacks('strategy_update', data);
    });

    // 系统状态
    this.socket.on('system_status', (data: any) => {
      this.notifyCallbacks('system_status', data);
    });
  }

  // 处理断开连接
  private handleDisconnect(reason: string) {
    if (reason === 'io server disconnect') {
      // 服务器主动断开，需要手动重连
      this.reconnect();
    }
    // 其他情况会自动重连
  }

  // 手动重连
  private async reconnect() {
    if (this.reconnectAttempts >= WS_CONFIG.reconnectAttempts) {
      console.error('WebSocket重连次数超限，停止重连');
      return;
    }

    this.reconnectAttempts++;
    const delay = WS_CONFIG.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`WebSocket将在 ${delay}ms 后重连 (尝试 ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('WebSocket重连失败:', error);
      });
    }, delay);
  }

  // 断开连接
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.isConnecting = false;
    this.connectionPromise = null;
    this.reconnectAttempts = 0;
  }

  // 订阅事件
  subscribe(eventType: WSEventType, callback: WSCallback): () => void {
    const callbacks = this.callbacks.get(eventType);
    if (callbacks) {
      callbacks.add(callback);
    }

    // 返回取消订阅函数
    return () => {
      const callbacks = this.callbacks.get(eventType);
      if (callbacks) {
        callbacks.delete(callback);
      }
    };
  }

  // 取消订阅
  unsubscribe(eventType: WSEventType, callback: WSCallback) {
    const callbacks = this.callbacks.get(eventType);
    if (callbacks) {
      callbacks.delete(callback);
    }
  }

  // 通知回调函数
  private notifyCallbacks(eventType: WSEventType, data: any) {
    const callbacks = this.callbacks.get(eventType);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`WebSocket回调执行错误 (${eventType}):`, error);
        }
      });
    }
  }

  // 发送消息
  emit(event: string, data?: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket未连接，无法发送消息');
    }
  }

  // 获取连接状态
  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  // 获取连接ID
  get connectionId(): string | undefined {
    return this.socket?.id;
  }
}

// 创建全局WebSocket管理器实例
const wsManager = new WebSocketManager();

// 导出WebSocket钩子
export const useWebSocket = () => {
  return {
    connect: () => wsManager.connect(),
    disconnect: () => wsManager.disconnect(),
    subscribe: (eventType: WSEventType, callback: WSCallback) => 
      wsManager.subscribe(eventType, callback),
    unsubscribe: (eventType: WSEventType, callback: WSCallback) => 
      wsManager.unsubscribe(eventType, callback),
    emit: (event: string, data?: any) => wsManager.emit(event, data),
    isConnected: wsManager.isConnected,
    connectionId: wsManager.connectionId,
  };
};

// 导出WebSocket管理器
export default wsManager;
