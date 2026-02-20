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
        self.listing = None
        self.trading = None

    def init_listing(self):
        print("Initializing Listing")
        self.listing = Listing(source=self.source)
        print("Listing Initialized")

    def init_Trading(self):
        print("Initializing Trading")
        self.trading = Trading(source=self.source, symbol=self.symbol)
        print("Trading initialized")

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