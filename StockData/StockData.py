from vnstock import Listing
from vnstock import Quote, Trading

def listing_information_all_symbols():
    listing = Listing(source="VCI")
    return listing.all_symbols()

#Exchange: HOSE, HNX
def listing_information_by_exchange(exchange: str):
    listing = Listing(source="VCI")
    return listing.symbols_by_exchange(exchange)

#VN30, VN100
def listing_information_by_group(group: str):
    listing = Listing(source="VCI")
    return listing.symbols_by_group(group)

def listing_information_by_industries():
    listing = Listing(source="VCI")
    return listing.symbols_by_industries()

def listing_information_by_industries_icb():
    listing = Listing(source="VCI")
    return listing.industries_icb()

def get_history_price(symbol: str, length: str, interval: str):
    quote = Quote(symbol, source="VCI")
    return quote.history(length=length, interval=interval)

def get_historical_price(symbol: str, start: str, end: str, interval: str):
    quote = Quote(symbol, source="VCI")
    return quote.history(start=start, end=end, interval=interval)

def get_trading_price(symbols_list :list[str]):
    trading = Trading(source="VCI",symbol="VCI")
    board = trading.price_board(symbols_list= symbols_list)

    trading_info = board[[('listing', 'symbol'), ('listing', 'ref_price'), ('listing', 'exchange')]]
    return trading_info