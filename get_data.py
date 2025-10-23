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
        {"ticker": "GEV", "start_date": "2020-01-01"},       # GeVernova
        {"ticker": "GOOGL", "start_date": "2020-01-01"},     # Google
    ]
}

# Speicherpfade
base_folder = os.path.expanduser("~/Documents/Ki_Trading")
data_folder = os.path.join(base_folder, "data", "stocks")

def fetch_stock_data(ticker, start_date, english=False):
    """
    Holt tägliche Daten von Yahoo Finance.
    """
    if english:
        print(f"Starting download for: {ticker}")
    else:
        print(f"Starte Download für: {ticker}")

    try:
        # Updated parameters for yfinance 0.2.66 compatibility
        stock = yf.Ticker(ticker)
        data = stock.history(
            start=start_date,
            interval="1d",
            timeout=10,
            auto_adjust=True,
            prepost=False,
            actions=False
        )

        if data.empty:
            if english:
                print(f"No data available for {ticker}.")
            else:
                print(f"Keine Daten für {ticker} verfügbar.")
            return pd.DataFrame()

        data.reset_index(inplace=True)
        data.rename(columns={"Date": "timestamp"}, inplace=True)

        if english:
            print(f"Successfully downloaded {len(data)} records for {ticker}")
        else:
            print(f"Erfolgreich {len(data)} Datensätze für {ticker} heruntergeladen")

        return data[["timestamp", "High", "Low", "Open", "Close", "Volume"]]
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Too Many Requests" in error_msg:
            if english:
                print(f"Rate limit exceeded for {ticker}. Please try again later.")
            else:
                print(f"Rate-Limit für {ticker} überschritten. Bitte später erneut versuchen.")
        elif "No data found" in error_msg or "No timezone found" in error_msg:
            if english:
                print(f"No market data available for {ticker}. Check ticker symbol.")
            else:
                print(f"Keine Marktdaten für {ticker} verfügbar. Ticker-Symbol prüfen.")
        else:
            if english:
                print(f"Error downloading {ticker}: {e}")
            else:
                print(f"Fehler beim Abrufen von {ticker}: {e}")
        return pd.DataFrame()

def save_stock_data(data, ticker, english=False):
    """
    Speichert Daten in einer einzigen Datei und aktualisiert sie.
    """
    if data.empty:
        if english:
            print(f"No new data for {ticker}.")
        else:
            print(f"Keine neuen Daten für {ticker}.")
        return

    folder = data_folder  # Ordner für Daten
    file_name = f"{ticker}_data.csv"
    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, file_name)

    # Ensure data has the right columns in the right order
    expected_columns = ["timestamp", "High", "Low", "Open", "Close", "Volume"]
    data = data[expected_columns].copy()

    # Alte Daten laden und aktualisieren
    if os.path.exists(file_path):
        try:
            # Read with explicit column names to prevent corruption
            existing_data = pd.read_csv(file_path, parse_dates=["timestamp"])

            # Validate existing data structure
            if list(existing_data.columns) == expected_columns:
                # Clean merge - remove duplicates and sort
                combined = pd.concat([existing_data, data], ignore_index=True)
                data = combined.drop_duplicates(subset=["timestamp"]).sort_values(by="timestamp").reset_index(drop=True)
            else:
                if english:
                    print(f"Warning: Corrupted data file for {ticker}. Recreating with fresh data.")
                else:
                    print(f"Warnung: Beschädigte Datendatei für {ticker}. Neu erstellen mit frischen Daten.")
                # Use only new data if existing file is corrupted
        except Exception as e:
            if english:
                print(f"Error reading existing {ticker} data: {e}. Creating fresh file.")
            else:
                print(f"Fehler beim Lesen der bestehenden {ticker} Daten: {e}. Erstelle neue Datei.")

    # Runde alle numerischen Werte auf 2 Nachkommastellen
    numeric_columns = ["High", "Low", "Open", "Close", "Volume"]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce").round(2)

    # Remove any rows with NaN values that could corrupt the data
    data = data.dropna()

    # Save with explicit columns to prevent corruption
    data.to_csv(file_path, index=False, columns=expected_columns)
    if english:
        print(f"Data for {ticker} saved to {file_path} ({len(data)} records)")
    else:
        print(f"Daten für {ticker} gespeichert unter {file_path} ({len(data)} Datensätze)")

def update_stock_data(english=False):
    """
    Aktualisiert Daten täglich.
    """
    if english:
        print("Updating assets...")
    else:
        print("Aktualisiere Assets...")

    for asset in ASSETS["stocks"]:
        ticker = asset["ticker"]
        start_date = asset["start_date"]
        data = fetch_stock_data(ticker, start_date, english)
        save_stock_data(data, ticker, english)

# Scheduler für tägliche Updates
schedule.every().day.at("00:00").do(update_stock_data)  # Daten täglich um Mitternacht aktualisieren

# Hauptprogramm
if __name__ == "__main__":
    import sys

    # Check for language preference
    english = "--english" in sys.argv
    daemon_mode = "--daemon" in sys.argv

    if daemon_mode:
        if english:
            print("Automated data update running as daemon...")
            update_stock_data(english=True)  # Initial execution for current data
            print("Waiting for scheduled updates (daily at midnight). Press Ctrl+C to exit.")
        else:
            print("Automatisierte Datenaktualisierung läuft als Daemon...")
            update_stock_data(english=False)  # Erste Ausführung für aktuelle Daten
            print("Warten auf geplante Updates (täglich um Mitternacht). Drücke Ctrl+C zum Beenden.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            if english:
                print("\nData update stopped.")
            else:
                print("\nDatenaktualisierung beendet.")
    else:
        if english:
            print("Loading stock data...")
            update_stock_data(english=True)  # Single execution
            print("Data download completed.")
        else:
            print("Lade Aktiendata herunter...")
            update_stock_data(english=False)  # Einmalige Ausführung
            print("Datendownload abgeschlossen.")

