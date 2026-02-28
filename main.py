from time import sleep

from Enum.liquidity import Liquidity, Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend, Momentum
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Timing.TimingFilter import TimingFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import Company, CompanyData
from Setup.Setup import setup_1, setup_4, setup_3, setup_2
from StockData.stock_analyzer import StockAnalyzer
from StockData.stock_data import StockData
import pandas as pd

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Init save data
    ##############  Volume  ######################
    symbol_list_1 = []
    symbol_list_2 = []
    symbol_list_3 = []
    symbol_list_4 = []

    stock_data = StockData()
    stock_data.init_listing()
    symbol_list = stock_data.listing_information_all_symbols()
    # symbol_list = stock_data.listing_information_by_exchange("HNX")

    counter = 1

    for symbol in symbol_list['symbol']:
        if counter == 19:
            counter = 1
            sleep(60)
        else:
            counter += 1

        stock_analyzer = StockAnalyzer(symbol)
        stock_analyzer.init_Stock()
        stock_analyzer.update_data_frame("2025-12-01", "2026-02-25")

        if stock_analyzer.data_frame is None:
            continue

        try:
            stock_analyzer.Calculate_Trading_Value()
            stock_analyzer.update_full_indicator()
            # print(stock_analyzer.data_frame)
            comp = Company(symbol)
            last_5 = stock_analyzer.data_frame.tail(5)
            print(comp.symbol)
            for index, row in last_5.iterrows():
                compData = CompanyData()
                compData.import_data(row)
                compData.trading_value = row['trading_value']
                compData.moving_average_10.ma_price = row['vol_ma10']
                compData.moving_average_10.ma_volume = row['price_ma10']
                compData.moving_average_10.window = 10
                compData.moving_average_20.ma_price = row['vol_ma20']
                compData.moving_average_20.ma_volume = row['price_ma20']
                compData.moving_average_20.window = 20
                compData.moving_average_50.ma_price = row['vol_ma50']
                compData.moving_average_50.ma_volume = row['price_ma50']
                compData.moving_average_50.window = 50
                compData.On_Balance_Volume = row['obv']
                compData.Volume_Oscillator = row['volume_osc']
                compData.Accumulation_Distribution = row['ad']
                compData.ATR_14 = row['atr_14']
                compData.ATR_MA5 = row['atr_ma5']
                compData.Bollinger_Bands.Middle = row['bb_middle']
                compData.Bollinger_Bands.BB_Upper = row['bb_upper']
                compData.Bollinger_Bands.BB_Lower = row['bb_lower']
                compData.Donchian_Channel.Middle = row['dc_middle']
                compData.Donchian_Channel.Upper_Channel = row['dc_upper']
                compData.Donchian_Channel.Lower_Channel = row['dc_lower']
                compData.RSI_14 = row['rsi_14']
                compData.ADX_14.ADX = row['adx_14']
                compData.ADX_14.plus_DI = row['plus_di']
                compData.ADX_14.minus_DI = row['minus_di']
                compData.MACD.MACD = row['macd']
                compData.MACD.signal = row['macd_signal']
                compData.MACD.histogram = row['macd_hist']
                # compData.StdDev_20 =
                comp.company_data.append(compData)
        except:
            print(comp.symbol + "can't check")
            continue

        if setup_1(comp) is not None:
            symbol_list_1.append(comp.symbol)

        if setup_2(comp) is not None:
            symbol_list_2.append(comp.symbol)

        if setup_3(comp) is not None:
            symbol_list_3.append(comp.symbol)

        if setup_4(comp) is not None:
            symbol_list_4.append(comp.symbol)

    ####### Export data
    df1 = pd.DataFrame(setup_1, columns=['setup_1'])
    df2 = pd.DataFrame(setup_2, columns=['setup_2'])
    df3 = pd.DataFrame(setup_3, columns=['setup_3'])
    df4 = pd.DataFrame(setup_4, columns=['setup_4'])

    result_data = pd.concat([df1, df2,df3,df4], axis=1)
    result_data.to_csv("""D:/Project/Project_StockDataAnalys/data.csv""", index=False)
