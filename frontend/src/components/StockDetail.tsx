import React, { useState, useEffect } from 'react';
import { stockApi } from '../services/api';
import { TradingSignal, BacktestResults } from '../types/Stock';
import { TrendingUp, TrendingDown, Minus, RefreshCw, AlertCircle, BarChart3 } from 'lucide-react';

interface StockDetailProps {
  ticker: string;
  onBack: () => void;
}

const StockDetail: React.FC<StockDetailProps> = ({ ticker, onBack }) => {
  const [signal, setSignal] = useState<TradingSignal | null>(null);
  const [backtest, setBacktest] = useState<BacktestResults | null>(null);
  const [chart, setChart] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStockDetail = async () => {
    try {
      setError(null);
      setLoading(true);

      // Fetch signal data
      try {
        const signalData = await stockApi.getTradingSignals(ticker);
        setSignal(signalData);
      } catch (err) {
        console.warn(`Could not fetch signals for ${ticker}:`, err);
      }

      // Fetch backtest results
      try {
        const backtestData = await stockApi.getBacktestResults(ticker);
        setBacktest(backtestData);
      } catch (err) {
        console.warn(`Could not fetch backtest results for ${ticker}:`, err);
      }

      // Fetch chart
      try {
        const chartData = await stockApi.getStockChart(ticker);
        setChart(chartData.chart);
      } catch (err) {
        console.warn(`Could not fetch chart for ${ticker}:`, err);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stock details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStockDetail();
  }, [ticker]);

  const getSignalIcon = (signalType: string) => {
    switch (signalType) {
      case 'Buy':
        return <TrendingUp className="w-6 h-6 text-green-500" />;
      case 'Sell':
        return <TrendingDown className="w-6 h-6 text-red-500" />;
      case 'Hold':
        return <Minus className="w-6 h-6 text-gray-500" />;
      default:
        return <AlertCircle className="w-6 h-6 text-gray-400" />;
    }
  };

  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case 'Buy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Sell':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'Hold':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Loading stock details...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Dashboard
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {signal?.name || ticker}
            </h1>
            <p className="text-gray-600">{ticker}</p>
          </div>
        </div>
        <button
          onClick={fetchStockDetail}
          className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* Trading Signal Card */}
      {signal && (
        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Current Trading Signal
            </h2>
            <div className={`px-4 py-2 rounded-lg border ${getSignalColor(signal.signal)} flex items-center`}>
              {getSignalIcon(signal.signal)}
              <span className="ml-2 font-semibold">{signal.signal}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-600">Current Price</p>
              <p className="text-2xl font-bold text-gray-900">${signal.current_price.toFixed(2)}</p>
            </div>

            {signal.entry_price && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-600">Entry Price</p>
                <p className="text-2xl font-bold text-green-600">${signal.entry_price.toFixed(2)}</p>
              </div>
            )}

            {signal.stop_loss && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-600">Stop Loss</p>
                <p className="text-2xl font-bold text-red-600">${signal.stop_loss.toFixed(2)}</p>
              </div>
            )}

            {signal.take_profit && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-600">Take Profit</p>
                <p className="text-2xl font-bold text-green-600">${signal.take_profit.toFixed(2)}</p>
              </div>
            )}

            {signal.atr && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-600">ATR</p>
                <p className="text-2xl font-bold text-blue-600">${signal.atr.toFixed(2)}</p>
              </div>
            )}

            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-600">Last Updated</p>
              <p className="text-sm text-gray-700">
                {new Date(signal.timestamp).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Parameters */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Trading Parameters</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">High Breakout</p>
                <p className="font-semibold">{signal.parameters.breakout_high_period} days</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Low Breakout</p>
                <p className="font-semibold">{signal.parameters.breakout_low_period} days</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">ATR Period</p>
                <p className="font-semibold">{signal.parameters.atr_period} days</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">ATR Multiplier</p>
                <p className="font-semibold">{signal.parameters.atr_multiplier}x</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Backtest Results */}
      {backtest && (
        <div className="bg-white rounded-lg shadow-md border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Backtest Results (2022-2024)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Total Profit</p>
              <p className={`text-2xl font-bold ${backtest.total_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${backtest.total_profit.toFixed(2)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Number of Trades</p>
              <p className="text-2xl font-bold text-gray-900">{backtest.number_of_trades}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Profit per Trade</p>
              <p className={`text-2xl font-bold ${backtest.profit_per_trade >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${backtest.profit_per_trade.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Price Chart */}
      {chart && (
        <div className="bg-white rounded-lg shadow-md border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Price Chart (Last 200 Days)</h2>
          <div className="flex justify-center">
            <img
              src={chart}
              alt={`${ticker} Price Chart`}
              className="max-w-full h-auto rounded-lg"
            />
          </div>
        </div>
      )}

      {/* No Data Message */}
      {!signal && !backtest && !chart && !loading && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="w-6 h-6 text-yellow-500 mr-3" />
            <div>
              <h3 className="text-yellow-800 font-semibold">No Data Available</h3>
              <p className="text-yellow-700 mt-1">
                No trading data is currently available for {ticker}.
                This might be because optimization hasn't been run yet or data is still being collected.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockDetail;