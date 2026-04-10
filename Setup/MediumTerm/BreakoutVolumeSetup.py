from Enum.liquidity import Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import CompanyData, Company

# Breakout with Volume Confirmation (Medium-term)
# Giá phá đỉnh 20 phiên
# Volume > 2 x MA20 tại thời điểm breakout
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
    high20 = max(data for data in comp.company_data[-20:])

    # Breakout
    breakout = comp.company_data[-1].price.close_price > high20

    # Volume confimation
    volume_confirmation = volume.find_smart_market(comp.company_data[-1]) == Cash_Flow.Smart_Money

    # Momentum confirmation
    rsi_momentum = comp.company_data[-1].RSI_14 > 60

    # Trend strength
    adx_strong = comp.company_data[-1].ADX_14 > 30

    if breakout and volume_confirmation and rsi_momentum and adx_strong:
        return comp.symbol
    return None
