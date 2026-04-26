import ta
from vnstock import Quote
from src.models.indicator import MovingAverage, BollingerBands, DonchianChannel, AverageDirectionalIndex, Moving_Average_Convergence_Divergence
from vnstock import Vnstock
import numpy as np
import pandas as pd

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
            print("data frame is not initialized.")
            return
        self.data_frame['trading_value'] = (self.data_frame['close'] * self.data_frame['volume'])/1000000
        return self.data_frame['trading_value']

#Todo: Convert to list
    def Calculate_Moving_Average(self, window):
        if self.data_frame is None:
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
            return

        self.data_frame['vol_ma5'] = self.data_frame['volume'].rolling(5).mean()
        self.data_frame['vol_ma20'] = self.data_frame['volume'].rolling(20).mean()
        self.data_frame['volume_osc'] = ((self.data_frame['vol_ma5'] - self.data_frame['vol_ma20']) / self.data_frame['vol_ma20']) * 100
        # print(self.data_frame)

        volume_oscillator = self.data_frame['volume_osc']
        return volume_oscillator.tolist()

    def Calculate_Accumulation_Distribution(self):
        if self.data_frame is None:
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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
            print("data frame is not initialized.")
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

    def Calculate_Stochastic_oscillator(self, window=14, smooth_window=3):
        """Calculate Stochastic Oscillator indicators"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        # Calculate Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=window,
            smooth_window=smooth_window
        )

        self.data_frame['stoch_k'] = stoch.stoch()
        self.data_frame['stoch_d'] = stoch.stoch_signal()

        return self.data_frame['stoch_k'].tolist(), self.data_frame['stoch_d'].tolist()

    def Calculate_Williams_R(self, window=14):
        """Calculate Williams %R indicator"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        self.data_frame['williams_r'] = ta.momentum.WilliamsRIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=window
        ).williams_r()

        return self.data_frame['williams_r'].tolist()

    def Calculate_Chaikin_Money_Flow(self, window=20):
        """Calculate Chaikin Money Flow indicator"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        self.data_frame['cmf'] = ta.volume.ChaikinMoneyFlowIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            volume=self.data_frame['volume'],
            window=window
        ).chaikin_money_flow()

        return self.data_frame['cmf'].tolist()

    def Calculate_Rate_of_Change(self, window=10):
        """Calculate Rate of Change indicator"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        self.data_frame['roc'] =ta.momentum.ROCIndicator(
            close=self.data_frame['close'],
            window=window
        ).roc()

        return self.data_frame['roc'].tolist()

    def Calculate_Standard_deviation(self, window=20):
        """Calculate Standard Deviation of price"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        self.data_frame['std_dev'] = self.data_frame['close'].rolling(window=window).std()
        return self.data_frame['std_dev'].tolist()

    def Calculate_Commodity_Channel_Index(self, window=20):
        """Calculate Commodity Channel Index"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        self.data_frame['cci'] = ta.trend.CCIIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=window
        ).cci()

        return self.data_frame['cci'].tolist()

    def Calculate_Money_Flow_index(self, window=14):
        """Calculate Money Flow index"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        self.data_frame['mfi'] = ta.volume.MFIIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            volume=self.data_frame['volume'],
            window=window
        ).money_flow_index()

        return self.data_frame['mfi'].tolist()

    def Calculate_Elder_Ray_index(self, window=13):
        """Calculate Elder Ray Index(Bull Power and Bear Power)"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        # Calculate 13-period EMA
        self.data_frame['ema_13'] = self.data_frame['close'].ewm(span=window).mean()

        # Bull Power = High - EMA
        self.data_frame['bull_power'] = self.data_frame['high'] - self.data_frame['ema_13']

        # Bear Power = Low - EMA
        self.data_frame['bear_power'] = self.data_frame['low'] - self.data_frame['ema_13']

        return self.data_frame['bull_power'].tolist(), self.data_frame['bear_power'].tolist()

    def Calculate_Know_Sure_Thing(self, roc1=10, roc2=15, roc3=20, roc4=30,
                                  ma1=10, ma2=10, ma3=10, ma4=15, signal=9):
        """Calculate Know Sure Thing indicator"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        # Calculate ROCs
        roc_ma1 = self.data_frame['close'].diff(roc1).rolling(ma1).mean()
        roc_ma2 = self.data_frame['close'].diff(roc2).rolling(ma2).mean()
        roc_ma3 = self.data_frame['close'].diff(roc3).rolling(ma3).mean()
        roc_ma4 = self.data_frame['close'].diff(roc4).rolling(ma4).mean()

        # Calculate KST
        self.data_frame['kst'] = roc_ma1 + roc_ma2 * 2 + roc_ma3 * 3 + roc_ma4 * 4
        self.data_frame['kst_signal'] = self.data_frame['kst'].rolling(signal).mean()

        return self.data_frame['kst'].tolist(), self.data_frame['kst_signal'].tolist()

    def Calculate_TEMA(self, window=20):
        """Calculate Triple Exponential Moving Average"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        ema1 = self.data_frame['close'].ewm(span=window).mean()
        ema2 = ema1.ewm(span=window).mean()
        ema3 = ema2.ewm(span=window).mean()

        self.data_frame['tema'] = 3 * ema1 - 3 * ema2 + ema3
        return self.data_frame['tema'].tolist()

    def Calculate_Parabolic_SAR(self, acceleration=0.02, maximum=0.2):
        """Calculate Parabolic SAR Indicator"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        # Initialize SAM array
        sar = np.zeros(len(self.data_frame))
        trend = np.ones(len(self.data_frame)) # 1. for uptrend, -1 for downtrned
        ep = np.zeros(len(self.data_frame)) # Extreme point
        af = np.zeros(len(self.data_frame)) # Acceleration factor

        # Initialize first values
        sar[0] = self.data_frame['close'].iloc[0]
        trend[0] = 1
        ep[0] = self.data_frame['high'].iloc[0]
        af[0] = acceleration

        for i in range(1, len(self.data_frame)):
            # Calculate SAR
            sar[i] = sar[i-1] + af[i-1] * (ep[i-1] - sar[i-1])

            # Check trend reversal
            if trend[i-1] == 1: # Uptrend
                # SAR should not exceed previous two lows
                sar[i] = min(sar[i], self.data_frame['low'].iloc[i-1],
                             self.data_frame['low'].illoc[i-2] if i > 1 else sar[i])

                # Check for reversal
                if self.data_frame['low'].iloc[i] < sar[i]:
                    trend[i] = -1
                    sar[i] = ep[i-1]
                    ep[i] = self.data_frame['low'].iloc[i-1]
                    af[i] = acceleration
                else:
                    trend[i] = -1

    def Calculate_Ichimoku_Cloud(self):
        return

    def Calculate_Fibonacci_Retracement(self):
        return

    def Calculate_VWAP(self):
        return

    def Calculate_ADXR(self):
        return

    def Calculate_DPO(self):
        return

    def Calculate_TRIX(self):
        return

    def Calculate_CMO(self):
        return

    def Calculate_Parabolic_SAR(self):
        return


    def Calculate_Ultimate_Oscillator(self, period1=7, period2=14, period3=28):
        """Calculate Ultimate Oscillator indicator"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        # Calculate buying pressure
        bp = self.data_frame['close'] - pd.concat([
            self.data_frame['low'],
            self.data_frame['close'].shift(1)
        ], axis=1).min(axis=1)

        # Calculate true range
        tr = pd.concat([
            self.data_frame['high'] - self.data_frame['low'],
            abs(self.data_frame['high'] - self.data_frame['close'].shift(1)),
            abs(self.data_frame['low'] - self.data_frame['close'].shift(1))
        ], axis=1).max(axis=1)

        # Calculate averages
        avg1 = bp.rolling(window=period1).sum() / tr.rolling(window=period1).sum()
        avg2 = bp.rolling(window=period2).sum() / tr.rolling(window=period2).sum()
        avg3 = bp.rolling(window=period3).sum() / tr.rolling(window=period3).sum()

        # Ultimate Oscillator = 100 * ((4 * avg1) + (2 * avg2) + avg3) / (4 + 2 + 1)
        self.data_frame['ultimate_oscillator'] = 100 * ((4 * avg1) + (2 * avg2) + avg3) / 7
        return self.data_frame['ultimate_oscillator'].tolist()

    def Calculate_PVO(self, short_window=12, long_window=26, signal_window=9):
        """Calculate Percentage Volume Oscillator"""
        if self.data_frame is None:
            print("data frame is not initialized.")
            return

        # Calculate EMAs of volume
        ema_short = self.data_frame['volume'].ewm(span=short_window).mean()
        ema_long = self.data_frame['volume'].ewm(span=long_window).mean()

        # PVO = ((EMA_short - EMA_long) / EMA_long) * 100
        self.data_frame['pvo'] = ((ema_short - ema_long) / ema_long) * 100

        # PVO signal line
        self.data_frame['pvo_signal'] = self.data_frame['pvo'].ewm(span=signal_window).mean()

        # PVO histogram
        self.data_frame['pvo_hist'] = self.data_frame['pvo'] - self.data_frame['pvo_signal']
        return (self.data_frame['pvo'].tolist(), self.data_frame['pvo_signal'].tolist(), self.data_frame['pvo_hist'].tolist())


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

        self.Calculate_Stochastic_oscillator()
        self.Calculate_Williams_R()
        self.Calculate_Chaikin_Money_Flow()
        self.Calculate_Rate_of_Change()
        self.Calculate_Standard_deviation()
        self.Calculate_Commodity_Channel_Index()
        self.Calculate_Money_Flow_index()
        self.Calculate_Elder_Ray_index()
        self.Calculate_Know_Sure_Thing()
        self.Calculate_TEMA()
        self.Calculate_Ultimate_Oscillator()
        self.Calculate_PVO()

        # Not implement
        self.Calculate_Ichimoku_Cloud()
        self.Calculate_Fibonacci_Retracement()
        self.Calculate_VWAP()
        self.Calculate_ADXR()
        self.Calculate_DPO()
        self.Calculate_TRIX()
        self.Calculate_CMO()
        self.Calculate_Parabolic_SAR()