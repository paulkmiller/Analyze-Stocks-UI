from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import sys
import json
import math
from datetime import datetime
import base64
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Add parent directory to path to import our modules
sys.path.append('..')

# Import basic modules
from get_data import fetch_stock_data, save_stock_data, ASSETS

# Try to import optional modules (these require data to be present)
try:
    from forward_testing import calculate_turtle_signals
    forward_testing_available = True
except (ImportError, FileNotFoundError) as e:
    print(f"Warning: Forward testing not available - {e}")
    forward_testing_available = False

try:
    from backtesting import backtest_turtle_strategy
    backtesting_available = True
except (ImportError, FileNotFoundError) as e:
    print(f"Warning: Backtesting not available - {e}")
    backtesting_available = False

def clean_nan_values(obj):
    """Recursively replace NaN and inf values with None for JSON serialization"""
    if isinstance(obj, dict):
        return {key: clean_nan_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj

app = Flask(__name__)
CORS(app)

# Configuration
base_folder = os.path.expanduser("~/Documents/Ki_Trading")
data_folder = os.path.join(base_folder, "data", "stocks")
results_folder = os.path.join(base_folder, "results")

# Ensure directories exist
os.makedirs(data_folder, exist_ok=True)
os.makedirs(results_folder, exist_ok=True)

# Stock mapping
STOCK_MAP = {
    "TSLA": "Tesla",
    "ENR": "Siemens Energy",
    "RKLB": "Rocket Lab",
    "META": "Meta",
    "AMZN": "Amazon",
    "NVDA": "Nvidia",
    "AAPL": "Apple",
    "GEV": "GeVernova"
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get list of available stocks"""
    stocks = []
    for asset in ASSETS["stocks"]:
        ticker = asset["ticker"]
        file_path = os.path.join(data_folder, f"{ticker}_data.csv")
        has_data = os.path.exists(file_path)

        stocks.append({
            "ticker": ticker,
            "name": STOCK_MAP.get(ticker, ticker),
            "start_date": asset["start_date"],
            "has_data": has_data,
            "last_updated": None if not has_data else datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        })

    return jsonify(stocks)

@app.route('/api/stocks/<ticker>/data', methods=['GET'])
def get_stock_data(ticker):
    """Get historical stock data for a specific ticker"""
    file_path = os.path.join(data_folder, f"{ticker}_data.csv")

    if not os.path.exists(file_path):
        return jsonify({"error": f"No data found for {ticker}"}), 404

    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Get query parameters
        limit = request.args.get('limit', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Filter by date range if provided
        if start_date:
            df = df[df['timestamp'] >= start_date]
        if end_date:
            df = df[df['timestamp'] <= end_date]

        # Limit results if requested
        if limit:
            df = df.tail(limit)

        # Convert to JSON-friendly format
        data = df.to_dict('records')
        for record in data:
            record['timestamp'] = record['timestamp'].isoformat() if pd.notna(record['timestamp']) else None

        return jsonify({
            "ticker": ticker,
            "name": STOCK_MAP.get(ticker, ticker),
            "data": data,
            "total_records": len(data)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stocks/<ticker>/signals', methods=['GET'])
def get_trading_signals(ticker):
    """Get current trading signals for a specific ticker"""
    if not forward_testing_available:
        return jsonify({"error": "Trading signals not available. Please run optimization first."}), 503

    file_path = os.path.join(data_folder, f"{ticker}_data.csv")

    if not os.path.exists(file_path):
        return jsonify({"error": f"No data found for {ticker}"}), 404

    try:
        # Load optimized parameters
        params_file = os.path.join(base_folder, "optimized_params_2005_2021.csv")
        if not os.path.exists(params_file):
            return jsonify({"error": "Optimized parameters not found. Run optimization first."}), 404

        params_df = pd.read_csv(params_file)

        # Find parameters for this ticker
        ticker_params = None
        for _, row in params_df.iterrows():
            if row["asset"] in STOCK_MAP and STOCK_MAP[ticker] == row["asset"]:
                ticker_params = {
                    "atr_period": 20,  # Default ATR period
                    "breakout_high_period": int(row["breakout_high_period"]),
                    "breakout_low_period": int(row["breakout_low_period"]),
                    "atr_multiplier": int(row["atr_multiplier"])
                }
                break

        if not ticker_params:
            return jsonify({"error": f"No optimized parameters found for {ticker}"}), 404

        # Load and prepare data
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Calculate signals
        df = calculate_turtle_signals(df, ticker_params)

        # Get latest signal
        latest = df.iloc[-1]

        return jsonify({
            "ticker": ticker,
            "name": STOCK_MAP.get(ticker, ticker),
            "signal": latest["Signal"],
            "current_price": float(latest["Close"]),
            "entry_price": float(latest["Entry_High"]) if pd.notna(latest["Entry_High"]) else None,
            "stop_loss": float(latest["Stop_Loss"]) if pd.notna(latest["Stop_Loss"]) else None,
            "take_profit": float(latest["Take_Profit"]) if pd.notna(latest["Take_Profit"]) else None,
            "atr": float(latest["ATR"]) if pd.notna(latest["ATR"]) else None,
            "timestamp": latest.name.isoformat(),
            "parameters": ticker_params
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stocks/<ticker>/chart', methods=['GET'])
def get_stock_chart(ticker):
    """Generate and return stock chart as base64 image"""
    file_path = os.path.join(data_folder, f"{ticker}_data.csv")

    if not os.path.exists(file_path):
        return jsonify({"error": f"No data found for {ticker}"}), 404

    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Get last 200 days for chart
        df_chart = df.tail(200)

        plt.figure(figsize=(12, 6))
        plt.plot(df_chart.index, df_chart['Close'], linewidth=1.5, label='Close Price')
        plt.title(f"{STOCK_MAP.get(ticker, ticker)} ({ticker}) - Stock Price")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()

        # Convert plot to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return jsonify({
            "ticker": ticker,
            "chart": f"data:image/png;base64,{chart_data}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stocks/<ticker>/update', methods=['POST'])
def update_stock_data(ticker):
    """Update stock data for a specific ticker"""
    try:
        # Find the asset configuration
        asset_config = None
        for asset in ASSETS["stocks"]:
            if asset["ticker"] == ticker:
                asset_config = asset
                break

        if not asset_config:
            return jsonify({"error": f"Ticker {ticker} not found in configuration"}), 404

        # Fetch and save new data
        data = fetch_stock_data(ticker, asset_config["start_date"])
        save_stock_data(data, ticker)

        return jsonify({
            "ticker": ticker,
            "message": "Data updated successfully",
            "records_fetched": len(data)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/backtest/<ticker>', methods=['GET'])
def get_backtest_results(ticker):
    """Get backtesting results for a specific ticker"""
    if not backtesting_available:
        return jsonify({"error": "Backtesting not available. Please run optimization and backtesting first."}), 503

    results_file = os.path.join(results_folder, "backtesting_results_2022_2024.csv")

    if not os.path.exists(results_file):
        return jsonify({"error": "Backtesting results not found. Run backtesting first."}), 404

    try:
        results_df = pd.read_csv(results_file)

        # Find results for this ticker
        ticker_name = STOCK_MAP.get(ticker, ticker)
        ticker_results = results_df[results_df['asset'] == ticker_name]

        if ticker_results.empty:
            return jsonify({"error": f"No backtesting results found for {ticker}"}), 404

        result = ticker_results.iloc[0]

        return jsonify({
            "ticker": ticker,
            "name": ticker_name,
            "total_profit": float(result["total_profit"]),
            "number_of_trades": int(result["number_of_trades"]),
            "profit_per_trade": float(result["total_profit"]) / int(result["number_of_trades"]) if int(result["number_of_trades"]) > 0 else 0
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard overview data for all stocks"""
    try:
        dashboard_data = []

        for asset in ASSETS["stocks"]:
            ticker = asset["ticker"]
            file_path = os.path.join(data_folder, f"{ticker}_data.csv")

            stock_info = {
                "ticker": ticker,
                "name": STOCK_MAP.get(ticker, ticker),
                "has_data": os.path.exists(file_path),
                "signal": None,
                "current_price": None,
                "change_percent": None,
                "last_updated": None
            }

            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    if not df.empty:
                        latest = df.iloc[-1]
                        previous = df.iloc[-2] if len(df) > 1 else latest

                        stock_info.update({
                            "current_price": float(latest["Close"]),
                            "change_percent": ((float(latest["Close"]) - float(previous["Close"])) / float(previous["Close"])) * 100,
                            "last_updated": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })

                        # Try to get signal (this might fail if parameters aren't available)
                        if forward_testing_available:
                            try:
                                # Create a temporary request context for the signals endpoint
                                with app.test_client() as client:
                                    response = client.get(f'/api/stocks/{ticker}/signals')
                                    if response.status_code == 200:
                                        signal_data = response.get_json()
                                        stock_info["signal"] = signal_data.get("signal")
                            except:
                                pass

                except Exception as e:
                    print(f"Error processing {ticker}: {e}")

            dashboard_data.append(stock_info)

        response_data = {
            "stocks": dashboard_data,
            "total_stocks": len(dashboard_data),
            "active_stocks": sum(1 for stock in dashboard_data if stock["has_data"]),
            "timestamp": datetime.now().isoformat()
        }

        # Clean NaN values before sending JSON response
        clean_response = clean_nan_values(response_data)
        return jsonify(clean_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Stock Analysis API...")
    print(f"Data folder: {data_folder}")
    print(f"Results folder: {results_folder}")
    app.run(debug=True, host='0.0.0.0', port=8000)