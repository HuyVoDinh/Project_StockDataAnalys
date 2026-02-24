from Enum.liquidity import Liquidity, Cash_Flow, Volume
from Filter.Volume.TimingFilter import TimingFilter
from Filter.Volume.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Filter.Volume.ShortTermTrendFilter import ShortTermTrendFilter
from Model.Indicator import Price
from StockData import stock_data
from Model.Company import Company, CompanyData
from StockData.stock_analyzer import StockAnalyzer
from StockData.stock_data import StockData
from Model.Indicator import MovingAverage, Moving_Average_Convergence_Divergence, AverageDirectionalIndex, DonchianChannel, BollingerBands, Price

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    stock_data = StockData()
    stock_data.init_listing()
    symbol_list = stock_data.listing_information_all_symbols()



    symbol = "VCB"
    stock_analyzer = StockAnalyzer(symbol)
    stock_analyzer.init_Stock()
    stock_analyzer.update_data_frame("2025-12-01", "2026-02-24")
    # stock_analyzer.Calculate_Trading_Value()
    stock_analyzer.update_full_indicator()
    print(stock_analyzer.data_frame)
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
    print(f"{comp.symbol}: - VolumeFilter: has filter_minimum_liquidity: {volFilter.filter_minimum_liquidity(comp.company_data[-1]).name}")
    print(f"{comp.symbol}: - VolumeFilter: has find_smart_market: {volFilter.find_smart_market((comp.company_data[-1])).name}")
    print(f"{comp.symbol}: - VolumeFilter: has find_smart_market: {volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3]).name}")

    shortTerm = ShortTermTrendFilter()
    print(f"{comp.symbol}: - Short-term: has moving_average_filter: {shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2]).name}")
    print(f"{comp.symbol}: - Short-term: has RSI_momentum_confirmation: {shortTerm.RSI_momentum_confirmation(comp.company_data[-1]).name}")
    print(f"{comp.symbol}: - Short-term: has check_incoming_momentum: {shortTerm.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2]).name}")

    volatility = VolatilityFilter()
    print(f"{comp.symbol}: - VolatilityFilter: has daily_candlestick_range: {volatility.daily_candlestick_range(comp.company_data[-1]).name}")
    print(f"{comp.symbol}: - VolatilityFilter: has candlestick_range: {volatility.candlestick_range(comp.company_data[-1]).name}")
    print(f"{comp.symbol}: - VolatilityFilter: has atr_filter: {volatility.atr_filter(comp.company_data[-1]).name}")

    timingFilter = TimingFilter()
    print(f"{comp.symbol}: - timingFilter: has setup_retest: {timingFilter.setup_retest(comp.company_data[-1], comp.company_data[-2]).name}")
    print(f"{comp.symbol}: - timingFilter: has getting_back_on_track_for_recovery: {timingFilter.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2]).name}")
    print(f"{comp.symbol}: - timingFilter: has confirm_entry_point: {timingFilter.confirm_entry_point(comp.company_data[-1], comp.company_data[-2]).name}")

    # print(f"{comp.symbol}: has check_volume_and_price {volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: has check_supply_test{volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: has check_obv{volFilter.check_obv(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: has check_accumulation_and_distribution{volFilter.check_accumulation_and_distribution(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: has check_vo{volFilter.check_vo(comp.company_data[-1]).name}")
    #
    # shortTerm = ShortTermTrendFilter()
    # print(f"{comp.symbol}: - Short-term: has moving_average_filter: {shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: - Short-term: has RSI_momentum_confirmation: {shortTerm.RSI_momentum_confirmation(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - Short-term: has check_incoming_momentum: {shortTerm.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: - Short-term: has check_trend_or_sideways: {shortTerm.check_trend_or_sideways(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - Short-term: has price_action_confirms_trend: {shortTerm.price_action_confirms_trend(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: - Short-term: has check_stable_uptrend: {shortTerm.check_stable_uptrend(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - Short-term: has check_end_trend: {shortTerm.check_end_trend(comp.company_data[-1]).name}")
    #
    # volatility = VolatilityFilter()
    # print(f"{comp.symbol}: - VolatilityFilter: has daily_candlestick_range: {volatility.daily_candlestick_range(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - VolatilityFilter: has candlestick_range: {volatility.candlestick_range(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - VolatilityFilter: has atr_filter: {volatility.atr_filter(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - VolatilityFilter: has bandwidth_filter: {volatility.bandwidth_filter(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - VolatilityFilter: has bandwidth_filter2: {volatility.bandwidth_filter2(comp.company_data[-1]).name}")
    # print(f"{comp.symbol}: - VolatilityFilter: has donchian_channel_filter: {volatility.donchian_channel_filter(comp.company_data[-1]).name}")
    #
    # timingFilter = TimingFilter()
    # print(f"{comp.symbol}: - timingFilter: has setup_retest: {timingFilter.setup_retest(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: - timingFilter: has getting_back_on_track_for_recovery: {timingFilter.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: - timingFilter: has confirm_entry_point: {timingFilter.confirm_entry_point(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: - timingFilter: has setup_middle_bands: {timingFilter.setup_middle_bands(comp.company_data[-1], comp.company_data[-2]).name}")
    # print(f"{comp.symbol}: - timingFilter: has setup_middle_bands: {timingFilter.setup_MACD(comp.company_data[-1]).name}")