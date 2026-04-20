from src.enums.liquidity import Cash_Flow
from src.enums.signal import Emplitude
from src.filters.short_term.short_term_trend_filter import ShortTermTrendFilter
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.filters.volume.VolumeFilter import VolumeFilter
from src.filters.risk.risk_filter import RiskFilter


# MA50 Support (Medium-term)
# Giá gần MA50 (trong vỏng 3%)
# RSI 45-55 (trung lập)
# ADX > 20 (xu hướng ổn định)
# ATR/Close 2-4% (biên động phù hợp)
#
# Entry: khi giá bật khỏi MA50
# Stop: Duoi Ma50 khoảng 2%
# Target: 3R (10-15%)
def ma50_support_setup(comp):
    shortTerm = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()
    risk = RiskFilter()

    # Price near MA50
    price_near_ma50 = abs(comp.company_data[-1].price.close_price - comp.company_data[-1].moving_average_50.ma_price) / comp.company_data[-1].moving_average_50.ma_price < 0.03
    volume_condition = volume.find_smart_market(comp.company_data[-1]) == Cash_Flow.Smart_Money
    rsi_neutral = 45 <= comp.company_data[-1].RSI_14 <= 55
    adx_stable = comp.company_data[-1].ADX_14.ADX > 20
    atr_condition = volatility.atr_filter(comp.company_data[-1]) in [Emplitude.Good, Emplitude.Weak]

    if price_near_ma50 and volume_condition and rsi_neutral and adx_stable and atr_condition:
        return comp.symbol
    return None