from Enum.liquidity import Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import Company, CompanyData

# Retest MA20 an toan
# Volume 1.4 - 1.8 x MA20
# Close > MA20
# MA20 doc len
# RSI 55-62
# ATR/Close 2-3%
#
# Entry: khi gia retest MA20 va bat
# Stop: Duoi swing low hoac Ma20 - 1%
# Target: 2R (5-7%)
def ma20_retest_setup(comp):
    volume = VolumeFilter()
    short_term = ShortTermTrendFilter()
    volatility = VolatilityFilter()

    smart_money = volume.find_smart_market(comp.company_data[-1])
    ma = short_term.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    rsi = short_term.RSI_momentum_confirmation(comp.company_data[-1])
    atr = volatility.atr_filter(comp.company_data[-1])
    if smart_money == Cash_Flow.Smart_Money and ma == Trend.Up and rsi == Trend.Good and atr == Trend.Good:
        return comp.symbol
    return None