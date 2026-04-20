
class BollingerBands:
    def __init__(self):
        self.BB_Upper = None
        self.BB_Lower = None
        self.Middle = None

class DonchianChannel:
    def __init__(self):
        self.Upper_Channel = None
        self.Lower_Channel = None
        self.Middle = None

class Moving_Average_Convergence_Divergence:
    def __init__(self):
        self.MACD = None
        self.signal = None
        self.histogram = None

class MovingAverage:
    def __init__(self):
        self.ma_price = None
        self.ma_volume = None
        self.window = None

class Price:
    def __init__(self):
        self.ref_price = None
        self.high_price = None
        self.low_price = None
        self.open_price = None
        self.close_price = None

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
    def __init__(self):
        self.ADX = None
        self.plus_DI = None
        self.minus_DI = None