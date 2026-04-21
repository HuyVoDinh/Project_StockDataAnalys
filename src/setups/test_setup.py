from src.enums.liquidity import Cash_Flow, Volume, Liquidity
from src.enums.signal import Emplitude
from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


# Absorption (Gom kín trước khi kéo)
# volume >= 1.5 x MA20
# |Close - Open| / Open < 3%
# Close gần High
# RSI 55-60
# Gia tich luy >= 2 tuan
#
# Entry: Phien xac nhan tang nh hom sau
# Stop: Duoi nen tich luy
# Target: Dinh gan nhat
def liquidity_setup(comp):
    volume = VolumeFilter()

    liquidity = volume.filter_minimum_liquidity(comp.company_data[-1], 50)
    if liquidity == Liquidity.Good:
        return comp.symbol
    return None