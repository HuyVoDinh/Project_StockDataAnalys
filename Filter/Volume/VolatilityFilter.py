# T+ needs to have AMPLIFIER but NOT TOO AGGRESSIVE
#
# Low volatility → no profit
#
# Too high volatility → sell-off / bull trap
#
# Moderate volatility → easy to pull in – easy to exit

class VolatilityFilter:
    def __init__(self):
        pass

    #Filter 1 -
    def daily_candlestick_range(self, company_data):
        # 2 % – 5 %
        # < 1.5% → Money not yet wagered
        # 6–7% → Too hot
        range = (company_data.price.high_price - company_data.price.low_price) / company_data.price.close_price
        if(range < 0.015):
            return -1
        elif(range > 0.5):
            return 0
        else:
            return 1

    #Filter 2
    #Candlestick body fluctuations
    def candlestick_range(self, company_data):
        # 1 % – 3 % Moderate candle body → money is controlling the price
        range = abs(company_data.price.close_price - company_data.price.open_price) / company_data.price.open_price
        if (range > 0.01 and range < 0.03):
            return 1
        return -1

    # ATR(14)
    # Used to find out if this stock has enough "vibration" to trade T+

    #Filter 3
    # ATR(14) / Close = 1.5% – 4%
    # < 1% → ì
    # 5% → easy to jerk violently, difficult to hold
    def atr_filter(self, company_data):
        if company_data.atr14 / company_data.price.close_price < 0.01:
            return -1
        elif company_data.atr14 / company_data.price.close_price > 0.05:
            return 0

        #ATR slightly increased(good setup) Today's ATR > ATR MA5 → Volatility is opening up
        if company_data.atr14 > company_data.atr_ma5:
            return 2
        return 1

    #Bollinger Bands – used to AVOID entering the wrong lane.
    def bandwidth_filter(self, company_data):
        # Bandwidth: 4 % – 10 %
        # < 3 % → squeezes, wait for a breakout
        # 12 % → already running, don't chase it

        range = (company_data.Bollinger_Bands.BB_Upper - company_data.Bollinger_Bands.BB_Lower) / company_data.Bollinger_Bands.Middle
        if(range < 0.03):
            return -1
        elif(range >= 0.12):
            return 0
        return 1

    def bandwidth_filter2(self, company_data):
        # Price moves from Middle → Upper band -> Strong T + (trading)
        # Price touches Upper band + sudden surge in volume → sell
        if company_data.Bollinger_Bands.Middle < company_data.price.close_price and company_data.Bollinger_Bands.BB_Upper > company_data.price.close_price:
            return 1
        elif company_data.Bollinger_Bands.BB_Upper < company_data.price.close_price:
            return -1
        return 0

    #Filter - detect
    def donchian_channel_filter(self, company_data):
        # Close < Upper Channel
        # Not a strong breakout yet, still room for T +
        if company_data.price.close_price < company_data.Donchian_Channel.Upper_Channel:
            return 1
        return -1
