from Model.Indicator import Price
from StockData import stock_data
from Model.Company import Company
from StockData.stock_data import StockData

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    stock_data = StockData("HPG")
    stock_data.init_listing()
    symbol_list = stock_data.listing_information_all_symbols()

    for symbol in symbol_list['symbol']:
        print(symbol)