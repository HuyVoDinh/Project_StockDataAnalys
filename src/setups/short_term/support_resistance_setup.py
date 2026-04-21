from src.enums.liquidity import Cash_Flow, Liquidity
from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volume.VolumeFilter import VolumeFilter
from src.filters.support_resistance_filter import SupportResistanceFilter
from src.filters.liquidity_filter import LiquidityFilter
from src.filters.market_trend_filter import MarketTrendFilter


# Support Resistance Strategy
# Price is near strong support level.
# volume increases when bouncing up from support.
# RSI is not oversold.
# MA20 is rising.
# Stable liquidity
# The market trend is in the right direction.
#
# Entry: When the price bounces up from support + volume increases + RSI is good + trend is favorable.
# Stop: Below support level
# Target: The nearest resistance level is 4-6%.

def support_resistance_setup(comp, market_data = None):
    """
    Identify tradings signals based on support/resistance analysis.
    :param comp:
    :param market_data:
    :return:
    """
    if not comp or len(comp.company_data) < 5:
        return None

    current_data = comp.company_data[-1]
    previous_data = comp.company_data[-2]

    volume_filter = VolumeFilter()
    short_term_filter = ShortTermTrendFilter()
    support_resistance_filter = SupportResistanceFilter()
    liquidity_filter = LiquidityFilter()
    market_trend_filter = MarketTrendFilter()

    smart_money = volume_filter.find_smart_market(current_data)
    ma_trend = short_term_filter.moving_average_filter(current_data, previous_data)
    rsi = short_term_filter.RSI_momentum_confirmation(current_data)
    liquidity_stable = liquidity_filter.check_liquidity_stability(comp.company_data)

    market_trend = Trend.Up
    if market_data and len(market_data) >= 20:
        market_trend = market_trend_filter.check_market_trend(market_data)

    support_levels = support_resistance_filter.find_support_levels(comp.company_data)
    resistance_levels = support_resistance_filter.find_registance_levels(comp.company_data)

    near_support = support_resistance_filter.is_near_support(current_data.price.close_price, support_levels, threshold=0.015) # 1.5%
    support_bounce = support_resistance_filter.check_support_bounce(comp.company_data, current_data)
    resistance_break = support_resistance_filter.check_resistance_break(comp.company_data, current_data)
    volume_confirmation = current_data.volume > current_data.moving_average_20.ma_volume * 1.3

    # Conditions for pop-ups from support
    if (near_support and
        support_bounce == Trend.Up and
        smart_money == Cash_Flow.Smart_Money and
        ma_trend == Trend.Up and
        rsi in [Trend.Good, Trend.Weak] and
        liquidity_stable == Liquidity.Good and
        market_trend == Trend.Up and
        volume_confirmation):
        return comp.symbol
    elif (resistance_break == Trend.Up and
        smart_money == Cash_Flow.Smart_Money and
        ma_trend == Trend.Up and
        rsi in [Trend.Good, Trend.Weak] and
        liquidity_stable == Liquidity.Good and
        market_trend == Trend.Up and
        volume_confirmation):
        return comp.symbol
    elif (near_support and
        smart_money == Cash_Flow.Smart_Money and
        ma_trend == Trend.Up and
        rsi in [Trend.Good, Trend.Weak] and
        liquidity_stable == Liquidity.Good and
        market_trend == Trend.Up and
        volume_confirmation):
        return comp.symbol
    elif (near_support and
        smart_money == Cash_Flow.Smart_Money and
        ma_trend == Trend.Up and
        rsi in [Trend.Good, Trend.Weak] and
        liquidity_stable == Liquidity.Good and
        market_trend == Trend.Up and
        current_data.price.close_price > current_data.price.open_price): #Candle rise
        if current_data.volume > previous_data.volume * 0.8:
            return comp.symbol

    return None