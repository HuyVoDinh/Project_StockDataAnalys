import ta
from vnstock import Quote
from src.models.indicator import MovingAverage, BollingerBands, DonchianChannel, AverageDirectionalIndex, Moving_Average_Convergence_Divergence
from vnstock import Vnstock

class StockAnalyzer:
    def __init__(self, symbol: str, source="KBS"):
        self.symbol = symbol
        self.source = source
        self.quote = None
        self.stock = None
        self.data_frame = None

    def init_Quote(self):
        print("Initializing Quote")
        self.quote = Quote(self.symbol, source=self.source)
        print("Quote Initialized")

    def init_Stock(self):
        print("Initializing stock...")
        self.stock = Vnstock().stock(symbol=self.symbol, source=self.source)
        print("Stock is initialized")

#          time   open   high    low  close    volume  trading_value
# 0  2025-11-25  15.80  15.90  15.20  15.30  11227900    171786870.0
    def update_data_frame(self, start, end):
        if self.stock is None:
            print("Stock is not initialized.")
            self.init_Stock()
        try:
            self.data_frame = self.stock.quote.history(start=start, end=end)
        except:
            self.data_frame = None


    def get_history_price(self, symbol: str, length: str, interval: str):
        if self.quote is None:
            print("Quote is not initialized.")
            self.init_Quote()
        return self.quote.history(length=length, interval=interval)

    def get_historical_price(self, symbol: str, start: str, end: str, interval: str):
        if self.quote is None:
            print("Quote is not initialized.")
            self.init_Quote()
        return self.quote.history(start=start, end=end, interval=interval)

    def Calculate_Trading_Value(self):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return
        self.data_frame['trading_value'] = (self.data_frame['close'] * self.data_frame['volume'])/1000000
        return self.data_frame['trading_value']

#Todo: Convert to list
    def Calculate_Moving_Average(self, window):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['vol_ma' + str(window)] = self.data_frame['volume'].rolling(window).mean()
        self.data_frame['price_ma'+ str(window)] = self.data_frame['close'].rolling(window).mean()
        # print(self.data_frame)
        ma = MovingAverage()
        ma.ma_price = self.data_frame['price_ma' + str(window)]
        ma.ma_volume = self.data_frame['vol_ma'+ str(window)]
        ma.window = window
        return ma

    def Calculate_On_Balance_Volume(self):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['obv'] = ta.volume.OnBalanceVolumeIndicator(
            close=self.data_frame['close'],
            volume=self.data_frame['volume']
        ).on_balance_volume()

        # print(self.data_frame)

        obv_list = self.data_frame['obv']
        return obv_list.tolist()

    def Calculate_Volume_Oscillator(self):
        # Tính MA volume
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['vol_ma5'] = self.data_frame['volume'].rolling(5).mean()
        self.data_frame['vol_ma20'] = self.data_frame['volume'].rolling(20).mean()
        self.data_frame['volume_osc'] = ((self.data_frame['vol_ma5'] - self.data_frame['vol_ma20']) / self.data_frame['vol_ma20']) * 100
        # print(self.data_frame)

        volume_oscillator = self.data_frame['volume_osc']
        return volume_oscillator.tolist()

    def Calculate_Accumulation_Distribution(self):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['ad'] = ta.volume.AccDistIndexIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            volume=self.data_frame['volume']
        ).acc_dist_index()

        # print(self.data_frame)
        accumulation_distribution = self.data_frame['ad']
        return accumulation_distribution.tolist()

    def Calculate_Average_True_Range(self, window = 14):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['atr_'+ str(window)] = ta.volatility.AverageTrueRange(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=window
        ).average_true_range()

        # print(self.data_frame)
        averate_true_range_list = self.data_frame['atr_'+str(window)].tolist()
        return averate_true_range_list

    def Calculate_Average_True_Range_MA5(self, window=14):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['atr_14'] = ta.volatility.AverageTrueRange(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=window
        ).average_true_range()

        self.data_frame['atr_ma5'] = self.data_frame['atr_14'].rolling(5).mean()
        # print(self.data_frame)

        average_true_range_ma5 = self.data_frame['atr_ma5']
        return average_true_range_ma5.tolist()

#Todo: Convert to list
    def Calculate_Bollinger_Bands(self, window=20, window_dev=2):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        bb = ta.volatility.BollingerBands(
            close=self.data_frame['close'],
            window=window,
            window_dev=window_dev
        )

        self.data_frame['bb_middle'] = bb.bollinger_mavg()
        self.data_frame['bb_upper'] = bb.bollinger_hband()
        self.data_frame['bb_lower'] = bb.bollinger_lband()

        # print((self.data_frame))
        bb = BollingerBands()
        bb.Middle = self.data_frame['bb_middle']
        bb.BB_Upper = self.data_frame['bb_upper']
        bb.BB_Lower = self.data_frame['bb_lower']
        return bb

    def Calculate_Donchian_Channel(self, window=20):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        dc = ta.volatility.DonchianChannel(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=window
        )

        self.data_frame['dc_upper'] = dc.donchian_channel_hband()
        self.data_frame['dc_lower'] = dc.donchian_channel_lband()
        self.data_frame['dc_middle'] = dc.donchian_channel_mband()

        # print(self.data_frame)
        dc = DonchianChannel()
        dc.Middle = self.data_frame['dc_middle']
        dc.Lower_Channel = self.data_frame['dc_lower']
        dc.Upper_Channel = self.data_frame['dc_upper']
        return dc

    def Calculate_Relative_Strength_Index(self, window=14):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['rsi_14'] = ta.momentum.RSIIndicator(
            close=self.data_frame['close'],
            window=window
        ).rsi()

        # print(self.data_frame)
        relative_strength_index = self.data_frame['rsi_14']
        return relative_strength_index.tolist()

    def Calculate_Average_Directional_Index(self, window=14):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        adx = ta.trend.ADXIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=window
        )

        self.data_frame['adx_' + str(window)] = adx.adx()
        self.data_frame['plus_di'] = adx.adx_pos()
        self.data_frame['minus_di'] = adx.adx_neg()

        # print(self.data_frame)
        adx = AverageDirectionalIndex()
        adx.ADX =  self.data_frame['adx_' + str(window)]
        adx.plus_DI = self.data_frame['plus_di']
        adx.minus_DI = self.data_frame['minus_di']
        return adx

    def Calculate_Moving_Average_Convergence_Divergence(self, window_slow=26, window_fast=12, window_sign=9):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        macd = ta.trend.MACD(
            close=self.data_frame['close'],
            window_slow=window_slow,
            window_fast=window_fast,
            window_sign=window_sign
        )

        self.data_frame['macd'] = macd.macd()
        self.data_frame['macd_signal'] = macd.macd_signal()
        self.data_frame['macd_hist'] = macd.macd_diff()

        macd = Moving_Average_Convergence_Divergence()
        macd.MACD = self.data_frame['macd']
        macd.signal = self.data_frame['macd_signal']
        macd.histogram = self.data_frame['macd_hist']
        # print(self.data_frame)
        return macd

    def update_full_indicator(self):
        self.Calculate_Trading_Value()
        self.Calculate_Moving_Average(window = 10)
        self.Calculate_Moving_Average(window = 20)
        self.Calculate_Moving_Average(window = 50)
        self.Calculate_On_Balance_Volume()
        self.Calculate_Volume_Oscillator()
        self.Calculate_Accumulation_Distribution()
        self.Calculate_Average_True_Range()
        self.Calculate_Average_True_Range_MA5()
        self.Calculate_Bollinger_Bands()
        self.Calculate_Donchian_Channel()
        self.Calculate_Relative_Strength_Index()
        self.Calculate_Average_Directional_Index()
        self.Calculate_Moving_Average_Convergence_Divergence()
