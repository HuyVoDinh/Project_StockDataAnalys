import os

import pandas as pd
from Filter.Volume.VolumeFilter import VolumeFilter

from Model import Company
from StockData.stock_analyzer import StockAnalyzer
from StockData.stock_data import StockData


def filter_stocks_by_market_cap_and_volume(symbol_list, output_file="filtered_stocks.csv"):
    filtered_stocks_df = pd.DataFrame()
    # try:
    for symbol in symbol_list['symbol']:
        stock_analyzer = StockAnalyzer(symbol)
        stock_analyzer.init_Stock()
        stock_analyzer.update_data_frame("2026-03-01", "2026-04-14")
        if stock_analyzer.data_frame is None:
            continue
        stock_analyzer.Calculate_Trading_Value()
        print(symbol)
        if stock_analyzer['trading_value'] > 50:
            filtered_stocks_df.append(symbol)

        pd.DataFrame(filtered_stocks_df, columns=['fundamental_technical_setup'])
        result_data = pd.concat([filtered_stocks_df], axis=1)
        result_data.to_csv(output_file, index=False)
    return filtered_stocks_df
    # except Exception as e:
    #     print(e)
    #     return None


def get_filtered_symbols(filtered_file="filtered_stocks.csv"):
    try:
        if not os.path.exists(filtered_file):
            print("File not found")
            return []

        df = pd.read_csv(filtered_file)

        if 'symbol' in df.columns:
            symbols = df['symbol'].tolist()
            return symbols
        else:
            print("No symbols found")
            return []
    except Exception as e:
        print(e)
        return []