from Enum.liquidity import Cash_Flow
from Enum.signal import Emplitude
from Enum.trend import Trend
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import Company, CompanyData

# Fundamental + Technical Setup (Long-term)
# P/E < ngành trung bình
# ROE > 15%
# Giá trên MA50
# Volume ổn định
# RSI 40-60
#
# Entry: Khi có tín hiểu kỹ thuật tích cực
# Stop dưới MA50 khoảng 7%
# Target: theo xu hướng dài hạn (30-50%)

def fundamental_technical_setup(comp):
    shortTerm = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()

    #Technical condition
    price_above_ma50 = comp.company_data[-1].price.close_price > comp.company_data[-1].price_above_ma50.ma_price
    volume_stable = volume.find_smart_market(comp.company_data[-1]) in [Cash_Flow.Smart_Money, Cash_Flow.Weak]
    rsi_neutral = 40 <= comp.company_data[-1].RSI_14 <= 60
    uptrend = shortTerm.moving_average_filter(comp.company_data[-1], comp.company_data[-2]) in [Trend.Up, Trend.Down]

    #Note: Fundamental data would need to be added to the CompanyData model
    # For now, we'll focus on the technical conditions that can be evaluated

    if price_above_ma50 and volume_stable and rsi_neutral and uptrend:
        return comp.symbol
    return None