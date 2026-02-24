from time import sleep

from Enum.liquidity import Liquidity, Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend, Momentum
from Filter.Volume.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Volume.TimingFilter import TimingFilter
from Filter.Volume.VolatilityFilter import VolatilityFilter
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
    # symbol_list = stock_data.listing_information_by_exchange("HNX")

    counter = 1

    for symbol in symbol_list['symbol']:
        #Setup filter - remove symbol is less than 30B
        # stock_analyzer = StockAnalyzer(symbol)
        # stock_analyzer.init_Stock()
        # stock_analyzer.update_data_frame("2025-12-01", "2026-02-10")
        # trading_value = stock_analyzer.Calculate_Trading_Value()

        if counter == 19:
            counter = 1
            sleep(60)
        else:
            counter += 1

        stock_analyzer = StockAnalyzer(symbol)
        stock_analyzer.init_Stock()
        stock_analyzer.update_data_frame("2025-12-01", "2026-02-24")

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

        volFilter = VolumeFilter()
        shortTerm = ShortTermTrendFilter()
        volatility = VolatilityFilter()
        timingFilter = TimingFilter()
        liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
        smart_market = volFilter.find_smart_market((comp.company_data[-1]))
        gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
        ma_signal = shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
        rsi_signal = shortTerm.RSI_momentum_confirmation(comp.company_data[-1])
        momentum = shortTerm.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2])
        daily_candlestick_range = volatility.daily_candlestick_range(comp.company_data[-1])
        # candlestick_range = volatility.candlestick_range(comp.company_data[-1])
        atr_signal = volatility.atr_filter(comp.company_data[-1])
        # retest = timingFilter.setup_retest(comp.company_data[-1], comp.company_data[-2])
        # recovery = timingFilter.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2])
        # entry_point = timingFilter.confirm_entry_point(comp.company_data[-1], comp.company_data[-2])
        if liquidity == Liquidity.Good and smart_market == Cash_Flow.Smart_Money and gather == Volume.Money_In and ma_signal == Trend.Up and rsi_signal == Trend.Good and momentum == Momentum.In and daily_candlestick_range == Emplitude.Good and atr_signal == Emplitude.Good:
            print(f"{symbol} is good")
            sleep(1000)
        else:
            print(f"{symbol} is bad")