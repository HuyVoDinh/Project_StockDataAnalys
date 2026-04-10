from Enum.liquidity import Liquidity, Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import Company

# Absorption (Gom kín trước khi kéo)
# Volume >= 1.5 x MA20
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