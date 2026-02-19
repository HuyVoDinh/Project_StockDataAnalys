
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
    def __init__(self, price, volume, window):
        self.ma_price = price
        self.ma_volume = volume
        self.window = window

class Price:
    def __init__(self, ref_price, high_price, low_price, open_price, close_price):
        self.ref_price = ref_price
        self.high_price = high_price
        self.low_price = low_price
        self.open_price = open_price
        self.close_price = close_price

    def __str__(self):
        return (f"Ref: {self.ref_price}",
                f"High price: {self.high_price}",
                f"Low price: {self.low_price}",
                f"Open: {self.open_price}",
                f"Close: {self.close_price}"
                )
    def __repr__(self):
        return (f"Ref: {self.ref_price}",
                f"High price: {self.high_price}",
                f"Low price: {self.low_price}",
                f"Open: {self.open_price}",
                f"Close: {self.close_price}"
                )

class AverageDirectionalIndex:
    def __init__(self, ADX, plus_DI, minus_DI):
        self.ADX = ADX
        self.plus_DI = plus_DI
        self.minus_DI = minus_DI