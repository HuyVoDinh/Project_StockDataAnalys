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
from Enum.trend import Trend, MarketState, Momentum

class ShortTermTrendFilter:
    def __init__(self):
        pass
    # Filter for a beautiful T+ trend
    # Close > MA20
    # MA20 sloping upwards
    # MA10 ≥ MA20
    def  moving_average_filter(self, company_data_current, company_data_previous):
        if (company_data_current.price.close_price > company_data_current.moving_average_20.ma_price and
            company_data_previous.moving_average_20.ma_price < company_data_current.moving_average_20.ma_price and
            company_data_current.moving_average_10.ma_price >= company_data_previous.moving_average_20.ma_price
        ):
            return Trend.Up
        return Trend.Down

    # RSI 55 – 65
    # < 50 → weak trend
    #
    # 70 → too hot, easy to sell off T+
    #
    # 📌 Best point: RSI 58–62
    # Fitler - Signal
    def RSI_momentum_confirmation(self, company_data):
        if company_data.RSI_14 < 50:
            return Trend.Weak
        elif company_data.RSI_14 > 70:
            return Trend.Fomo
        else: return Trend.Good

    def check_incoming_momentum(self, company_data_current, company_data_previous):
        if(company_data_current.RSI_14 < 65 and company_data_current.RSI_14 < company_data_previous.RSI_14):
            return Momentum.In
        return Momentum.Out

    #ADX – Distinguishing between a true trend and a sideways trend
    def check_trend_or_sideways(self, company_data):
        if company_data.ADX_14.ADX < 20:
            return Trend.Sideway
        elif company_data.ADX_14.ADX > 40:
            return Trend.Fomo
        else: return Trend.Good

    def price_action_confirms_trend(self, company_data_current, company_data_previous):
        if (company_data_current.price.high_price >= company_data_previous.price.high_price and company_data_current.price.low_price >= company_data_previous.price.low_price):
            return Trend.Up
        return Trend.Down

    def check_stable_uptrend(self, company_data):
        if(company_data.moving_average_10.ma_price > company_data.moving_average_20.ma_price and company_data.moving_average_20.ma_price > company_data.moving_average_50.ma_price):
            return Trend.Up
        return Trend.Down
    # Price is far from MA20 > 7%
    # RSI > 70
    # ADX > 40
    # → Do not trade short-term (T+)
    #Filter - warning
    def check_end_trend(self, company_data):
        if company_data.moving_average_20.ma_price == 0:
            return None
        if(company_data.price.close_price / company_data.moving_average_20.ma_price > 0.07 and
        company_data.RSI_14 > 70 and company_data.ADX_14.ADX < 40):
            return MarketState.LATE_TREND
        return MarketState.EARLY_TREND