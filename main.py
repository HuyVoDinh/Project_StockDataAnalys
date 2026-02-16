from StockData import StockData
from StockData.StockData import listing_information_all_symbols, get_trading_price

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    symbols_list = ['NVL', 'VCI', 'VCB']
    data = get_trading_price(symbols_list)
    print(data.head())