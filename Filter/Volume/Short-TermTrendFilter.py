from Model import Company
# Trend is for 5-20 sessions, not medium-term.
#
# Requirements:
#
# Price is being supported
#
# Does not go against the major trend
#
# Has room for a 3-8% increase

# Filter for a beautiful T+ trend
# Close > MA20
# MA20 sloping upwards
# MA10 ≥ MA20
def moving_average_filter(company_data_current, company_data_previous):
    if (company_data_current.price.close_price > company_data_current.MA20_price and
        company_data_previous.moving_average.ma20_price < company_data_current.moving_average.ma20_price and
        company_data_current.moving_average.ma10_price >= company_data_previous.moving_average.ma20_price
    ):
        return 1
    return 0

# RSI 55 – 65
# < 50 → weak trend
#
# 70 → too hot, easy to sell off T+
#
# 📌 Best point: RSI 58–62
# Fitler - Signal
def RSI_momentum_confirmation(company_data):
    if company_data.RSI_14 < 50:
        return -1
    elif company_data.RSI_14 > 70:
        return 0
    else: return 1

def check_incoming_momentum(company_data_current, company_data_previous):
    if(company_data_current.RSI_14 < 65 and company_data_current.RSI_14 < company_data_previous.RSI_14):
        return 1
    return 0

#ADX – Distinguishing between a true trend and a sideways trend
def check_trend_or_sideways(company_data):
    if(company_data.ADX_14 > 20 and company_data.ADX_14 < 35):
        return 1
    return 0

def price_action_confirms_trend(company_data_current, company_data_previous):
    if (company_data_current.price.high_price >= company_data_previous.price.high_price and company_data_current.price.low_price >= company_data_previous.price.low_price):
        return 1
    return 0

def check_stable_uptrend(company_data):
    if(company_data.MA10_price > company_data.moving_average.ma20_price and company_data.moving_average.ma20_price > company_data.moving_average.ma50_price):
        return 1
    return 0
# Price is far from MA20 > 7%
# RSI > 70
# ADX > 40
# → Do not trade short-term (T+)
#Filter - warning
def check_end_trend(company_data):
    if(company_data.price.close_price / company_data.moving_average.ma20_price > 0.07 and
    company_data.RSI_14 > 70 and company_data.ADX < 40):
        return -1
    return 1


