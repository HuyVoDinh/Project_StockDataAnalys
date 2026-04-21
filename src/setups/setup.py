from src.enums.liquidity import Cash_Flow, Volume
from src.enums.signal import Emplitude
from src.enums.trend import Trend
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.timing.timing_filter import TimingFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter


#Retest MA20 an toàn
# volume 1.4 – 1.8 × MA20
# Close > MA20
# MA20 dốc lên
# RSI 55–62
# ATR/Close 2–3%
#
# Entry: khi giá retest MA20 và bật
# Stop: dưới swing low hoặc MA20 –1%
# Target: 2R (~5–7%)
def setup_1(comp):
    volume = VolumeFilter()
    shortTerm = ShortTermTrendFilter()
    volatility = VolatilityFilter()

    smart_money = volume.find_smart_market(comp.company_data[-1])
    ma = shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2])
    rsi = shortTerm.RSI_momentum_confirmation(comp.company_data[-1])
    atr = volatility.atr_filter(comp.company_data[-1])
    if smart_money == Cash_Flow.Smart_Money and ma == Trend.Up and rsi == Trend.Good and atr == Emplitude.Good:
        return comp.symbol
    return None

#Absorption (gom kín trước khi kéo)
# volume ≥ 1.5 × MA20
# |Close – Open| / Open < 3%
# Close gần High
# RSI 55–60
# Giá tích lũy ≥ 2 tuần
#
# Entry: phiên xác nhận tăng nhẹ hôm sau
# Stop: dưới nền tích lũy
# Target: đỉnh gần nhất
#
# 👉 Bắt trước breakout.
def setup_2(comp):
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

#Bollinger squeeze breakout
# BB Width < 4% (siết band)
# volume bắt đầu tăng
# Close > BB Middle
# RSI > 55
#
# Entry: khi phá Upper Band nhẹ
# Stop: dưới Middle Band
# Target: 2R
#
# 👉 setups nén – bung.
def setup_3(comp):
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


# volume Spike có kiểm soát
# volume 1.8 – 2.3 × MA20
# Close tăng < 4%
# RSI < 65
# Giá không xa MA20 > 3%
#
# Entry: cuối phiên nếu không có râu trên dài
# Stop: dưới đáy phiên spike
# Target: 5–8%
#
# 👉 Dòng tiền đột biến nhưng chưa FOMO.
def setup_4(comp):
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
