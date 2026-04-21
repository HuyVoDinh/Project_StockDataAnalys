from src.enums.liquidity import Volume
from src.enums.signal import Emplitude
from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.timing.timing_filter import TimingFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


# Bollinger squeeze breakout
# BB Width < 4% (siet band)
# volume bat dau tang
# Close > BB Middle
# RSI > 55
#
# Entry: Khi pha Upper band tang nhe
# Stop: Duoi Middle band
# Target: 2R
# setups nen - bung
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
