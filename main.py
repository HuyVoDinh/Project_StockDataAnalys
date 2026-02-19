from Model.Indicator import Price
from StockData import stock_data
from Model.Company import Company
from StockData.stock_data import StockData

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    company = Company('NVL')
    stock_data = StockData('HPG')
    stock_data.init_Trading()
    stock_data.update_data_frame(start="2026-01-01", end="2026-02-19")
    # trading_info = stock_data.get_trading_price()
    price = stock_data.Calculate_Relative_Strength_Index()
    # print(trading_info)
    print(price)
    # for p in price:
    #     print(f"MA{p.window}: price: {p.ma_price} - volume {p.ma_volume}")