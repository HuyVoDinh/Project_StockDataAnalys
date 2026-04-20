from src.enums.liquidity import Cash_Flow
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


# Breakout with volume Confirmation (Medium-term)
# Giá phá đỉnh 20 phiên
# volume > 2 x MA20 tại thời điểm breakout
# RSI > 60 (động lượng tăng)
# ADX > 30 (xu hướng mạnh)
#
# Entry: khi giá đóng cưa trên đỉnh mới
# Stop: dưới đáy của cây nến breakout
# Target: 3R (10-15%)
def breakout_volume_setup(comp):
    shortTerm = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()

    # Find 20 day high
    high20 = max(data.price.close_price for data in comp.company_data[-20:])

    # Breakout
    breakout = comp.company_data[-1].price.close_price > high20

    # volume confimation
    volume_confirmation = volume.find_smart_market(comp.company_data[-1]) == Cash_Flow.Smart_Money

    # Momentum confirmation
    rsi_momentum = comp.company_data[-1].RSI_14 > 60

    # Trend strength
    adx_strong = comp.company_data[-1].ADX_14.ADX > 30

    if breakout and volume_confirmation and rsi_momentum and adx_strong:
        return comp.symbol
    return None
