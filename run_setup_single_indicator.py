from time import sleep

from Enum.liquidity import Liquidity, Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend, Momentum
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Timing.TimingFilter import TimingFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import Company, CompanyData
from Setup.setup_single_indicator_1 import *
from StockData.stock_analyzer import StockAnalyzer
from StockData.stock_data import StockData
from Setup import *
import pandas as pd

from demo import result_data

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Init save data
    ##############  Volume  ######################
    vol_symbol_list_1 = []
    vol_symbol_list_2 = []
    vol_symbol_list_3 = []
    vol_symbol_list_4 = []
    vol_symbol_list_5 = []
    vol_symbol_list_6 = []
    vol_symbol_list_7 = []
    vol_symbol_list_8 = []
    ##############  Volatility  ######################
    vola_symbol_list_1 = []
    vola_symbol_list_2 = []
    vola_symbol_list_3 = []
    vola_symbol_list_4 = []
    vola_symbol_list_5 = []
    ##############  Timing  ######################
    timing_symbol_list_1 = []
    timing_symbol_list_2 = []
    timing_symbol_list_3 = []
    timing_symbol_list_4 = []
    timing_symbol_list_5 = []
    ##############  ShortTerm  ######################
    short_symbol_list_1 = []
    short_symbol_list_2 = []
    short_symbol_list_3 = []
    short_symbol_list_4 = []
    short_symbol_list_5 = []
    short_symbol_list_6 = []
    #####################################################################
    stock_data = StockData()
    stock_data.init_listing()
    symbol_list = stock_data.listing_information_all_symbols()
    # symbol_list = stock_data.listing_information_by_exchange("HNX")

    counter = 1

    for symbol in symbol_list['symbol']:
        if counter == 18:
            counter = 1
            sleep(60)
        else:
            counter += 1

        try:
            stock_analyzer = StockAnalyzer(symbol)
            stock_analyzer.init_Stock()
            stock_analyzer.update_data_frame("2025-12-01", "2026-02-25")

            if stock_analyzer.data_frame is None:
                continue

            stock_analyzer.Calculate_Trading_Value()
            stock_analyzer.update_full_indicator()
            # print(stock_analyzer.data_frame)
            comp = Company(symbol)
            last_5 = stock_analyzer.data_frame.tail(5)
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

        print(comp.symbol)

        if volume_filter_single_indicator_1(comp) is not None:
            vol_symbol_list_1.append(comp.symbol)
        if volume_filter_single_indicator_2(comp) is not None:
            vol_symbol_list_2.append(comp.symbol)
        if volume_filter_single_indicator_3(comp) is not None:
            vol_symbol_list_3.append(comp.symbol)
        if volume_filter_single_indicator_4(comp) is not None:
            vol_symbol_list_4.append(comp.symbol)
        if volume_filter_single_indicator_5(comp) is not None:
            vol_symbol_list_5.append(comp.symbol)
        if volume_filter_single_indicator_6(comp) is not None:
            vol_symbol_list_6.append(comp.symbol)
        if volume_filter_single_indicator_7(comp) is not None:
            vol_symbol_list_7.append(comp.symbol)
        if volume_filter_single_indicator_8(comp) is not None:
            vol_symbol_list_8.append(comp.symbol)

        if volatility_filter_single_indicator_1(comp) is not None:
            vola_symbol_list_1.append(comp.symbol)
        if volatility_filter_single_indicator_2(comp) is not None:
            vola_symbol_list_2.append(comp.symbol)
        if volatility_filter_single_indicator_3(comp) is not None:
            vola_symbol_list_3.append(comp.symbol)
        if volatility_filter_single_indicator_4(comp) is not None:
            vola_symbol_list_4.append(comp.symbol)
        if volatility_filter_single_indicator_5(comp) is not None:
            vola_symbol_list_5.append(comp.symbol)

        if timing_filter_single_indicator_1(comp) is not None:
            timing_symbol_list_1.append(comp.symbol)
        if timing_filter_single_indicator_2(comp) is not None:
            timing_symbol_list_2.append(comp.symbol)
        if timing_filter_single_indicator_3(comp) is not None:
            timing_symbol_list_3.append(comp.symbol)
        if timing_filter_single_indicator_4(comp) is not None:
            timing_symbol_list_4.append(comp.symbol)
        if timing_filter_single_indicator_5(comp) is not None:
            timing_symbol_list_5.append(comp.symbol)

        if short_filter_single_indicator_1(comp) is not None:
            short_symbol_list_1.append(comp.symbol)
        if short_filter_single_indicator_2(comp) is not None:
            short_symbol_list_2.append(comp.symbol)
        if short_filter_single_indicator_3(comp) is not None:
            short_symbol_list_3.append(comp.symbol)
        if short_filter_single_indicator_4(comp) is not None:
            short_symbol_list_4.append(comp.symbol)
        if short_filter_single_indicator_5(comp) is not None:
            short_symbol_list_5.append(comp.symbol)
        if short_filter_single_indicator_6(comp) is not None:
            short_symbol_list_6.append(comp.symbol)


    ####### Export data
    df1 = pd.DataFrame(vol_symbol_list_1, columns=['vol_symbol_list_1'])
    df2 = pd.DataFrame(vol_symbol_list_2, columns=['vol_symbol_list_2'])
    df3 = pd.DataFrame(vol_symbol_list_3, columns=['vol_symbol_list_3'])
    df4 = pd.DataFrame(vol_symbol_list_4, columns=['vol_symbol_list_4'])
    df5 = pd.DataFrame(vol_symbol_list_5, columns=['vol_symbol_list_5'])
    df6 = pd.DataFrame(vol_symbol_list_6, columns=['vol_symbol_list_6'])
    df7 = pd.DataFrame(vol_symbol_list_7, columns=['vol_symbol_list_7'])

    df8 = pd.DataFrame(vola_symbol_list_1, columns=['vola_symbol_list_1'])
    df9 = pd.DataFrame(vol_symbol_list_2, columns=['vol_symbol_list_2'])
    df10 = pd.DataFrame(vol_symbol_list_3, columns=['vol_symbol_list_3'])
    df11 = pd.DataFrame(vol_symbol_list_4, columns=['vol_symbol_list_4'])
    df12 = pd.DataFrame(vol_symbol_list_5, columns=['vol_symbol_list_5'])

    df13 = pd.DataFrame(timing_symbol_list_1, columns=['timing_symbol_list_1'])
    df14 = pd.DataFrame(timing_symbol_list_2, columns=['timing_symbol_list_2'])
    df15 = pd.DataFrame(timing_symbol_list_3, columns=['timing_symbol_list_3'])
    df16 = pd.DataFrame(timing_symbol_list_4, columns=['timing_symbol_list_4'])
    df17 = pd.DataFrame(timing_symbol_list_5, columns=['timing_symbol_list_5'])

    df18 = pd.DataFrame(short_symbol_list_1, columns=['short_symbol_list_1'])
    df19 = pd.DataFrame(short_symbol_list_2, columns=['short_symbol_list_2'])
    df20 = pd.DataFrame(short_symbol_list_3, columns=['short_symbol_list_3'])
    df21 = pd.DataFrame(short_symbol_list_4, columns=['short_symbol_list_4'])
    df22 = pd.DataFrame(short_symbol_list_5, columns=['short_symbol_list_5'])
    df23 = pd.DataFrame(short_symbol_list_6, columns=['short_symbol_list_6'])

    result_data = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14,df15, df16,df17,df18,df19, df20, df21,df22,df23], axis=1)
    result_data.to_csv("""D:/Project/Project_StockDataAnalys/data.csv""", index=False)