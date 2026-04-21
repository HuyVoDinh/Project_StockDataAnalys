from src.enums.liquidity import Cash_Flow, Liquidity
from src.enums.signal import Emplitude
from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter
from src.filters.price_action_filter import PriceActionFilter
from src.filters.liquidity_filter import LiquidityFilter
from src.filters.market_trend_filter import MarketTrendFilter


# Price action Strategy
# Special candlestick patterns (pin bar, engulfing, doji)
# volume confirms the trend.
# RSI is not overbought or oversold.
# MA20 is rising.
# Stable liquidity
# Market trend remains stable.
#
# Entry: When a special candlestick pattern appears + volume increases + RSI is good + trend is favorable.
# Stop: Below the bottom of a pin bar/engulfing candle or below the MA20
# Target: 3-5% (Depending on the model)

def price_action_setup(comp, market_data = None):
    """
    Identifying tradings signals based on price action analysis.
    :param comp:
    :param market_data:
    :return:
    """
    if not comp or len(comp.company_data) < 5:
        return None

    # Get the latest data
    current_data = comp.company_data[-1]
    previous_data = comp.company_data[-2]

    # Init filters
    volume_filter = VolumeFilter()
    short_term_filter = ShortTermTrendFilter()
    volatility_filter = VolatilityFilter()
    price_action_filter = PriceActionFilter()
    liquidity_filter = LiquidityFilter()
    market_trend_filter = MarketTrendFilter()

    smart_money = volume_filter.find_smart_market(current_data)
    ma_trend = short_term_filter.moving_average_filter(current_data, previous_data)
    rsi = short_term_filter.RSI_momentum_confirmation(current_data)
    liquidity_stable = liquidity_filter.check_liquidity_stability(comp.company_data)

    # Check market trends
    market_trend = Trend.Up
    if market_data and len(market_data) >= 20:
        market_trend = market_trend_filter.check_market_trend(market_data)

    # Check the price action candlestick pattern.
    pin_bar = price_action_filter.check_pin_bar(current_data)
    engulfing = price_action_filter.check_engulfing_pattern(current_data, previous_data)
    doji = price_action_filter.check_doji(current_data)
    inside_bar = price_action_filter.check_inside_bar(current_data, previous_data)
    outside_bar = price_action_filter.check_outside_bar(current_data, previous_data)

    # Check the volume increase condition to confirm the signal.
    volume_confirmation = current_data.volume > current_data.moving_average_20.ma_volume * 1.2

    if (pin_bar in [Trend.Up, Trend.Down] and
        smart_money == Cash_Flow.Smart_Money and
        ma_trend == Trend.Up and
        rsi == Trend.Good and
        liquidity_stable == Liquidity.Good and
        market_trend == Trend.Up and
        volume_confirmation):
        return comp.symbol
    elif (engulfing in [Trend.Up, Trend.Down] and
          smart_money == Cash_Flow.Smart_Money and
          ma_trend == Trend.Up and
          rsi == Trend.Good and
          liquidity_stable == Liquidity.Good and
          market_trend == Trend.Up and
          volume_confirmation):
        return comp.symbol
    # Break out
    elif (outside_bar in [Emplitude.Break] and
          smart_money == Cash_Flow.Smart_Money and
          ma_trend == Trend.Up and
          rsi == Trend.Good and
          liquidity_stable == Liquidity.Good and
          market_trend == Trend.Up):
        return comp.symbol
    # Accumulation followed by reversal
    elif (inside_bar in [Emplitude.Tight] and
          smart_money == Cash_Flow.Smart_Money and
          ma_trend == Trend.Up and
          rsi == Trend.Good and
          liquidity_stable == Liquidity.Good and
          market_trend == Trend.Up):
        # Check further to see if the candle following the doji is a bullish candle.
        if current_data.price.close_price > current_data.price.open_price:
            return comp.symbol
    return None