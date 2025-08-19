import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, ApiError } from '../types';

// API配置
const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  retries: 3,
};

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证token（如果有）
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加请求时间戳
    config.metadata = { startTime: new Date() };
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算请求耗时
    const endTime = new Date();
    const duration = endTime.getTime() - response.config.metadata?.startTime?.getTime();
    console.log(`API请求耗时: ${duration}ms - ${response.config.url}`);
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 处理401未授权错误
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      // 清除token并重定向到登录页
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }
    
    // 处理网络错误重试
    if (!error.response && originalRequest._retryCount < API_CONFIG.retries) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
      const delay = Math.pow(2, originalRequest._retryCount) * 1000; // 指数退避
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return apiClient(originalRequest);
    }
    
    return Promise.reject(error);
  }
);

// API响应包装器
const handleApiResponse = <T>(response: AxiosResponse<ApiResponse<T>>): T => {
  if (response.data.success) {
    return response.data.data as T;
  } else {
    throw new Error(response.data.message || response.data.error || '请求失败');
  }
};

// API错误处理
const handleApiError = (error: any): ApiError => {
  if (error.response) {
    // 服务器响应错误
    return {
      code: error.response.status.toString(),
      message: error.response.data?.message || error.response.data?.error || '服务器错误',
      details: error.response.data,
    };
  } else if (error.request) {
    // 网络错误
    return {
      code: 'NETWORK_ERROR',
      message: '网络连接失败，请检查网络设置',
      details: error.request,
    };
  } else {
    // 其他错误
    return {
      code: 'UNKNOWN_ERROR',
      message: error.message || '未知错误',
      details: error,
    };
  }
};

// 通用API方法
export const api = {
  // GET请求
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.get<ApiResponse<T>>(url, config);
      return handleApiResponse(response);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // POST请求
  post: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.post<ApiResponse<T>>(url, data, config);
      return handleApiResponse(response);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // PUT请求
  put: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.put<ApiResponse<T>>(url, data, config);
      return handleApiResponse(response);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // DELETE请求
  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.delete<ApiResponse<T>>(url, config);
      return handleApiResponse(response);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // PATCH请求
  patch: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.patch<ApiResponse<T>>(url, data, config);
      return handleApiResponse(response);
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// 具体API方法
export const strategyApi = {
  // 获取策略列表
  getStrategies: () => api.get('/strategies'),
  
  // 获取策略详情
  getStrategy: (id: string) => api.get(`/strategies/${id}`),
  
  // 创建策略
  createStrategy: (data: any) => api.post('/strategies', data),
  
  // 更新策略
  updateStrategy: (id: string, data: any) => api.put(`/strategies/${id}`, data),
  
  // 删除策略
  deleteStrategy: (id: string) => api.delete(`/strategies/${id}`),
  
  // 启动策略
  startStrategy: (id: string) => api.post(`/strategies/${id}/start`),
  
  // 停止策略
  stopStrategy: (id: string) => api.post(`/strategies/${id}/stop`),
  
  // 暂停策略
  pauseStrategy: (id: string) => api.post(`/strategies/${id}/pause`),
  
  // 恢复策略
  resumeStrategy: (id: string) => api.post(`/strategies/${id}/resume`),
};

export const tradingApi = {
  // 获取订单列表
  getOrders: (params?: any) => api.get('/trading/orders', { params }),
  
  // 获取订单详情
  getOrder: (id: string) => api.get(`/trading/orders/${id}`),
  
  // 创建订单
  createOrder: (data: any) => api.post('/trading/orders', data),
  
  // 取消订单
  cancelOrder: (id: string) => api.delete(`/trading/orders/${id}`),
  
  // 获取持仓
  getPositions: () => api.get('/trading/positions'),
  
  // 获取账户信息
  getAccount: () => api.get('/accounts/info'),
  
  // 获取余额
  getBalance: () => api.get('/accounts/balance'),
};

export const dataApi = {
  // 获取市场数据
  getMarketData: (symbol: string, params?: any) => 
    api.get(`/data/market/${symbol}`, { params }),
  
  // 获取历史市场数据
  getHistoricalData: (symbol: string, params?: any) => 
    api.get(`/data/market/${symbol}/historical`, { params }),
  
  // 获取新闻数据
  getNews: (params?: any) => api.get('/data/news', { params }),
  
  // 获取大户交易
  getWhaleAlerts: (params?: any) => api.get('/data/whale-alerts', { params }),
  
  // 获取数据摘要
  getDataSummary: () => api.get('/data/summary'),
  
  // 获取支持的交易对
  getSupportedSymbols: () => api.get('/data/symbols'),
  
  // 订阅交易对
  subscribeSymbol: (symbol: string) => api.post(`/data/symbols/${symbol}/subscribe`),
  
  // 获取数据服务健康状态
  getDataHealth: () => api.get('/data/health'),
};

export const monitoringApi = {
  // 获取系统健康状态
  getSystemHealth: () => api.get('/monitoring/health'),
  
  // 获取系统指标
  getSystemMetrics: () => api.get('/monitoring/metrics'),
  
  // 获取告警列表
  getAlerts: (params?: any) => api.get('/monitoring/alerts', { params }),
  
  // 确认告警
  acknowledgeAlert: (id: string) => api.post(`/monitoring/alerts/${id}/acknowledge`),
};

// 导出默认API客户端
export default apiClient;
