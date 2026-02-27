from Enum.liquidity import Liquidity, Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend, Momentum, MarketState
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Timing.TimingFilter import TimingFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter


#Volume
def volume_filter_single_indicator_1(comp):
    volFilter = VolumeFilter()
    liquidity = volFilter.filter_minimum_liquidity(comp.company_data[-1])
    if liquidity == Liquidity.Good:
        return comp.symbol
    return None

def volume_filter_single_indicator_2(comp):
    volFilter = VolumeFilter()
    smart_market = volFilter.find_smart_market((comp.company_data[-1]))
    if smart_market == Cash_Flow.Smart_Money:
        return comp.symbol
    return None

def volume_filter_single_indicator_3(comp):
    volFilter = VolumeFilter()
    gather = volFilter.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    if gather == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_4(comp):
    volFilter = VolumeFilter()
    vol_and_price = volFilter.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    if vol_and_price == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_5(comp):
    volFilter = VolumeFilter()
    supply = volFilter.check_supply_test(comp.company_data[-1], comp.company_data[-2])
    if supply == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_6(comp):
    volFilter = VolumeFilter()
    obv = volFilter.check_obv(comp.company_data[-1], comp.company_data[-2])
    if obv == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_7(comp):
    volFilter = VolumeFilter()
    vo = volFilter.check_vo(comp.company_data[-1])
    if vo == Volume.Money_In:
        return comp.symbol
    return None

def volume_filter_single_indicator_8(comp):
    volFilter = VolumeFilter()
    accum = volFilter.check_accumulation_and_distribution(comp.company_data[-1], comp.company_data[-2])
    if accum == Volume.Money_In:
        return comp.symbol
    return None

############## Volatility #####################

def volatility_filter_single_indicator_1(comp):
    volatility = VolatilityFilter()
    daily_cand = volatility.daily_candlestick_range(comp.company_data[-1])
    if daily_cand == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_2(comp):
    volatility = VolatilityFilter()
    cand_range = volatility.candlestick_range(comp.company_data[-1])
    if cand_range == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_3(comp):
    volatility = VolatilityFilter()
    bandwidth = volatility.bandwidth_filter(comp.company_data[-1])
    if bandwidth == Emplitude.Break:
        return comp.symbol
    return None

def volatility_filter_single_indicator_4(comp):
    volatility = VolatilityFilter()
    bandwidth = volatility.bandwidth_filter2(comp.company_data[-1])
    if bandwidth == Emplitude.Good:
        return comp.symbol
    return None

def volatility_filter_single_indicator_5(comp):
    volatility = VolatilityFilter()
    donchain = volatility.donchian_channel_filter(comp.company_data[-1])
    if donchain == Emplitude.Good:
        return comp.symbol
    return None


##################### Timing #################
def timing_filter_single_indicator_1(comp):
    timing = TimingFilter()
    retest = timing.setup_retest(comp.company_data[-1], comp.company_data[-2])
    if retest == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_2(comp):
    timing = TimingFilter()
    back_on_track = timing.getting_back_on_track_for_recovery(comp.company_data[-1], comp.company_data[-2])
    if back_on_track == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_3(comp):
    timing = TimingFilter()
    entry = timing.confirm_entry_point(comp.company_data[-1], comp.company_data[-2])
    if entry == Trend.Recovery:
        return comp.symbol
    return None

def timing_filter_single_indicator_4(comp):
    timing = TimingFilter()
    middle_band = timing.setup_middle_bands(comp.company_data[-1], comp.company_data[-2])
    if middle_band == Trend.Good:
        return comp.symbol
    return None

def timing_filter_single_indicator_5(comp):
    timing = TimingFilter()
    macd = timing.setup_MACD(comp.company_data[-1])
    if macd == Trend.Recovery:
        return comp.symbol
    return None


############################ ShortTerm #######################
def short_filter_single_indicator_1(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    if ma == Trend.Up:
        return comp.symbol
    return None

def short_filter_single_indicator_2(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.RSI_momentum_confirmation(comp.company_data[-1])
    if result == Trend.Good:
        return comp.symbol
    return None

def short_filter_single_indicator_3(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.check_incoming_momentum(comp.company_data[-1], comp.company_data[-2])
    if ma == Momentum.In:
        return comp.symbol
    return None

def short_filter_single_indicator_4(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.check_trend_or_sideways(comp.company_data[-1])
    if result == Trend.Good:
        return comp.symbol
    return None

def short_filter_single_indicator_5(comp):
    short_term = ShortTermTrendFilter()
    ma = short_term.price_action_confirms_trend(comp.company_data[-1], comp.company_data[-2])
    if ma == Trend.Up:
        return comp.symbol
    return None

def short_filter_single_indicator_6(comp):
    short_term = ShortTermTrendFilter()
    result = short_term.check_end_trend(comp.company_data[-1])
    if result == MarketState.EARLY_TREND:
        return comp.symbol
    return None

