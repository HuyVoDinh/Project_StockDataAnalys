import numpy as np
import ta
from vnstock import Listing
from vnstock import Quote, Trading
from Model import Indicator
from Model.Indicator import Price
from vnstock import Vnstock

class StockData:
    def __init__(self, symbol: str, start, end, source="VCI"):
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
        self.stock = Vnstock(symbol=self.symbol, source=self.source)
        print("Stock is initialized")

    def update_data_frame(self, start, end):
        if self.stock is None:
            print("Stock is not initialized.")
            self.init_Stock()
        self.data_frame = self.stock.quote.history(start=start, end=end)

    def listing_information_all_symbols(self):
        return self.listing.all_symbols()

    #Exchange: HOSE, HNX
    def listing_information_by_exchange(self, exchange: str):
        return self.listing.symbols_by_exchange(exchange)

    #VN30, VN100
    def listing_information_by_group(self, group: str):
        return self.listing.symbols_by_group(group)

    def listing_information_by_industries(self):
        return self.listing.symbols_by_industries()

    def listing_information_by_industries_icb(self):
        return self.listing.industries_icb()

    def get_history_price(self, symbol: str, length: str, interval: str):
        return self.quote.history(length=length, interval=interval)

    def get_historical_price(self, symbol: str, start: str, end: str, interval: str):
        return self.quote.history(start=start, end=end, interval=interval)

    def get_trading_price(self, symbols_list :list[str]):

        board = self.trading.price_board(symbols_list= symbols_list)

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
        price = Price(ref_price, high_price, low_price, open_close, close_price)
        return price

    def import_volume_data(self, trading_info):
        volume = trading_info[('match', 'accumulated_volume')]
        return volume

    def example(self):
        self.data_frame['vol_ma10'] = self.data_frame['volume'].rolling(10).mean()
        self.data_frame['vol_ma20'] = self.data_frame['volume'].rolling(20).mean()
        self.data_frame['vol_ma50'] = self.data_frame['volume'].rolling(50).mean()
        self.data_frame['price_ma10'] = self.data_frame['close'].rolling(10).mean()
        self.data_frame['price_ma20'] = self.data_frame['close'].rolling(20).mean()
        self.data_frame['price_ma50'] = self.data_frame['close'].rolling(50).mean()
        print(self.data_frame)


    def On_Balance_Volume(self):
        self.data_frame['obv'] = ta.volume.OnBalanceVolumeIndicator(
            close=self.data_frame['close'],
            volume=self.data_frame['volume']
        ).on_balance_volume()

        print(self.data_frame)


    def Volume_Oscillator(self):
        # Tính MA volume
        self.data_frame['vol_ma5'] = self.data_frame['volume'].rolling(5).mean()
        self.data_frame['vol_ma20'] = self.data_frame['volume'].rolling(20).mean()
        self.data_frame['volume_osc'] = ((self.data_frame['vol_ma5'] - self.data_frame['vol_ma20']) / self.data_frame['vol_ma20']) * 100
        print(self.data_frame)


    def Accumulation_Distribution(self):
        self.data_frame['ad'] = ta.volume.AccDistIndexIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            volume=self.data_frame['volume']
        ).acc_dist_index()

        print(self.data_frame)

    def Average_True_Range(self):
        self.data_frame['atr_14'] = ta.volatility.AverageTrueRange(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=14
        ).average_true_range()

        print(self.data_frame)

    def Average_True_Range_MA5(self):
        self.data_frame['atr_14'] = ta.volatility.AverageTrueRange(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=14
        ).average_true_range()

        self.data_frame['atr_ma5'] = self.data_frame['atr_14'].rolling(5).mean()

        print(self.data_frame)

    def Bollinger_Bands(self):
        bb = ta.volatility.BollingerBands(
            close=self.data_frame['close'],
            window=20,
            window_dev=2
        )

        self.data_frame['bb_middle'] = bb.bollinger_mavg()
        self.data_frame['bb_upper'] = bb.bollinger_hband()
        self.data_frame['bb_lower'] = bb.bollinger_lband()

        print((self.data_frame))

    def Donchian_Channel(self):
        dc = ta.volatility.DonchianChannel(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=20
        )

        self.data_frame['dc_upper'] = dc.donchian_channel_hband()
        self.data_frame['dc_lower'] = dc.donchian_channel_lband()
        self.data_frame['dc_middle'] = dc.donchian_channel_mband()

        print(self.data_frame)

    def Relative_Strength_Index(self):
        self.data_frame['rsi_14'] = ta.momentum.RSIIndicator(
            close=self.data_frame['close'],
            window=14
        ).rsi()

        print(self.data_frame)

    def Average_Directional_Index(self):
        adx = ta.trend.ADXIndicator(
            high=self.data_frame['high'],
            low=self.data_frame['low'],
            close=self.data_frame['close'],
            window=14
        )

        self.data_frame['adx_14'] = adx.adx()
        self.data_frame['plus_di'] = adx.adx_pos()
        self.data_frame['minus_di'] = adx.adx_neg()

        print(self.data_frame)

    def Moving_Average_Convergence_Divergence(self):
        macd = ta.trend.MACD(
            close=self.data_frame['close'],
            window_slow=26,
            window_fast=12,
            window_sign=9
        )

        self.data_frame['macd'] = macd.macd()
        self.data_frame['macd_signal'] = macd.macd_signal()
        self.data_frame['macd_hist'] = macd.macd_diff()

        print(self.data_frame)