import os
from datetime import datetime

import pandas as pd

from src.analysis.stock_analyzer import StockAnalyzer


def filter_stocks_by_market_cap_and_volume(symbol_list, output_file="filtered_stocks.csv"):
    filtered_stocks_df = []
    now = datetime.now()
    for symbol in symbol_list['symbol']:
        stock_analyzer = StockAnalyzer(symbol)
        stock_analyzer.init_Stock()
        stock_analyzer.update_data_frame("2026-03-01", now.strftime("%Y-%m-%d"))
        if stock_analyzer.data_frame is None:
            print(f"[Main][filter_stocks_by_market_cap_and_volume] No stock data: {symbol}")
            continue
        stock_analyzer.Calculate_Trading_Value()
        print(symbol)
        trading_value = stock_analyzer.data_frame['trading_value']
        if trading_value.iloc[-1] > 30:
            print("[MarketCapVolumeFilter][filter_stocks_by_market_cap_and_volume] Filtered stocks data - add: " + symbol)
            filtered_stocks_df.append(symbol)
        else:
            print(f"[MarketCapVolumeFilter][filter_stocks_by_market_cap_and_volume] {symbol} - {trading_value.iloc[-1] if not trading_value.empty else 'No data'} < 50")

    result_data = pd.DataFrame(filtered_stocks_df, columns=['symbol'])
    result_data.to_csv(output_file, index=False)
    return filtered_stocks_df

def get_filtered_symbols(filtered_file="filtered_stocks.csv"):
    try:
        if not os.path.exists(filtered_file):
            print("[MarketCapVolumeFilter][filter_stocks_by_market_cap_and_volume] File not found")
            return []

        df = pd.read_csv(filtered_file)

        if 'symbol' in df.columns:
            symbols = df['symbol'].tolist()
            return symbols
        else:
            print("[MarketCapVolumeFilter][filter_stocks_by_market_cap_and_volume] No symbols found")
            return []
    except Exception as e:
        print(f"[MarketCapVolumeFilter][filter_stocks_by_market_cap_and_volume] {e}")
        return []