
class BollingerBands:
    def __init__(self,BB_Upper, BB_Lower, Middle):
        self.BB_Upper = BB_Upper
        self.BB_Lower = BB_Lower
        self.Middle = Middle

class DonchianChannel:
    def __init__(self,Upper_Channel, Lower_Channel, Middle):
        self.Upper_Channel = Upper_Channel
        self.Lower_Channel = Lower_Channel
        self.Middle = Middle

class MACD:
    def __init__(self,MACD, signal, histogram = 0):
        self.MACD = MACD
        self.signal = signal
        self.histogram = histogram

class MovingAverage:
    def __init__(self, ma10_price, ma10_volume, ma20_price, ma20_volume, ma50_price, ma50_volume):
        self.ma10_price = ma10_price
        self.ma10_volume = ma10_volume
        self.ma20_price = ma20_price
        self.ma20_volume = ma20_volume
        self.ma50_price = ma50_price
        self.ma50_volume = ma50_volume

class Price:
    def __init__(self, high_price, low_price, open_price, close_price):
        self.high_price = high_price
        self.low_price = low_price
        self.open_price = open_price
        self.close_price = close_price
