from Enum.liquidity import Liquidity, Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend, Momentum, MarketState
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Timing.TimingFilter import TimingFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter


#Volume
def volume_filter_single_indicator_2_1(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    if liquidity == Liquidity.Good and smart_market == Cash_Flow.Smart_Money:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_2(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    if liquidity == Liquidity.Good and gather == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_3(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    if liquidity == Liquidity.Good and vol_and_price == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_4(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    if liquidity == Liquidity.Good and supply == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_5(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    if liquidity == Liquidity.Good and obv == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_6(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    vo = volFilter.check_vo(comp.company_data[-1])
    if liquidity == Liquidity.Good and vo == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_7(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1])
    if liquidity == Liquidity.Good and accum == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_8(comp):
    volFilter = VolumeFilter()
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    if smart_market == Cash_Flow.Smart_Money and gather == Volume.Money_In:
        return comp.symbol
    return None


def volume_filter_single_indicator_2_9(comp):
    volFilter = VolumeFilter()
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    if smart_market == Cash_Flow.Smart_Money and vol_and_price == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_10(comp):
    volFilter = VolumeFilter()
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    if smart_market == Cash_Flow.Smart_Money and supply == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_11(comp):
    volFilter = VolumeFilter()
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    if smart_market == Cash_Flow.Smart_Money and obv == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_12(comp):
    volFilter = VolumeFilter()
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    vo = volFilter.check_vo(comp.company_data[-1])
    if smart_market == Cash_Flow.Smart_Money and vo == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_13(comp):
    volFilter = VolumeFilter()
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1])
    if smart_market == Cash_Flow.Smart_Money and accum == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_14(comp):
    volFilter = VolumeFilter()
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    if gather == Volume.Money_In and  vol_and_price == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_15(comp):
    volFilter = VolumeFilter()
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    if gather == Volume.Money_In and supply == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_16(comp):
    volFilter = VolumeFilter()
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    if gather == Volume.Money_In and obv == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_17(comp):
    volFilter = VolumeFilter()
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    vo = volFilter.check_vo(comp.company_data[-1])
    if gather == Volume.Money_In and vo == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_18(comp):
    volFilter = VolumeFilter()
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1])
    if gather == Volume.Money_In and accum == Volume.Money_In:
        return comp.symbol
    return None


def volume_filter_single_indicator_2_19(comp):
    volFilter = VolumeFilter()
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    if vol_and_price == Volume.Money_In and supply == Volume.Money_In:
        return comp.symbol
    return None


def volume_filter_single_indicator_2_20(comp):
    volFilter = VolumeFilter()
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    if vol_and_price == Volume.Money_In and obv == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_21(comp):
    volFilter = VolumeFilter()
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    vo = volFilter.check_vo(comp.company_data[-1])
    if vol_and_price == Volume.Money_In and vo == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_22(comp):
    volFilter = VolumeFilter()
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1])
    if vol_and_price == Volume.Money_In and accum == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_23(comp):
    volFilter = VolumeFilter()
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    if supply == Volume.Money_In and obv == Volume.Money_In:
        return comp.symbol
    return None


def volume_filter_single_indicator_2_24(comp):
    volFilter = VolumeFilter()
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    vo = volFilter.check_vo(comp.company_data[-1])
    if supply == Volume.Money_In and  vo == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_25(comp):
    volFilter = VolumeFilter()
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1])
    if supply == Volume.Money_In and accum == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_26(comp):
    volFilter = VolumeFilter()
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    vo = volFilter.check_vo(comp.company_data[-1])
    if obv == Volume.Money_In and vo == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_27(comp):
    volFilter = VolumeFilter()
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1])
    if obv == Volume.Money_In and accum == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_2_28(comp):
    volFilter = VolumeFilter()
    vo = volFilter.check_vo(comp.company_data[-1])
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1])
    if vo == Volume.Money_In and accum == Volume.Money_In:
        return comp.symbol
    return None

############## Volatility #####################

def volatility_filter_single_indicator_2_1(comp):
    volatility = VolatilityFilter()
    daily_cand = volatility.daily_candlestick_range(comp.company_data[-1])
    cand_range = volatility.candlestick_range(comp.company_data[-1])
    if daily_cand == Emplitude.Good and  cand_range == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2_2(comp):
    volatility = VolatilityFilter()
    daily_cand = volatility.daily_candlestick_range(comp.company_data[-1])
    bandwidth = volatility.bandwidth_filter(comp.company_data[-1])
    if daily_cand == Emplitude.Good and bandwidth == Emplitude.Break:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2_3(comp):
    volatility = VolatilityFilter()
    daily_cand = volatility.daily_candlestick_range(comp.company_data[-1])
    bandwidth = volatility.bandwidth_filter2(comp.company_data[-1])
    if daily_cand == Emplitude.Good and bandwidth == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2_4(comp):
    volatility = VolatilityFilter()
    daily_cand = volatility.daily_candlestick_range(comp.company_data[-1])
    donchain = volatility.donchian_channel_filter(comp.company_data[-1])
    if daily_cand == Emplitude.Good and donchain == Emplitude.Good:
        return comp.symbol
    return None




def volatility_filter_single_indicator_2_5(comp):
    volatility = VolatilityFilter()
    cand_range = volatility.candlestick_range(comp.company_data[-1])
    bandwidth = volatility.bandwidth_filter(comp.company_data[-1])
    if cand_range == Emplitude.Good and bandwidth == Emplitude.Break:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2_6(comp):
    volatility = VolatilityFilter()
    cand_range = volatility.candlestick_range(comp.company_data[-1])
    bandwidth = volatility.bandwidth_filter2(comp.company_data[-1])
    if cand_range == Emplitude.Good and bandwidth == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2_7(comp):
    volatility = VolatilityFilter()
    cand_range = volatility.candlestick_range(comp.company_data[-1])
    donchain = volatility.donchian_channel_filter(comp.company_data[-1])
    if cand_range == Emplitude.Good and donchain == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2_8(comp):
    volatility = VolatilityFilter()
    bandwidth = volatility.bandwidth_filter(comp.company_data[-1])
    bandwidth2 = volatility.bandwidth_filter2(comp.company_data[-1])
    if bandwidth == Emplitude.Break and bandwidth2 == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2_9(comp):
    volatility = VolatilityFilter()
    bandwidth = volatility.bandwidth_filter(comp.company_data[-1])
    donchain = volatility.donchian_channel_filter(comp.company_data[-1])
    if bandwidth == Emplitude.Break and donchain == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_10(comp):
    volatility = VolatilityFilter()
    bandwidth = volatility.bandwidth_filter2(comp.company_data[-1])
    donchain = volatility.donchian_channel_filter(comp.company_data[-1])
    if bandwidth == Emplitude.Good and donchain == Emplitude.Good:
        return comp.symbol
    return None

##################### Timing #################
def timing_filter_single_indicator_2_1(comp):
    timing = TimingFilter()
    retest = timing.setup_retest(comp.company_data[-1], comp.company_data[-2])
    back_on_track = timing.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2])
    if retest == Trend.Recovery and back_on_track == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_2_2(comp):
    timing = TimingFilter()
    retest = timing.setup_retest(comp.company_data[-1], comp.company_data[-2])
    entry = timing.confirm_entry_point(comp.company_data[-1], comp.company_data[-2])
    if retest == Trend.Recovery and entry == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_2_3(comp):
    timing = TimingFilter()
    retest = timing.setup_retest(comp.company_data[-1], comp.company_data[-2])
    middle_band = timing.setup_middle_bands(comp.company_data[-1], comp.company_data[-2])
    if retest == Trend.Recovery and middle_band == Trend.Good:
        return comp.symbol
    return None

def timing_filter_single_indicator_2_4(comp):
    timing = TimingFilter()
    retest = timing.setup_retest(comp.company_data[-1], comp.company_data[-2])
    macd = timing.setup_MACD(comp.company_data[-1])
    if retest == Trend.Recovery and macd == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_2_5(comp):
    timing = TimingFilter()
    back_on_track = timing.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2])
    entry = timing.confirm_entry_point(comp.company_data[-1], comp.company_data[-2])
    if back_on_track == Trend.Recovery and entry == Trend.Recovery:
        return comp.symbol
    return None


def timing_filter_single_indicator_2_6(comp):
    timing = TimingFilter()
    back_on_track = timing.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2])
    middle_band = timing.setup_middle_bands(comp.company_data[-1], comp.company_data[-2])
    if back_on_track == Trend.Recovery and middle_band == Trend.Good:
        return comp.symbol
    return None

def timing_filter_single_indicator_2_7(comp):
    timing = TimingFilter()
    back_on_track = timing.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2])
    macd = timing.setup_MACD(comp.company_data[-1])
    if back_on_track == Trend.Recovery and  macd == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_2_8(comp):
    timing = TimingFilter()
    entry = timing.confirm_entry_point(comp.company_data[-1], comp.company_data[-2])
    middle_band = timing.setup_middle_bands(comp.company_data[-1], comp.company_data[-2])
    if entry == Trend.Recovery and middle_band == Trend.Good:
        return comp.symbol
    return None


def timing_filter_single_indicator_2_8(comp):
    timing = TimingFilter()
    entry = timing.confirm_entry_point(comp.company_data[-1], comp.company_data[-2])
    macd = timing.setup_MACD(comp.company_data[-1])
    if entry == Trend.Recovery and macd == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_4(comp):
    timing = TimingFilter()
    middle_band = timing.setup_middle_bands(comp.company_data[-1], comp.company_data[-2])
    macd = timing.setup_MACD(comp.company_data[-1])
    if middle_band == Trend.Good and macd == Trend.Recovery:
        return comp.symbol
    return None

############################ ShortTerm #######################
def short_filter_single_indicator_2_1(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    rsi = short_term.RSI_momentum_confirmation(comp.company_data[-1])
    if ma == Trend.Up and rsi == Trend.Good:
        return comp.symbol
    return None


def short_filter_single_indicator_2_2(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    momentum = short_term.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2])
    if ma == Trend.Up and momentum == Momentum.In:
        return comp.symbol
    return None


def short_filter_single_indicator_2_3(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    trend = short_term.check_trend_or_sideways(comp.company_data[-1])
    if ma == Trend.Up and trend == Trend.Good:
        return comp.symbol
    return None

def short_filter_single_indicator_2_4(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    price_action = short_term.price_action_confirms_trend(comp.company_data[-1], comp.company_data[-2])
    if ma == Trend.Up and price_action == Trend.Up:
        return comp.symbol
    return None


def short_filter_single_indicator_2_5(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    trend = short_term.check_end_trend(comp.company_data[-1])
    if ma == Trend.Up and trend == MarketState.EARLY_TREND:
        return comp.symbol
    return None

def short_filter_single_indicator_2_6(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.RSI_momentum_confirmation(comp.company_data[-1])
    ma = short_term.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2])
    if result == Trend.Good and ma == Momentum.In:
        return comp.symbol
    return None

def short_filter_single_indicator_2_7(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.RSI_momentum_confirmation(comp.company_data[-1])
    trend = short_term.check_trend_or_sideways(comp.company_data[-1])
    if result == Trend.Good and trend == Trend.Good:
        return comp.symbol
    return None


def short_filter_single_indicator_2_8(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.RSI_momentum_confirmation(comp.company_data[-1])
    ma = short_term.price_action_confirms_trend(comp.company_data[-1], comp.company_data[-2])
    if result == Trend.Good and ma == Trend.Up:
        return comp.symbol
    return None


def short_filter_single_indicator_2_9(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.RSI_momentum_confirmation(comp.company_data[-1])
    trend = short_term.check_end_trend(comp.company_data[-1])
    if result == Trend.Good and trend == MarketState.EARLY_TREND:
        return comp.symbol
    return None

def short_filter_single_indicator_2_10(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2])
    trend = short_term.check_trend_or_sideways(comp.company_data[-1])
    if ma == Momentum.In and trend == Trend.Good:
        return comp.symbol
    return None

def short_filter_single_indicator_2_11(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2])
    price_action = short_term.price_action_confirms_trend(comp.company_data[-1], comp.company_data[-2])
    if ma == Momentum.In and price_action == Trend.Up:
        return comp.symbol
    return None

def short_filter_single_indicator_2_12(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2])
    trend = short_term.check_end_trend(comp.company_data[-1])
    if ma == Momentum.In and trend == MarketState.EARLY_TREND:
        return comp.symbol
    return None

def short_filter_single_indicator_2_13(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.check_trend_or_sideways(comp.company_data[-1])
    trend = short_term.check_end_trend(comp.company_data[-1])
    if result == Trend.Good and trend == MarketState.EARLY_TREND:
        return comp.symbol
    return None

def short_filter_single_indicator_2_14(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.check_trend_or_sideways(comp.company_data[-1])
    ma = short_term.price_action_confirms_trend(comp.company_data[-1], comp.company_data[-2])
    if result == Trend.Good and ma == Trend.Up:
        return comp.symbol
    return None

def short_filter_single_indicator_2_15(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.price_action_confirms_trend(comp.company_data[-1], comp.company_data[-2])
    result = short_term.check_end_trend(comp.company_data[-1])
    if ma == Trend.Up and result == MarketState.EARLY_TREND:
        return comp.symbol
    return None
