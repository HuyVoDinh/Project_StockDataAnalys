from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


# Multi-timeframe Trend Confirmation (Medium-trend)
# MA10 > MA20 > MA50 (thong nhat xu huong tang)
# volume tang deu trong 3 phien
# RSI 50-65 (dong luong tot)
# ATR on dinh
#
# Entry: khi xac nhan xu huong tang da khung thoi gian
# Stop: Duoi MA50 khoang 3%
# Target: 3R (15-20%)
def multi_timeframe_trend_setup(comp):
    shortTerm = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()

    # Multi MA alignment
    uptrend_alignment = (comp.company_data[-1].moving_average_10.ma_price > comp.company_data[-1].moving_average_20.ma_price > comp.company_data[-1].moving_average_50.ma_price)

    # volume trend
    volume_trend = (comp.company_data[-1].volume > comp.company_data[-2].volume > comp.company_data[-3].volume)

    # RSI momentum
    rsi_momentum = 50 <= comp.company_data[-1].RSI_14 <= 65

    # Stable trend
    stable_trend = shortTerm.check_trend_or_sideways(comp.company_data[-1]) == Trend.Good

    if uptrend_alignment and volume_trend and rsi_momentum and stable_trend:
        return comp.symbol
    return None