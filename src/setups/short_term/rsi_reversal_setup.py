from src.enums.liquidity import Cash_Flow
from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


# RSI Reversal (Short-term)
# RSI < 30 (qua ban) hoac RSI > 70 (qua mua)
# Gia cham hoac vuot MA20
# volume tang dot biet
# Stochastic dang phan ky
#
# Entry: Khi RSI quay dau tu vung qua ban
# Stop: Duoi muc thap nhat 5 phien
# Target: khang cu gan nhat
def rsi_reversal_setup(comp):
    shortTerm = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()

    # RSI conditions
    rsi_oversold = comp.company_data[-1].RSI_14 < 30
    rsi_overbought = comp.company_data[-1].RSI_14 > 70
    ma_retest = shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2]) in [Trend.Up, Trend.Good]
    volume_spike = volume.find_smart_market(comp.company_data[-1]) == Cash_Flow.Smart_Money

    if (rsi_oversold or rsi_overbought) and volume_spike and ma_retest:
        return comp.symbol
    return None