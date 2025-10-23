import { useState } from 'react';
import Dashboard from './components/Dashboard';
import StockDetail from './components/StockDetail';
import { useTheme } from './contexts/ThemeContext';
import './App.css';

interface AppState {
  currentView: 'dashboard' | 'stock-detail';
  selectedTicker?: string;
}

function App() {
  const { isDarkMode } = useTheme();
  const [appState, setAppState] = useState<AppState>({
    currentView: 'dashboard'
  });

  const showStockDetail = (ticker: string) => {
    setAppState({
      currentView: 'stock-detail',
      selectedTicker: ticker
    });
  };

  const showDashboard = () => {
    setAppState({
      currentView: 'dashboard'
    });
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-100'}`}>
      <div className={`container mx-auto px-4 py-8 transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
        {appState.currentView === 'dashboard' && (
          <Dashboard onStockSelect={showStockDetail} />
        )}

        {appState.currentView === 'stock-detail' && appState.selectedTicker && (
          <StockDetail
            ticker={appState.selectedTicker}
            onBack={showDashboard}
          />
        )}
      </div>
    </div>
  );
}

export default App
