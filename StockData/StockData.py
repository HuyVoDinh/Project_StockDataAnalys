import numpy as np
import ta
from vnstock import Listing
from vnstock import Quote, Trading
from Model import Indicator
from Model.Indicator import Price
from vnstock import Vnstock

class StockData:
    def __init__(self, symbol: str, source="VCI"):
        self.symbol = symbol
        self.source = source

    def listing_information_all_symbols(self):
        listing = Listing(source=self.source)
        return listing.all_symbols()

    #Exchange: HOSE, HNX
    def listing_information_by_exchange(self, exchange: str):
        listing = Listing(source=self.source)
        return listing.symbols_by_exchange(exchange)

    #VN30, VN100
    def listing_information_by_group(self, group: str):
        listing = Listing(source=self.source)
        return listing.symbols_by_group(group)

    def listing_information_by_industries(self):
        listing = Listing(source=self.source)
        return listing.symbols_by_industries()

    def listing_information_by_industries_icb(self):
        listing = Listing(source=self.source)
        return listing.industries_icb()

    def get_history_price(self, symbol: str, length: str, interval: str):
        quote = Quote(symbol, source=self.source)
        return quote.history(length=length, interval=interval)

    def get_historical_price(self, symbol: str, start: str, end: str, interval: str):
        quote = Quote(symbol, source=self.source)
        return quote.history(start=start, end=end, interval=interval)

    def get_trading_price(self, symbols_list :list[str]):
        trading = Trading(source=self.source,symbol="VCI")
        board = trading.price_board(symbols_list= symbols_list)

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
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-15')

        df['vol_ma10'] = df['volume'].rolling(10).mean()
        df['vol_ma20'] = df['volume'].rolling(20).mean()
        df['vol_ma50'] = df['volume'].rolling(50).mean()
        df['price_ma10'] = df['close'].rolling(10).mean()
        df['price_ma20'] = df['close'].rolling(20).mean()
        df['price_ma50'] = df['close'].rolling(50).mean()
        print(df)

    #sai dâta
    def On_Balance_Volume(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2026-02-12', end='2026-02-13')

        df['obv'] = ta.volume.OnBalanceVolumeIndicator(
            close=df['close'],
            volume=df['volume']
        ).on_balance_volume()

        print(df)

    #sai data
    def Volume_Oscillator(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-31', end='2026-02-13')

        # Tính MA volume
        df['vol_ma5'] = df['volume'].rolling(5).mean()
        df['vol_ma20'] = df['volume'].rolling(20).mean()

        # Volume Oscillator (dạng %)
        df['volume_osc'] = ((df['vol_ma5'] - df['vol_ma20']) / df['vol_ma20']) * 100

        # df['vol_ema5'] = df['volume'].ewm(span=5, adjust=False).mean()
        # df['vol_ema20'] = df['volume'].ewm(span=20, adjust=False).mean()
        #
        # df['volume_osc'] = (
        #                            (df['vol_ema5'] - df['vol_ema20']) / df['vol_ema20']
        #                    ) * 100
        print(df)

    #wrong result
    def Accumulation_Distribution(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        df['ad'] = ta.volume.AccDistIndexIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        ).acc_dist_index()

        print(df)

    def Average_True_Range(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        df['atr_14'] = ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        ).average_true_range()

        print(df)

    def Average_True_Range_MA5(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        df['atr_14'] = ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        ).average_true_range()

        df['atr_ma5'] = df['atr_14'].rolling(5).mean()

        print(df)

    def Bollinger_Bands(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        bb = ta.volatility.BollingerBands(
            close=df['close'],
            window=20,
            window_dev=2
        )

        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()

        print((df))

    def Donchian_Channel(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        dc = ta.volatility.DonchianChannel(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=20
        )

        df['dc_upper'] = dc.donchian_channel_hband()
        df['dc_lower'] = dc.donchian_channel_lband()
        df['dc_middle'] = dc.donchian_channel_mband()

        print(df)

    def Relative_Strength_Index(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        df['rsi_14'] = ta.momentum.RSIIndicator(
            close=df['close'],
            window=14
        ).rsi()

        print(df)

    def Average_Directional_Index(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        adx = ta.trend.ADXIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        )

        df['adx_14'] = adx.adx()
        df['plus_di'] = adx.adx_pos()
        df['minus_di'] = adx.adx_neg()

        print(df)

    def Moving_Average_Convergence_Divergence(self):
        stock = Vnstock().stock(symbol='HPG', source=self.source)
        df = stock.quote.history(start='2025-12-01', end='2026-02-13')

        macd = ta.trend.MACD(
            close=df['close'],
            window_slow=26,
            window_fast=12,
            window_sign=9
        )

        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_hist'] = macd.macd_diff()

        print(df)