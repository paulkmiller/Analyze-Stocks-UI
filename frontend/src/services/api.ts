import axios from 'axios';
import { Stock, StockData, TradingSignal, BacktestResults, DashboardData } from '../types/Stock';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const stockApi = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Get all stocks
  getStocks: async (): Promise<Stock[]> => {
    const response = await api.get('/api/stocks');
    return response.data;
  },

  // Get stock data
  getStockData: async (ticker: string, params?: {
    limit?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<{ ticker: string; name: string; data: StockData[]; total_records: number }> => {
    const response = await api.get(`/api/stocks/${ticker}/data`, { params });
    return response.data;
  },

  // Get trading signals
  getTradingSignals: async (ticker: string): Promise<TradingSignal> => {
    const response = await api.get(`/api/stocks/${ticker}/signals`);
    return response.data;
  },

  // Get stock chart
  getStockChart: async (ticker: string): Promise<{ ticker: string; chart: string }> => {
    const response = await api.get(`/api/stocks/${ticker}/chart`);
    return response.data;
  },

  // Update stock data
  updateStockData: async (ticker: string) => {
    const response = await api.post(`/api/stocks/${ticker}/update`);
    return response.data;
  },

  // Get backtest results
  getBacktestResults: async (ticker: string): Promise<BacktestResults> => {
    const response = await api.get(`/api/backtest/${ticker}`);
    return response.data;
  },

  // Get dashboard data
  getDashboardData: async (): Promise<DashboardData> => {
    const response = await api.get('/api/dashboard');
    return response.data;
  },
};

export default api;