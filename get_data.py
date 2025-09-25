import os
import pandas as pd
import yfinance as yf
import schedule
from datetime import datetime
import time


# Liste der Aktien
ASSETS = {
    "stocks": [
        # Aktien
        {"ticker": "TSLA", "start_date": "2020-01-01"},      # Tesla
       # {"ticker": "PLTR", "start_date": "2020-01-01"},      # Palantir
        {"ticker": "ENR", "start_date": "2020-01-01"},       # Siemens Energy
        {"ticker": "RKLB", "start_date": "2020-01-01"},      # Rocket Lab
       # {"ticker": "CYB", "start_date": "2020-01-01"},       # Cyberark
       # {"ticker": "SYM", "start_date": "2020-01-01"},       # Symbotic
       # {"ticker": "RHM", "start_date": "2020-01-01"},       # Rheinmetal
        {"ticker": "META", "start_date": "2020-01-01"},      # Meta
        {"ticker": "AMZN", "start_date": "2020-01-01"},      # Amazon
        {"ticker": "NVDA", "start_date": "2020-01-01"},      # Nvidia
        {"ticker": "AAPL", "start_date": "2020-01-01"},      # Apple
        {"ticker": "GIV", "start_date": "2020-01-01"},       # GeVernova
    ]
}

# Speicherpfade
base_folder = os.path.expanduser("~/Documents/Ki_Trading")
data_folder = os.path.join(base_folder, "data", "stocks")

def fetch_stock_data(ticker, start_date):
    """
    Holt tägliche Daten von Yahoo Finance.
    """
    print(f"Starte Download für: {ticker}")
    try:
        data = yf.download(ticker, start=start_date, interval="1d")  # Tägliche Daten
        if data.empty:
            print(f"Keine Daten für {ticker} verfügbar.")
            return pd.DataFrame()

        data.reset_index(inplace=True)  # Setzt den Index zurück
        data.rename(columns={"Date": "timestamp"}, inplace=True)  # "Date" in "timestamp" umbenennen
        return data[["timestamp", "High", "Low", "Open", "Close", "Volume"]]
    except Exception as e:
        print(f"Fehler beim Abrufen von {ticker}: {e}")
        return pd.DataFrame()

def save_stock_data(data, ticker):
    """
    Speichert Daten in einer einzigen Datei und aktualisiert sie.
    """
    if data.empty:
        print(f"Keine neuen Daten für {ticker}.")
        return

    folder = data_folder  # Ordner für Daten
    file_name = f"{ticker}_data.csv"
    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, file_name)

    # Alte Daten laden und aktualisieren
    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path, parse_dates=["timestamp"])
        data = pd.concat([existing_data, data]).drop_duplicates(subset=["timestamp"]).sort_values(by="timestamp")

    # Runde alle numerischen Werte auf 2 Nachkommastellen
    numeric_columns = ["High", "Low", "Open", "Close", "Volume"]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce").round(2)

    data.to_csv(file_path, index=False)
    print(f"Daten für {ticker} gespeichert unter {file_path}")

def update_stock_data():
    """
    Aktualisiert Daten täglich.
    """
    print("Aktualisiere Assets...")
    for asset in ASSETS["stocks"]:
        ticker = asset["ticker"]
        start_date = asset["start_date"]
        data = fetch_stock_data(ticker, start_date)
        save_stock_data(data, ticker)

# Scheduler für tägliche Updates
schedule.every().day.at("00:00").do(update_stock_data)  # Daten täglich um Mitternacht aktualisieren

# Hauptprogramm
if __name__ == "__main__":
    print("Automatisierte Datenaktualisierung läuft...")
    update_stock_data()  # Erste Ausführung für aktuelle Daten
    while True:
        schedule.run_pending()
        time.sleep(1)

