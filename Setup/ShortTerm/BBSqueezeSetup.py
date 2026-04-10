from Enum.liquidity import Cash_Flow, Volume
from Enum.signal import Signal, Emplitude
from Enum.trend import Trend
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Timing.TimingFilter import TimingFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import Company, CompanyData

# Bollinger squeeze breakout
# BB Width < 4% (siet band)
# Volume bat dau tang
# Close > BB Middle
# RSI > 55
#
# Entry: Khi pha Upper band tang nhe
# Stop: Duoi Middle band
# Target: 2R
# Setup nen - bung
def bb_squeeze_setup(comp):
    volume = VolumeFilter()
    shortTerm = ShortTermTrendFilter()
    volatility = VolatilityFilter()
    timing = TimingFilter()

    bandwidth = volatility.bandwidth_filter(comp.company_data[-1])
    gather = volume.check_gather_goods(comp.company_data[-1], comp.company_data[-2], comp.company_data[-3])
    bb = volatility.bandwidth_filter2(comp.company_data[-1])
    rsi = shortTerm.RSI_momentum_confirmation(comp.company_data[-1])

    if bandwidth == Emplitude.Break and gather == Volume.Money_In and bb == Emplitude.Good and rsi == Trend.Good:
        return comp.symbol
    return None
