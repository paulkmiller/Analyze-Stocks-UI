import pandas as pd
import numpy as np
import os
from itertools import product

# Speicherpfade
base_folder = os.path.expanduser("~/Documents/Ki_Trading")
data_folder = os.path.join(base_folder, "data", "stocks")
results_folder = os.path.join(base_folder, "results")
os.makedirs(results_folder, exist_ok=True)

# Märkte mit ihren Tickern
markets = {
    "Tesla": "TSLA",
    "Palantir": "PLTR",
    "Siemens Energy": "ENR",
    "Rocket Lab": "RKLB",
    "Cyberark": "CYB",
    "Symbotic": "SYM",
    "Rheinmetall": "RHM",
}

# Turtle-Parameter
breakout_high_periods = [20, 55]  # System 1 und System 2
breakout_low_periods = [10, 20]   # Exit-Strategien
atr_multiplier = [2, 3]          # Stop-Loss basierend auf ATR
risk_per_trade = 0.01            # 1% Risiko pro Trade

# Berechnung der Positionsgröße
def calculate_position_size(account_balance, atr, risk_per_trade):
    return risk_per_trade * account_balance / atr

# Backtest der Turtle-Strategie
def backtest_turtle_strategy(df, params, account_balance):
    df["TR"] = np.maximum(
        df["High"] - df["Low"],
        np.maximum(abs(df["High"] - df["Close"].shift(1)), abs(df["Low"] - df["Close"].shift(1)))
    )
    df["ATR"] = df["TR"].rolling(window=20).mean()  # 20-Tage-ATR als Basis
    df["High_Breakout"] = df["High"].rolling(window=params["breakout_high_period"]).max()
    df["Low_Breakout"] = df["Low"].rolling(window=params["breakout_low_period"]).min()

    df["Buy_Signal"] = df["Close"] > df["High_Breakout"].shift(1)
    df["Sell_Signal"] = df["Close"] < df["Low_Breakout"].shift(1)

    position_open = False
    buy_price = 0
    stop_loss = 0
    total_profit = 0
    position_size = 0

    for i in range(len(df)):
        row = df.iloc[i]

        if not position_open and row["Buy_Signal"]:
            atr = row["ATR"]
            if atr > 0:  # ATR darf nicht 0 sein
                position_size = calculate_position_size(account_balance, atr, risk_per_trade)
                position_open = True
                buy_price = row["Close"]
                stop_loss = buy_price - params["atr_multiplier"] * atr

        elif position_open:
            if row["Close"] <= stop_loss or row["Sell_Signal"]:
                position_open = False
                sell_price = row["Close"]
                profit = (sell_price - buy_price) * position_size
                total_profit += profit

    return total_profit

# Optimierung der Parameter
def optimize_params_2005_2021(df, params_range, account_balance):
    best_profit = -float("inf")
    best_params = None

    for breakout_high, breakout_low, atr_mult in product(
        params_range["breakout_high_periods"], params_range["breakout_low_periods"], params_range["atr_multiplier"]
    ):
        params = {
            "breakout_high_period": breakout_high,
            "breakout_low_period": breakout_low,
            "atr_multiplier": atr_mult,
        }
        profit = backtest_turtle_strategy(df, params, account_balance)

        if profit > best_profit:
            best_profit = profit
            best_params = params

    return best_params, best_profit

# Hauptprogramm
optimized_results = []
initial_account_balance = 100000  # Startkapital

for market_name, ticker in markets.items():
    file_path = os.path.join(data_folder, f"{ticker}_data.csv")
    if os.path.exists(file_path):
        print(f"Starte Turtle-Optimierung für {market_name} ({ticker})...")
        df = pd.read_csv(file_path)

        # Datenvorbereitung
        df.rename(columns={"Date": "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        numeric_columns = ["High", "Low", "Close", "Open", "Volume"]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
        df.dropna(subset=numeric_columns, inplace=True)

        # Zeitraum für Optimierung (2005–2021)
        train_df = df.loc["2005-01-01":"2021-12-31"]

        # Parameter optimieren
        best_params, best_profit = optimize_params_2005_2021(
            train_df,
            {
                "breakout_high_periods": breakout_high_periods,
                "breakout_low_periods": breakout_low_periods,
                "atr_multiplier": atr_multiplier,
            },
            initial_account_balance
        )
        print(f"Beste Parameter für {market_name}: {best_params} mit Gewinn: {best_profit:.2f}")

        optimized_results.append({
            "asset": market_name,
            "breakout_high_period": best_params["breakout_high_period"],
            "breakout_low_period": best_params["breakout_low_period"],
            "atr_multiplier": best_params["atr_multiplier"],
            "profit": best_profit,
        })
    else:
        print(f"Datei für {market_name} ({ticker}) nicht gefunden: {file_path}")

# Ergebnisse speichern
optimized_params_df = pd.DataFrame(optimized_results)
optimized_params_file = os.path.join(base_folder, "optimized_params_2005_2021.csv")
optimized_params_df.to_csv(optimized_params_file, index=False)
print(f"Optimierte Turtle-Parameter gespeichert unter: {optimized_params_file}")






