export interface Stock {
  ticker: string;
  name: string;
  start_date: string;
  has_data: boolean;
  last_updated?: string;
}

export interface StockData {
  timestamp: string;
  High: number;
  Low: number;
  Open: number;
  Close: number;
  Volume: number;
}

export interface TradingSignal {
  ticker: string;
  name: string;
  signal: 'Buy' | 'Sell' | 'Hold';
  current_price: number;
  entry_price?: number;
  stop_loss?: number;
  take_profit?: number;
  atr?: number;
  timestamp: string;
  parameters: {
    atr_period: number;
    breakout_high_period: number;
    breakout_low_period: number;
    atr_multiplier: number;
  };
}

export interface BacktestResults {
  ticker: string;
  name: string;
  total_profit: number;
  number_of_trades: number;
  profit_per_trade: number;
}

export interface DashboardStock {
  ticker: string;
  name: string;
  has_data: boolean;
  signal?: 'Buy' | 'Sell' | 'Hold';
  current_price?: number;
  change_percent?: number;
  last_updated?: string;
}

export interface DashboardData {
  stocks: DashboardStock[];
  total_stocks: number;
  active_stocks: number;
  timestamp: string;
}