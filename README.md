# Analyze-Stocks

A **Turtle Trading Strategy** implementation for stock analysis that helps determine optimal buy/sell timing for stocks. This project implements the famous Turtle Trading system developed by Richard Dennis, using technical indicators to generate automated trading signals.

## Project Purpose

This system provides data-driven insights for stock trading decisions by:
- Automatically downloading and analyzing stock market data
- Optimizing trading parameters using historical backtesting
- Generating real-time buy/sell signals based on proven Turtle Trading methodology
- Providing comprehensive performance analysis and visualization

## Core Components & Functionality

### 1. **Data Collection (`get_data.py`)**
- Downloads daily stock data from Yahoo Finance using `yfinance`
- Monitors specific stocks: TSLA, ENR, RKLB, META, AMZN, NVDA, AAPL, GIV
- Stores data in CSV files in `~/Documents/Ki_Trading/data/stocks/`
- Runs scheduled daily updates at midnight
- **Key function**: `fetch_stock_data()` at line 32

### 2. **Parameter Optimization (`optimize_atr_parameters.py`)**
- Optimizes Turtle Trading parameters using historical data (2005-2021)
- Tests different breakout periods (20, 55 days) and ATR multipliers (2, 3)
- Uses backtesting to find optimal parameters for each stock
- Generates `optimized_params_2005_2021.csv` with best parameters
- **Core optimization logic**: `optimize_params_2005_2021()` at line 73

### 3. **Backtesting (`backtesting.py`)**
- Tests optimized parameters on historical data (2022-2024)
- Implements Turtle Trading logic with position sizing based on ATR
- Generates trading signals, calculates profits, and creates visualizations
- Creates trade charts and saves results to CSV files
- **Main backtesting function**: `backtest_turtle_strategy()` at line 28

### 4. **Forward Testing (`forward_testing.py`)**
- Applies optimized parameters to current market data
- Generates real-time trading signals (Buy/Sell/Hold)
- Calculates entry prices, stop losses, and take profits
- **Signal calculation**: `calculate_turtle_signals()` at line 38

## How It Functions

1. **Data Pipeline**: Downloads and maintains current stock data
2. **Optimization Phase**: Finds best parameters using historical training data (2005-2021)
3. **Validation Phase**: Tests parameters on out-of-sample data (2022-2024 backtesting)
4. **Live Trading Phase**: Generates current trading recommendations

## Dependencies

```python
pandas          # Data manipulation and analysis
numpy           # Numerical calculations
yfinance        # Stock data retrieval from Yahoo Finance
matplotlib      # Chart generation and visualization
schedule        # Task scheduling for automated updates
```

Standard library modules: `os`, `datetime`, `time`, `itertools`

## Installation & Usage

1. Install dependencies:
```bash
pip install pandas numpy yfinance matplotlib schedule
```

2. Run the components:
```bash
# Download latest stock data
python get_data.py

# Optimize parameters (run once or when reoptimizing)
python optimize_atr_parameters.py

# Run backtesting analysis
python backtesting.py

# Get current trading signals
python forward_testing.py
```

## Output Files

- `~/Documents/Ki_Trading/data/stocks/`: Historical stock data CSV files
- `~/Documents/Ki_Trading/results/`: Backtesting results and trade charts
- `~/Documents/Ki_Trading/forward_testing/`: Current trading signals
- `optimized_params_2005_2021.csv`: Optimized parameters for each stock

## React Frontend Integration

This project includes a complete React frontend with Flask API backend integration. The system is now ready for full-stack usage with a modern web interface.

### API Endpoints:
- `GET /api/health` - Health check
- `GET /api/stocks` - List all available stocks
- `GET /api/stocks/{ticker}/data` - Get historical stock data
- `GET /api/stocks/{ticker}/signals` - Get current trading signals
- `GET /api/stocks/{ticker}/chart` - Get stock price chart
- `GET /api/backtest/{ticker}` - Get backtesting results
- `GET /api/dashboard` - Get dashboard overview data
- `POST /api/stocks/{ticker}/update` - Update stock data

### Quick Start (Full Stack):

1. **Backend Setup:**
```bash
# Install Python dependencies
pip install -r api/requirements.txt

# Start the Flask API server
python start_backend.py
```

2. **Frontend Setup:**
```bash
# Install Node.js dependencies
cd frontend
npm install

# Start the React development server
npm run dev
```

3. **Access the Application:**
- Frontend: http://localhost:5174 (Vite dev server)
- API: http://localhost:8000

### Quick Start Commands:

**Terminal 1 - Backend:**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r api/requirements.txt

# Start Flask API server
cd api && python app.py
```

**Terminal 2 - Frontend:**
```bash
# Install Node.js dependencies and start
cd frontend
npm install
npm run dev
```
