from platform import processor


class Company():
    def __init__(self, symbol, company_data ):
        self.symbol = symbol
        self.company_data = company_data

class CompanyData():
    def __init__(self, price, open_price, close_price, volume, time,ma20_volume, OBV, VO, AD):
        self.price = price
        self.open_price = open_price
        self.close_price = close_price
        self.volume = volume
        self.time = time
        self.MA20_Volume = ma20_volume
        self.On_Balance_Volume = OBV
        self.Volume_Oscillator = VO
        self.Accumulation_Distribution = AD
