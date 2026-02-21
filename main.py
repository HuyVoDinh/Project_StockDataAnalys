from Enum.liquidity import Liquidity
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Indicator import Price
from StockData import stock_data
from Model.Company import Company, CompanyData
from StockData.stock_analyzer import StockAnalyzer
from StockData.stock_data import StockData

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    stock_data = StockData()
    stock_data.init_listing()
    symbol_list = stock_data.listing_information_all_symbols()

    for symbol in symbol_list['symbol']:
        #Setup filter - remove symbol is less than 30B
        stock_analyzer = StockAnalyzer(symbol)
        stock_analyzer.init_Stock()
        stock_analyzer.update_data_frame("2025-12-01", "2026-02-10")
        trading_value = stock_analyzer.Calculate_Trading_Value()

    # symbol = "HPG"
    # stock_analyzer = StockAnalyzer(symbol)
    # stock_analyzer.init_Stock()
    # stock_analyzer.update_data_frame("2025-12-01", "2026-02-10")
    # stock_analyzer.Calculate_Trading_Value()
    # print(stock_analyzer.data_frame)
    comp = Company(symbol)
    last_5 = stock_analyzer.data_frame.tail(5)
    for index, row in last_5.iterrows():
        compData = CompanyData()
        compData.import_data(row)
        compData.trading_value = row['trading_value']
        comp.company_data.append(compData)

    volFilter = VolumeFilter()
    if volFilter.filter_minimum_liquidity(comp.company_data[-1]) == Liquidity.Good:
        print(f"{comp.symbol}: has good liquidity: {comp.company_data[-1].trading_value}")
    else:
        print(f"{comp.symbol}: has weak liquidity: {comp.company_data[-1].trading_value}")
