from platform import processor
import Indicator


class Company():
    def __init__(self, symbol, company_data ):
        self.symbol = symbol
        self.company_data = company_data

class CompanyData():
    def __init__(self, price, high_price, low_price, open_price, close_price, volume, time, ma10_price, ma20_price,ma20_volume, ma50_price, OBV, VO, AD, atr14, atr_ma5, bollinger_band,donchian_channel, rsi14, adx14):
        self.price = price
        self.high_price = high_price
        self.low_price = low_price
        self.open_price = open_price
        self.close_price = close_price
        self.volume = volume
        self.time = time
        self.MA10_price = ma10_price
        self.MA20_price = ma20_price
        self.MA20_Volume = ma20_volume
        self.MA50_price = ma50_price
        self.On_Balance_Volume = OBV
        self.Volume_Oscillator = VO
        self.Accumulation_Distribution = AD
        self.ATR_14 = atr14
        self.ATR_MA5 = atr_ma5
        self.Bollinger_Bands = bollinger_band
        self.Donchian_Channel = donchian_channel
        self.RSI_14 = rsi14
        self.ADX_14 = adx14
