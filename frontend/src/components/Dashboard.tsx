import React, { useState, useEffect } from 'react';
import { stockApi } from '../services/api';
import { DashboardData, DashboardStock } from '../types/Stock';
import { useTheme } from '../contexts/ThemeContext';
import { TrendingUp, RefreshCw, AlertCircle, Download, Info, X, DollarSign, Percent, Moon, Sun } from 'lucide-react';

interface DashboardProps {
  onStockSelect?: (ticker: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onStockSelect }) => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [retryingTicker, setRetryingTicker] = useState<string | null>(null);
  const [stockErrors, setStockErrors] = useState<Record<string, string>>({});
  const [showInfoModal, setShowInfoModal] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setError(null);
      setLoading(true);
      console.log('Fetching dashboard data from API...');
      const data = await stockApi.getDashboardData();
      console.log('Dashboard data received:', data);
      console.log('Data type:', typeof data);
      console.log('Stocks array:', data?.stocks);
      console.log('Stocks length:', data?.stocks?.length);
      setDashboardData(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // new comment about new thing we're making
  // TODO: make the new thing
  // TODO:

  const retryStockData = async (ticker: string) => {
    try {
      setRetryingTicker(ticker);
      setStockErrors(prev => ({ ...prev, [ticker]: '' }));

      console.log(`Retrying data download for ${ticker}...`);
      await stockApi.updateStockData(ticker);

      // Refresh dashboard data to show updated information
      const data = await stockApi.getDashboardData();
      setDashboardData(data);
      setLastUpdated(new Date());

      console.log(`Successfully updated data for ${ticker}`);
    } catch (err) {
      console.error(`Error updating ${ticker}:`, err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to update stock data';
      setStockErrors(prev => ({ ...prev, [ticker]: errorMessage }));
    } finally {
      setRetryingTicker(null);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);



  const formatPrice = (price?: number) => {
    return (price && !isNaN(price)) ? `$${price.toFixed(2)}` : 'N/A';
  };

  const formatPercentage = (percent?: number) => {
    if (!percent || isNaN(percent)) return 'N/A';
    const sign = percent >= 0 ? '+' : '';
    const color = percent >= 0 ? 'text-green-600' : 'text-red-600';
    return <span className={color}>{sign}{percent.toFixed(2)}%</span>;
  };

  const calculatePortfolioMetrics = () => {
    if (!dashboardData?.stocks) return { totalValue: 0, avgChange: 0, topPerformer: null, topPerformerChange: 0 };

    const validStocks = dashboardData.stocks.filter(stock =>
      stock.has_data && stock.current_price && !isNaN(stock.current_price) &&
      stock.change_percent !== null && !isNaN(stock.change_percent)
    );

    if (validStocks.length === 0) return { totalValue: 0, avgChange: 0, topPerformer: null, topPerformerChange: 0 };

    // Calculate total portfolio value (assuming 1 share each for simplicity)
    const totalValue = validStocks.reduce((sum, stock) => sum + (stock.current_price || 0), 0);

    // Calculate average change percentage
    const avgChange = validStocks.reduce((sum, stock) => sum + (stock.change_percent || 0), 0) / validStocks.length;

    // Find top performer
    const topPerformer = validStocks.reduce((best, current) => {
      const currentChange = current.change_percent || -Infinity;
      const bestChange = best.change_percent || -Infinity;
      return currentChange > bestChange ? current : best;
    });

    return {
      totalValue,
      avgChange,
      topPerformer: topPerformer.ticker,
      topPerformerChange: topPerformer.change_percent || 0
    };
  };

  console.log('Dashboard render - loading:', loading, 'error:', error, 'dashboardData:', dashboardData);

  if (loading) {
    return (
      <div className={`flex justify-center items-center h-64 min-h-screen p-6 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className={`ml-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen p-6 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className={`border rounded-lg p-6 ${isDarkMode ? 'bg-red-900 border-red-700' : 'bg-red-50 border-red-200'}`}>
          <div className="flex items-center">
            <AlertCircle className="w-6 h-6 text-red-500 mr-3" />
            <div>
              <h3 className={`font-semibold ${isDarkMode ? 'text-red-300' : 'text-red-800'}`}>Error Loading Dashboard</h3>
              <p className={`mt-1 ${isDarkMode ? 'text-red-200' : 'text-red-700'}`}>{error}</p>
              <button
                onClick={fetchDashboardData}
                className="mt-3 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 min-h-screen p-6 transition-colors duration-200 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="text-left pl-2">
          <h1 className={`text-3xl font-bold text-left ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Trading Dashboard</h1>
          <p className={`mt-2 text-left ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            Turtle Trading Strategy - Stock Analysis & Signals
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleDarkMode}
            className={`flex items-center p-2 rounded-lg transition-colors ${
              isDarkMode
                ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setShowInfoModal(true)}
            className={`flex items-center p-2 rounded-lg transition-colors ${
              isDarkMode
                ? 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title="What does the refresh button do?"
          >
            <Info className="w-4 h-4" />
          </button>
          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {dashboardData && (() => {
        const metrics = calculatePortfolioMetrics();
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className={`rounded-lg shadow-md p-6 border ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Portfolio Value</p>
                  <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    ${metrics.totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                  <p className={`text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>Based on 1 share each</p>
                </div>
                <div className={`p-3 rounded-full ${isDarkMode ? 'bg-blue-900' : 'bg-blue-100'}`}>
                  <DollarSign className={`w-6 h-6 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                </div>
              </div>
            </div>

            <div className={`rounded-lg shadow-md p-6 border ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Average Change</p>
                  <p className={`text-2xl font-bold ${metrics.avgChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {metrics.avgChange >= 0 ? '+' : ''}{metrics.avgChange.toFixed(2)}%
                  </p>
                  <p className={`text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>Daily performance</p>
                </div>
                <div className={`p-3 rounded-full ${
                  metrics.avgChange >= 0
                    ? (isDarkMode ? 'bg-green-900' : 'bg-green-100')
                    : (isDarkMode ? 'bg-red-900' : 'bg-red-100')
                }`}>
                  <Percent className={`w-6 h-6 ${
                    metrics.avgChange >= 0
                      ? (isDarkMode ? 'text-green-400' : 'text-green-600')
                      : (isDarkMode ? 'text-red-400' : 'text-red-600')
                  }`} />
                </div>
              </div>
            </div>

            <div className={`rounded-lg shadow-md p-6 border ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Top Performer</p>
                  <p className={`text-lg font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    {metrics.topPerformer || 'N/A'}
                  </p>
                  {metrics.topPerformer && (
                    <p className={`text-sm font-medium ${metrics.topPerformerChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {metrics.topPerformerChange >= 0 ? '+' : ''}{metrics.topPerformerChange.toFixed(2)}%
                    </p>
                  )}
                </div>
                <div className={`p-3 rounded-full ${isDarkMode ? 'bg-yellow-900' : 'bg-yellow-100'}`}>
                  <TrendingUp className={`w-6 h-6 ${isDarkMode ? 'text-yellow-400' : 'text-yellow-600'}`} />
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Stocks Table */}
      <div className={`rounded-lg shadow-md border overflow-hidden ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
        <div className={`px-6 py-4 border-b ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <h2 className={`text-xl font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Stock Overview</h2>
          {!dashboardData && (
            <p className="text-red-600 text-sm mt-2">⚠️ No data received from API. Check console for errors.</p>
          )}
        </div>
        {dashboardData && dashboardData.stocks && dashboardData.stocks.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className={isDarkMode ? 'bg-gray-700' : 'bg-gray-50'}>
                <tr>
                  <th className={`px-6 py-3 text-center text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>
                    Stock
                  </th>
                  <th className={`px-6 py-3 text-center text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>
                    Price
                  </th>
                  <th className={`px-6 py-3 text-center text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>
                    Change
                  </th>
                  <th className={`px-6 py-3 text-center text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>
                    Status
                  </th>
                  <th className={`px-6 py-3 text-center text-xs font-medium uppercase tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className={`divide-y ${isDarkMode ? 'bg-gray-800 divide-gray-700' : 'bg-white divide-gray-200'}`}>
                {dashboardData.stocks?.map((stock: DashboardStock) => (
                  <tr
                    key={stock.ticker}
                    className={isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}
                  >
                    <td
                      className="px-6 py-4 whitespace-nowrap cursor-pointer text-center"
                      onClick={() => onStockSelect?.(stock.ticker)}
                    >
                      <div>
                        <div className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{stock.name}</div>
                        <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>{stock.ticker}</div>
                        {stockErrors[stock.ticker] && (
                          <div className="text-xs text-red-400 mt-1">
                            {stockErrors[stock.ticker]}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm text-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                      {formatPrice(stock.current_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                      {formatPercentage(stock.change_percent)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="flex justify-center">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          stock.has_data
                            ? (isDarkMode ? 'bg-green-900 text-green-300' : 'bg-green-100 text-green-800')
                            : (isDarkMode ? 'bg-red-900 text-red-300' : 'bg-red-100 text-red-800')
                        }`}>
                          {stock.has_data ? 'Active' : 'No Data'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="flex items-center justify-center space-x-2">
                        {!stock.has_data && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              retryStockData(stock.ticker);
                            }}
                            disabled={retryingTicker === stock.ticker}
                            className="flex items-center px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {retryingTicker === stock.ticker ? (
                              <>
                                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                                Updating...
                              </>
                            ) : (
                              <>
                                <Download className="w-3 h-3 mr-1" />
                                Download
                              </>
                            )}
                          </button>
                        )}
                        {stock.has_data && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              retryStockData(stock.ticker);
                            }}
                            disabled={retryingTicker === stock.ticker}
                            className="flex items-center px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {retryingTicker === stock.ticker ? (
                              <>
                                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                                Updating...
                              </>
                            ) : (
                              <>
                                <RefreshCw className="w-3 h-3 mr-1" />
                                Update
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {(!dashboardData || !dashboardData.stocks || dashboardData.stocks.length === 0) && (
          <div className="px-6 py-8 text-center">
            <p className="text-gray-500">No stock data available. Check API connection.</p>
          </div>
        )}
      </div>

      {/* Info Modal */}
      {showInfoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`rounded-lg p-6 max-w-md mx-4 ${isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}`}>
            <div className="flex justify-between items-center mb-4">
              <h2 className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Refresh Button Info</h2>
              <button
                onClick={() => setShowInfoModal(false)}
                className={`transition-colors ${isDarkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className={`space-y-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              <div>
                <h3 className={`font-medium mb-1 flex items-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh Button (Top-Right)
                </h3>
                <p>Refreshes the dashboard view with data already stored in the system. Fast - no external API calls.</p>
              </div>
              <div>
                <h3 className={`font-medium mb-1 flex items-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  <Download className="w-4 h-4 mr-2" />
                  Download/Update Buttons (Per Stock)
                </h3>
                <p>Downloads fresh data from Yahoo Finance for individual stocks. Use when a specific ticker needs new data.</p>
              </div>
              <div className={`p-3 rounded ${isDarkMode ? 'bg-blue-900 bg-opacity-50' : 'bg-blue-50'}`}>
                <p className={`font-medium flex items-center ${isDarkMode ? 'text-blue-300' : 'text-blue-800'}`}>
                  <Info className="w-4 h-4 mr-2" />
                  Typical Workflow:
                </p>
                <p className={isDarkMode ? 'text-blue-200' : 'text-blue-700'}>1. Click individual "Download" for missing data<br />
                2. Click "Refresh" to see updated dashboard</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;