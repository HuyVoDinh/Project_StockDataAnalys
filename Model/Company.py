from platform import processor
import Indicator


class Company():
    def __init__(self, symbol, company_data ):
        self.symbol = symbol
        self.company_data = company_data

class CompanyData():
    def __init__(self, price, volume, time, moving_average, OBV, VO, AD, atr14, atr_ma5, bollinger_band,donchian_channel, rsi14, adx14, macd):
        self.price = price
        self.volume = volume
        self.time = time
        self.moving_average = moving_average
        self.On_Balance_Volume = OBV
        self.Volume_Oscillator = VO
        self.Accumulation_Distribution = AD
        self.ATR_14 = atr14
        self.ATR_MA5 = atr_ma5
        self.Bollinger_Bands = bollinger_band
        self.Donchian_Channel = donchian_channel
        self.RSI_14 = rsi14
        self.ADX_14 = adx14
        self.MACD = macd
