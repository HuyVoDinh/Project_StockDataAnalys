import pandas as pd
import os
import sys
import pickle

from Trading.Demo import Demo
from Trading.Strategy1 import Strategy1
from Trading.Strategy2 import Strategy2
from Trading.Strategy3 import Strategy3
from Trading.Strategy4 import Strategy4
from Trading.Strategy5 import Strategy5

def load_current_data():
    """Load current data from the main processing"""
    try:
        # Load the current data CSV
        data_file = "data_current.csv"
        if not os.path.exists(data_file):
            data_file = "data.csv"

        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            return df
        else:
            print("[Trading][load_current_data] No data file found. Please run main.py firest to generate data.")
            return  None
    except Exception as e:
        print(f"[Trading][load_current_data] Error loading data: {e}")
        return None

def load_company_data():
    """Load company data from the main processing"""
    try:
        # Load the company data
        if os.path.exists("company_data.pkl"):
            with open("company_data.pkl", "rb") as f:
                return pickle.load(f)
        else:
            print("[Trading][load_company_data] No company data file found")
            return {}
    except Exception as e:
        print(f"[Trading][load_company_data] Error loading company data: {e}")

def get_filtered_symbol():
    """Load symbols from filtered_stocks.csv"""
    try:
        # load the filtered sotcks CSV
        filtered_file = "filtered_stocks.csv"

        if os.path.exists(filtered_file):
            df = pd.read_csv(filtered_file)
            if 'symbol' in df.columns:
                symbols = df['symbol'].tolist()
                return symbols
            else:
                print(f"[Trading][get_filtered_symbol] 'symbol' column not found. Please run main.py firest to generate data.")
        else:
            print("[Trading][get_filtered_symbol] No filtered_stocks.csv found")
            return []
    except Exception as e:
        print(f"[Trading][get_filtered_symbol] Error loading filtered_stocks.csv: {e}")
        return []

def get_all_symbols(data_df):
    """Extract all symbols from the data frame"""
    symbols = set()
    for column in data_df.columns:
        symbols.update(data_df[column].dropna().unique())
    return list(symbols)

def get_current_prices(symbols):
    """Get current prices for symbols from company data"""
    prices = {}
    company_data = load_company_data()
    for symbol in symbols:
       if symbol in company_data and company_data[symbol].company_data:
            # Get the lastest price from company data
            lastest_data = company_data[symbol].company_data[-1]
            if lastest_data and lastest_data.price and lastest_data.price.close_price:
                prices[symbol] = lastest_data.price.close_price
            else:
                # Fallback to average of open and close if close price not available
                if lastest_data.price and lastest_data.price.open_price:
                    prices[symbol] = (lastest_data.price.open_price + lastest_data.price.open_price) / 2 if lastest_data.price.close_price else lastest_data.price.open_price
                else:
                    # Last fallback to a default value
                    prices[symbol] = 100000
    return prices

def main():
    print("[Trading][main] Loading current data...")
    data_df = load_current_data()

    if data_df is None:
        return

    print("[Trading][main] Data loaded successfully")

    # Load company data
    print("[Trading][main] Loading company data...")
    company_data = load_company_data()
    print(f"[Trading][main] Loaded company data for {len(company_data)} symbols")

    # Get all symbols
    symbols = get_filtered_symbol()
    if not symbols:
        print("[Trading][main] No symbols found, using all symbols from data")
        symbols = get_all_symbols(data_df)
    print(f"[Trading][main] Found {len(symbols)} symbols to process")

    # Get current prices (simplified)
    current_prices = get_current_prices(symbols)

    # Create strategies
    strategies = [
        Strategy1(),
        Strategy2(),
        Strategy3(),
        Strategy4(),
        Strategy5(),
        Demo(),
    ]

    # Prepare data for strategies
    data = {
        'symbols': symbols,
        'company_data': company_data
    }

    # Execute each strategies
    for i, strategy in enumerate(strategies, 1):
        print(f"\n[Trading][main] Executing {strategy.name}...")
        strategy.execute_trades(data, current_prices)

        # Generate report
        report = strategy.get_report(current_prices)
        print(report)

        # Save report to file
        report_file = f"Trading/{strategy.name}_report.csv"
        with open(report_file, "w", encoding='utf-8') as f:
            f.write(report)

        print(f"[Trading][main] Report save to {report_file}")

    print("\n [Trading][main] All strategies executed successfully")

if __name__ == "__main__":
    main()
