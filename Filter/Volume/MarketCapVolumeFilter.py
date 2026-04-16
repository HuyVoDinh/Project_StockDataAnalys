import os

import pandas as pd
from Filter.Volume.VolumeFilter import VolumeFilter

from Model import Company
from StockData.stock_analyzer import StockAnalyzer
from StockData.stock_data import StockData


def filter_stocks_by_market_cap_and_volume(symbol_list, output_file="filtered_stocks.csv"):
    filtered_stocks_df = []
    for symbol in symbol_list['symbol']:
        stock_analyzer = StockAnalyzer(symbol)
        stock_analyzer.init_Stock()
        stock_analyzer.update_data_frame("2026-03-01", "2026-04-14")
        if stock_analyzer.data_frame is None:
            continue
        stock_analyzer.Calculate_Trading_Value()
        print(symbol)
        trading_value = stock_analyzer.data_frame['trading_value']
        if trading_value.iloc[-1] > 50:
            print("[MarketCapVolumeFilter][filter_stocks_by_market_cap_and_volume] Filtered stocks data - add: " + symbol)
            filtered_stocks_df.append(symbol)
        else:
            print(f"[MarketCapVolumeFilter][filter_stocks_by_market_cap_and_volume] {symbol} - {trading_value.iloc[-1] if not trading_value.empty else 'No data'} < 50")

    result_data = pd.DataFrame(filtered_stocks_df, columns=['fundamental_technical_setup'])
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