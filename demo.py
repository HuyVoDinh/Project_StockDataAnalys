import pandas as pd

from StockData import stock_data
from StockData.stock_data import StockData

stock_data = StockData()
stock_data.init_listing()
symbol_list = stock_data.listing_information_by_group()
for symbol in symbol_list['symbol']:
    print(symbol)
print(len(symbol_list))