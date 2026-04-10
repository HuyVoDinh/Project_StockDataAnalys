from Enum.liquidity import Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import Company, CompanyData

# Volume Spike co kiem soat
# Volume 1.8 - 2.3 x MA20
# Close tang < 4%
# RSI < 65
# GIa khong xa MA20 > 3%
#
# Entry: cuoi phien neu khong co rau tren dai
# Stop: Duoi day phien spike
# Target: 5-8%
# dong tien dot biet nhung chua FOMO
def volume_spike_setup(comp):
    volume = VolumeFilter()
    shortTerm = ShortTermTrendFilter()
    volatility = VolatilityFilter()

    smart_money = volume.find_smart_market(comp.company_data[-1])
    candles = volatility.daily_candlestick_range(comp.company_data[-1])
    rsi = shortTerm.RSI_momentum_confirmation(comp.company_data[-1])
    ma = shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2])

    if smart_money == Cash_Flow.Smart_Money and candles == Emplitude.Good and ma == Trend.Up and rsi == Trend.Good:
        return comp.symbol
    return None