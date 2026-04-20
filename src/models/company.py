from ast import List
from src.models.indicator import Price, MovingAverage, BollingerBands, DonchianChannel, AverageDirectionalIndex, Moving_Average_Convergence_Divergence



class Company():
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.company_data: List[CompanyData] = []

class CompanyData():
    def __init__(self):
        self.price = Price()
        self.volume = None
        self.time = None
        self.trading_value = None
        self.moving_average_10 = MovingAverage()
        self.moving_average_20 = MovingAverage()
        self.moving_average_50 = MovingAverage()
        self.On_Balance_Volume = None
        self.Volume_Oscillator = None
        self.Accumulation_Distribution = None
        self.ATR_14 = None
        self.ATR_MA5 = None
        self.Bollinger_Bands = BollingerBands()
        self.Donchian_Channel = DonchianChannel()
        self.RSI_14 = None
        self.ADX_14 = AverageDirectionalIndex()
        self.MACD = Moving_Average_Convergence_Divergence()
        self.StdDev_20 = None

    def import_data(self, dataFrame):
        self.price.open_price = dataFrame['open']
        self.price.high_price = dataFrame['high']
        self.price.low_price = dataFrame['low']
        self.price.close_price = dataFrame['close']
        self.volume = dataFrame['volume']
        self.time = dataFrame['time']
