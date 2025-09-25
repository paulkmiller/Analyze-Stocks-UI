import pandas as pd
import os
import matplotlib.pyplot as plt

# Speicherpfade
base_folder = os.path.expanduser("~/Documents/Ki_Trading")
data_folder = os.path.join(base_folder, "data", "stocks")
results_folder = os.path.join(base_folder, "results")
os.makedirs(results_folder, exist_ok=True)

# Parameter-Datei
params_file = os.path.join(base_folder, "optimized_params_2005_2021.csv")
if not os.path.exists(params_file):
    raise FileNotFoundError(f"Die Datei mit optimierten Parametern wurde nicht gefunden: {params_file}")

# Optimierte Parameter laden
optimized_params_df = pd.read_csv(params_file)
optimized_params = {
    row["asset"]: {
        "breakout_high_period": int(row["breakout_high_period"]),
        "breakout_low_period": int(row["breakout_low_period"]),
        "atr_multiplier": int(row["atr_multiplier"]),
    }
    for _, row in optimized_params_df.iterrows()
}

# Backtest der Turtle-Strategie
def backtest_turtle_strategy(df, params, account_balance):
    position_open = False
    buy_price = 0
    stop_loss = 0
    total_profit = 0
    trades = []

    for i in range(len(df)):
        row = df.iloc[i]

        if not position_open and row["Buy_Signal"]:
            position_size = account_balance * 0.01 / row["ATR"]  # Positionsgröße basierend auf ATR
            position_open = True
            buy_price = row["Close"]
            stop_loss = buy_price - params["atr_multiplier"] * row["ATR"]
            trades.append({"date": row.name, "action": "Buy", "price": buy_price, "stop_loss": stop_loss})

        elif position_open:
            if row["Close"] <= stop_loss or row["Sell_Signal"]:
                position_open = False
                sell_price = row["Close"]
                profit = (sell_price - buy_price) * position_size
                total_profit += profit
                trades.append({"date": row.name, "action": "Sell", "price": sell_price, "profit": profit})

    return total_profit, trades

def plot_trades(df, trades, asset):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df["Close"], label="Kurs", linewidth=0.7)

    for trade in trades:
        if trade["action"] == "Buy":
            plt.scatter(trade["date"], trade["price"], color="green", label="Kauf", zorder=5)
        elif trade["action"] == "Sell":
            plt.scatter(trade["date"], trade["price"], color="red", label="Verkauf", zorder=5)

    plt.title(f"Trades für {asset}")
    plt.xlabel("Datum")
    plt.ylabel("Kurs")
    plt.legend()
    plt.grid(alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, f"{asset}_trades_chart.png"))
    plt.show()

# Hauptprogramm
results = []
initial_account_balance = 1000

ticker_map = {
    "Tesla": "TSLA",
    "Palantir": "PLTR",
    "Siemens Energy": "ENR",
    "Rocket Lab": "RKLB",
    "Cyberark": "CYB",
    "Symbotic": "SYM",
    "Rheinmetall": "RHM",
}

for asset, params in optimized_params.items():
    ticker = ticker_map.get(asset)  # Map asset to ticker abbreviation
    if not ticker:
        print(f"Kein Ticker für {asset} gefunden. Überspringe.")
        continue

    file_path = os.path.join(data_folder, f"{ticker}_data.csv")
    if os.path.exists(file_path):
        print(f"Starte Backtesting für {asset}...")
        df = pd.read_csv(file_path)

        # Datenvorbereitung
        df.rename(columns={"Date": "timestamp"}, inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        numeric_columns = ["High", "Low", "Close", "Open", "Volume"]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
        df.dropna(subset=numeric_columns, inplace=True)

        # Zeitraum für Backtesting (2022–2024)
        test_df = df.loc["2022-01-01":"2024-12-31"]

        # Signale basierend auf den Parametern generieren
        test_df["Buy_Signal"] = test_df["Close"] > test_df["High"].rolling(window=params["breakout_high_period"]).max().shift(1)
        test_df["Sell_Signal"] = test_df["Close"] < test_df["Low"].rolling(window=params["breakout_low_period"]).min().shift(1)
        test_df["ATR"] = test_df["High"] - test_df["Low"]  # ATR-Äquivalent basierend auf Preisspanne

        # Backtesting
        total_profit, trades = backtest_turtle_strategy(test_df, params, initial_account_balance)

        # Speichern der Trades
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(os.path.join(results_folder, f"{asset}_trades.csv"), index=False)

        # Ergebnisse speichern
        results.append({"asset": asset, "total_profit": total_profit, "number_of_trades": len(trades)})

        # Visualisierung
        plot_trades(test_df, trades, asset)
    else:
        print(f"Daten für {asset} nicht gefunden: {file_path}")

# Gesamtergebnisse speichern
results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(results_folder, "backtesting_results_2022_2024.csv"), index=False)
print("Backtesting abgeschlossen. Ergebnisse gespeichert unter backtesting_results_2022_2024.csv.")

