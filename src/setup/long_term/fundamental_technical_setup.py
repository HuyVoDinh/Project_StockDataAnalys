from src.enums.liquidity import Cash_Flow
from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


# Fundamental + Technical setup (Long-term)
# P/E < ngành trung bình
# ROE > 15%
# Giá trên MA50
# volume ổn định
# RSI 40-60
#
# Entry: Khi có tín hiểu kỹ thuật tích cực
# Stop dưới MA50 khoảng 7%
# Target: theo xu hướng dài hạn (30-50%)

def fundamental_technical_setup(comp):
    shortTerm = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()

    #Technical condition
    price_above_ma50 = comp.company_data[-1].price.close_price > comp.company_data[-1].moving_average_50.ma_price
    volume_stable = volume.find_smart_market(comp.company_data[-1]) in [Cash_Flow.Smart_Money, Cash_Flow.Weak]
    rsi_neutral = 40 <= comp.company_data[-1].RSI_14 <= 60
    uptrend = shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2]) in [Trend.Up, Trend.Down]

    #Note: Fundamental data would need to be added to the CompanyData model
    # For now, we'll focus on the technical conditions that can be evaluated

    if price_above_ma50 and volume_stable and rsi_neutral and uptrend:
        return comp.symbol
    return None