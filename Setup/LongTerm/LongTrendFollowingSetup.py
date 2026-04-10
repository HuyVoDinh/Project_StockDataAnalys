from Enum.liquidity import Cash_Flow, Volume
from Enum.signal import Emplitude
from Enum.trend import Trend
from Filter.ShortTerm.ShortTermTrendFilter import ShortTermTrendFilter
from Filter.Volatility.VolatilityFilter import VolatilityFilter
from Filter.Volume.VolumeFilter import VolumeFilter
from Model.Company import CompanyData, Company

# Long-term Trend Following (Long-term)
# MA50 > MA1000 > MA200 (nếu có)
# Giá trên MA50 trong 10 phiên liên tiếp
# Volume trung bnh > 50 trieệu
# RSI không quá mua/ban (30-70)
#
# Entry: khi MA20 cắt lên MA50
# Stop: Dưới Ma50 khoảng 5%
# Target: theo xu hướng (20-30%)

def long_trend_following_setup(comp):
    shortTerm = ShortTermTrendFilter()
    volume = VolumeFilter()
    volatility = VolatilityFilter()

    # Long-term uptrend
    long_uptrend = (comp.company_data[-1].moving_average_50.ma_price > comp.company_data[-1].moving_average_20.ma_price)

    # Price above MA50 for 10 sessions
    price_above_ma50 = all(data.price.close_price > data.moving_average_50.ma_price for data in comp.company_data[-10:])

    # Volume condition
    avg_volume = sum(data.volume for data in comp.company_data[-10:]) / 10
    volume_condition = avg_volume > 50000000

    # RSI range
    rsi_range = 30 <= comp.company_data[-1].RSI_14 <= 70

    if long_uptrend and price_above_ma50 and volume_condition and rsi_range:
        return comp.symbol
    return None