import pandas as pd
import numpy as np
import os

# Speicherpfade
base_folder = os.path.expanduser("~/Documents/Ki_Trading")
data_folder = os.path.join(base_folder, "data", "stocks")
results_folder = os.path.join(base_folder, "forward_testing")
os.makedirs(results_folder, exist_ok=True)

# Optimierte Parameter laden
optimized_params_2005_2021 = os.path.join(base_folder, "optimized_params_2005_2021.csv")
if not os.path.exists(optimized_params_2005_2021):
    raise FileNotFoundError(f"Die Datei mit optimierten Parametern wurde nicht gefunden: {optimized_params_2005_2021}")

optimized_params_df = pd.read_csv(optimized_params_2005_2021)

# Ticker-Abkürzungen
ticker_map = {
    "Tesla": "TSLA",
    "Palantir": "PLTR",
    "Siemens Energy": "ENR",
    "Rocket Lab": "RKLB",
    "Cyberark": "CYB",
    "Symbotic": "SYM",
    "Rheinmetall": "RHM",
}

optimized_params = {
    ticker_map[row["asset"]]: {
        "atr_period": 20,  # Fixed ATR period for consistency
        "breakout_high_period": int(row["breakout_high_period"]),
        "breakout_low_period": int(row["breakout_low_period"]),
        "atr_multiplier": int(row["atr_multiplier"]) if "atr_multiplier" in row else 2,
    }
    for _, row in optimized_params_df.iterrows()
}

# Funktion: Berechne Turtle-Trading-Indikatoren
def calculate_turtle_signals(data, params):
    """
    Berechnet Einstieg, Stop-Loss und Take-Profit gemäß Turtle-Trading-Regeln.
    """
    data["TR"] = np.maximum(
        data["High"] - data["Low"],
        np.maximum(abs(data["High"] - data["Close"].shift(1)), abs(data["Low"] - data["Close"].shift(1))),
    )
    data["ATR"] = data["TR"].rolling(window=params["atr_period"], min_periods=params["atr_period"]).mean()

    # Entry- und Exit-Level
    data["Entry_High"] = data["High"].rolling(window=params["breakout_high_period"]).max()
    data["Exit_Low"] = data["Low"].rolling(window=params["breakout_low_period"]).min()

    # Signal generieren
    data["Signal"] = np.where(data["Close"] > data["Entry_High"].shift(1), "Buy",
                              np.where(data["Close"] < data["Exit_Low"].shift(1), "Sell", "Hold"))

    # Stop-Loss und Take-Profit
    data["Stop_Loss"] = np.where(data["Signal"] == "Buy", data["Entry_High"] - 2 * data["ATR"], np.nan)
    data["Take_Profit"] = np.where(data["Signal"] == "Buy", data["Entry_High"] + 2 * data["ATR"], np.nan)

    return data

# Hauptprogramm
if __name__ == "__main__":
    import sys

    # Check for language preference
    english = "--english" in sys.argv

    # Ergebnisse vorbereiten
    results = []

    # Forward Testing
    for ticker, params in optimized_params.items():
        file_path = os.path.join(data_folder, f"{ticker}_data.csv")

        if os.path.exists(file_path):
            if english:
                print(f"Analyzing {ticker}...")
            else:
                print(f"Analysiere {ticker}...")
            df = pd.read_csv(file_path)

            # Datenvorbereitung
            df.rename(columns={"Date": "timestamp"}, inplace=True)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            numeric_columns = ["High", "Low", "Close", "Open", "Volume"]
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
            df.dropna(subset=numeric_columns, inplace=True)

            # Turtle-Trading-Berechnungen
            df = calculate_turtle_signals(df, params)

            # Letztes Signal erfassen
            latest_row = df.iloc[-1]
            entry_price = latest_row["Entry_High"] if latest_row["Signal"] == "Buy" else np.nan
            stop_loss = latest_row["Stop_Loss"] if latest_row["Signal"] == "Buy" else np.nan
            take_profit = latest_row["Take_Profit"] if latest_row["Signal"] == "Buy" else np.nan

            results.append({
                "asset": ticker,
                "signal": latest_row["Signal"],
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
            })
        else:
            if english:
                print(f"File for {ticker} not found: {file_path}")
            else:
                print(f"Datei für {ticker} nicht gefunden: {file_path}")

    # Ergebnisse speichern
    results_df = pd.DataFrame(results)
    results_file = os.path.join(results_folder, "forward_testing_results.csv")
    results_df.to_csv(results_file, index=False)
    if english:
        print(f"\nForward testing completed. Results saved to {results_file}")
    else:
        print(f"\nForward Testing abgeschlossen. Ergebnisse gespeichert in {results_file}")















