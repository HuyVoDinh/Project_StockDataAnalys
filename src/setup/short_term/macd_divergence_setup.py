from src.enums.liquidity import Volume
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


# MACD Divergence Reversal (Short-term)
# MACD phan ky voi gia
# volume giam tai day
# RSI < 30 (qua ban)
# ADX > 25 (xac nhan xu huong manh)
#
# Entry: khi MACD cat len signal line
# Stop: Duoi swing low gan nhat
# Target: 2R (5-10%)
def macd_divergence_setup(comp):
    short_term = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()

    # Check for MACD bullish divergence
    macd_bullish = comp.company_data[-1].MACD.MACD > comp.company_data[-1].MACD.signal and comp.company_data[-2].MACD.MACD < comp.company_data[-2].MACD.signal
    rsi_oversold = comp.company_data[-1].RSI_14 < 30
    volume_descreasing = volume.check_supply_test(comp.company_data[-1], comp.company_data[-2]) == Volume.Money_In
    adx_strong = comp.company_data[-1].ADX_14.ADX > 25

    if macd_bullish and rsi_oversold and volume_descreasing and adx_strong:
        return comp.symbol
    return None