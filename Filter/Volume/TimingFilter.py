from Model import Company
from Model import Indicator
# T+ Timing Principle (Remember this)
#
# Don't chase the price
#
# Don't buy long green candles
#
# Buy when risk < reward
#
# Good timing =
#
# price just confirmed + hasn't moved yet

# Giá điều chỉnh về MA20
# Không thủng MA20
# Volume giảm
# Timing:
#
# Mua khi nến hồi kết thúc
#
# Ưu tiên nến rút chân / doji
def setup_retest(company_data_current, company_data_previous):
    if(company_data_current.price > company_data_current.moving_average.ma20_price and company_data_current.volume < company_data_previous.volume):
        return 1
    return 0
#RSI từ 60 → 55 → quay đầu tăng
#nhịp hồi kỹ thuật, rất hợp T+2
def getting_back_on_track_for_recovery(company_data_current, company_data_previous):
    if (company_data_current.RSI_14 < 60 and company_data_current.RSI_14 > 55):
        if(company_data_current.RSI_14 > company_data_previous.RSI_14):
            return 1
    return 0

# Correction session: Volume decreases
# Entry session: Volume increases slightly
#
#If entry volume > 2× MA20 → buy at the peak
def confirm_entry_point(company_data_current, company_data_previous):
    if(company_data_current.volume > company_data_previous.volume and company_data_current.volume < 2 * company_data_current.moving_average.ma20_volume):
        return 1
    return 0
# Giá chạm BB Middle
# Không thủng
# Bật lên
# → xác suất T+ cao
def setup_middle_bands(company_data_current, company_data_previous):
    if(company_data_previous.Bollinger_Bands.Middle > company_data_previous.price and company_data_current.Bollinger_Bands.Middle < company_data_current.price):
        return 1
    return 0

# MACD > 0
# MACD cắt lên Signal
# Histogram chuyển âm → dương
# 👉 Tốt nhất khi giá vừa retest MA20
def setup_MACD(company_data_current):
    if(company_data_current.MACD.MACD > 0 and company_data_current.MACD.MACD > company_data_current.MACD.signal):
        return 1
    return 0