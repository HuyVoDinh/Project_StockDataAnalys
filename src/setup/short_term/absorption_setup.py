from src.enums.liquidity import Cash_Flow, Volume
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
def absorption_setup(comp):
    volume = VolumeFilter()
    shortTerm = ShortTermTrendFilter()
    volatility = VolatilityFilter()

    smart_money = volume.find_smart_market(comp.company_data[-1])
    check_volume = volume.check_volume_and_price(comp.company_data[-1], comp.company_data[-2])
    candles = volatility.daily_candlestick_range(comp.company_data[-1])
    rsi = shortTerm.RSI_momentum_confirmation(comp.company_data[-1])

    if smart_money == Cash_Flow.Smart_Money and check_volume == Volume.Money_In and candles == Emplitude.Good and rsi == Trend.Good:
        return comp.symbol
    return None