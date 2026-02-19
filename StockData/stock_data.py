import numpy as np
import ta
from vnstock import Listing
from vnstock import Quote, Trading
from Model import Indicator
from Model.Indicator import Price, MovingAverage, BollingerBands, DonchianChannel, AverageDirectionalIndex, MACD
from vnstock import Vnstock

class StockData:
    def __init__(self, symbol: str, source="VCI"):
        self.symbol = symbol
        self.source = source
        self.quote = None
        self.listing = None
        self.trading = None
        self.stock = None
        self.data_frame = None

    def init_listing(self):
        print("Initializing Listing")
        self.listing = Listing(source=self.source)
        print("Listing Initialized")

    def init_Quote(self):
        print("Initializing Quote")
        self.quote = Quote(self.symbol, source=self.source)
        print("Quote Initialized")

    def init_Trading(self):
        print("Initializing Trading")
        self.trading = Trading(source=self.source, symbol=self.symbol)
        print("Trading initialized")

    def init_Stock(self):
        print("Initializing stock...")
        self.stock = Vnstock().stock(symbol=self.symbol, source=self.source)
        print("Stock is initialized")

    def update_data_frame(self, start, end):
        if self.stock is None:
            print("Stock is not initialized.")
            self.init_Stock()
        self.data_frame = self.stock.quote.history(start=start, end=end)

    def listing_information_all_symbols(self):
        if self.listing is None:
            print("Listing is not initialized.")
            self.init_listing()
        return self.listing.all_symbols()

    #Exchange: HOSE, HNX
    def listing_information_by_exchange(self, exchange: str):
        if self.listing is None:
            print("Listing is not initialized.")
            self.init_listing()
        return self.listing.symbols_by_exchange(exchange)

    #VN30, VN100
    def listing_information_by_group(self, group: str):
        if self.listing is None:
            print("Listing is not initialized.")
            self.init_listing()
        return self.listing.symbols_by_group(group)

    def listing_information_by_industries(self):
        if self.listing is None:
            print("Listing is not initialized.")
            self.init_listing()
        return self.listing.symbols_by_industries()

    def listing_information_by_industries_icb(self):
        if self.listing is None:
            print("Listing is not initialized.")
            self.init_listing()
        return self.listing.industries_icb()

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

    def get_trading_price(self):
        if self.trading is None:
            print("Trading is not initialized.")
            self.init_Trading()

        board = self.trading.price_board(symbols_list=[self.symbol])

        trading_info = board[[('listing', 'symbol'),
                              ('listing', 'ref_price'),
                              ('listing', 'ceiling'),
                              ('listing', 'floor'),
                              ('match', 'match_price'),
                              ('match', 'open_price'),
                              ('match', 'highest'),
                              ('match', 'lowest'),
                              ('match', 'accumulated_volume'),
                              ]]
        symbols = trading_info[('listing', 'symbol')]
        for symbol in symbols:
            print(symbol)
        return trading_info

    def import_price_data(self, trading_info):
        ref_price = trading_info[('listing', 'ref_price')]
        high_price = trading_info[('match', 'highest')]
        low_price = trading_info[('match', 'lowest')]
        open_close = trading_info[('match', 'open_price')]
        close_price = trading_info[('match', 'match_price')]
        price = Price(ref_price/1000, high_price/1000, low_price/1000, open_close/1000, close_price/1000)
        return price

    def import_volume_data(self, trading_info):
        volume = trading_info[('match', 'accumulated_volume')]
        return volume

#Todo: Convert to list
    def Calculate_Moving_Average(self, window):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['vol_ma' + str(window)] = self.data_frame['volume'].rolling(window).mean()
        self.data_frame['price_ma'+ str(window)] = self.data_frame['close'].rolling(window).mean()
        print(self.data_frame)
        return MovingAverage(price=self.data_frame['price_ma' + str(window)],volume=self.data_frame['vol_ma'+ str(window)], window=window)

    def Calculate_On_Balance_Volume(self):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['obv'] = ta.volume.OnBalanceVolumeIndicator(
            close=self.data_frame['close'],
            volume=self.data_frame['volume']
        ).on_balance_volume()

        print(self.data_frame)

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
        print(self.data_frame)

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

        print(self.data_frame)
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

        print(self.data_frame)
        averate_true_range_list = self.data_frame['atr_'+str(window)].tolist()
        return averate_true_range_list.tolist()

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
        print(self.data_frame)

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

        print((self.data_frame))
        return BollingerBands(self.data_frame['bb_upper'],self.data_frame['bb_lower'], self.data_frame['bb_middle'])

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

        print(self.data_frame)
        return DonchianChannel(self.data_frame['dc_upper'], self.data_frame['dc_lower'], self.data_frame['dc_middle'])

    def Calculate_Relative_Strength_Index(self, window=14):
        if self.data_frame is None:
            print("data fram is not initialized.")
            return

        self.data_frame['rsi_14'] = ta.momentum.RSIIndicator(
            close=self.data_frame['close'],
            window=window
        ).rsi()

        print(self.data_frame)
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

        print(self.data_frame)
        return AverageDirectionalIndex(ADX=self.data_frame['adx_'+str(window)], plus_DI=self.data_frame['plus_di'], minus_DI=self.data_frame['minus_di'])

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

        print(self.data_frame)
        return MACD(self.data_frame['macd'], self.data_frame['macd_signal'], self.data_frame['macd_hist'])