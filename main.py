from Model.Indicator import Price
from StockData import StockData
from Model.Company import Company
from StockData.StockData import listing_information_all_symbols, get_trading_price, example, On_Balance_Volume, \
    Volume_Oscillator, Accumulation_Distribution

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    company = Company('NVL')
    # symbols_list = ['NVL']
    # data = get_trading_price(company.symbol)
    # print(data.head())
    Accumulation_Distribution()