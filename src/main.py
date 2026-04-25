import os.path
from datetime import datetime
import os

from src.tradings.strategy1 import strategy1
from src.tradings.strategy2 import strategy2
from src.tradings.strategy3 import strategy3
from src.tradings.strategy4 import strategy4
from src.tradings.strategy5 import strategy5
from src.tradings.strategy6 import strategy6
from src.tradings.strategy7 import strategy7
from src.tradings.test_strategy import test_strategy
from models.company import Company, CompanyData
from src.analysis.stock_analyzer import StockAnalyzer
from src.analysis.stock_data import StockData
import pandas as pd
from vnstock import register_user
from filters.volume.MarketCapVolumeFilter import filter_stocks_by_market_cap_and_volume, get_filtered_symbols

isRegistered = False

def process_all_symbols():
    # Init save data
    stock_data = StockData()
    stock_data.init_listing()
    # symbol_list = stock_data.listing_information_by_group("VN100")
    symbol_list = stock_data.listing_information_all_symbols()
    # symbol_list = stock_data.listing_information_by_exchange("HNX")
    filter_symbol_list = {}
    if not os.path.exists('filtered_stocks.csv'):
        print("[Main][process_all_symbols] filtered_stocks is not exists")
        filter_symbol_list = filter_stocks_by_market_cap_and_volume(symbol_list)
        if filter_symbol_list is not None:
            print("[Main][process_all_symbols] Successfully filtered stocks data")
        else:
            print("[Main][process_all_symbols]Failed to filter stocks data")
    else:
        print("[Main][process_all_symbols] Filtered stocks data already exists. Load symbols")
        filter_symbol_list = get_filtered_symbols()
    company_data = {}
    now = datetime.now()
    for symbol in filter_symbol_list:
        try:
            stock_analyzer = StockAnalyzer(symbol)
            stock_analyzer.init_Stock()

            # stock_analyzer.update_data_frame("2024-01-01", "2026-04-23")
            stock_analyzer.update_data_frame("2024-01-01", now.strftime("%Y-%m-%d"))

            if stock_analyzer.data_frame is None:
                print(f"[Main][process_all_symbols] Failed to get stock data: {symbol}")
                continue

            stock_analyzer.Calculate_Trading_Value()
            stock_analyzer.update_full_indicator()
            # print(stock_analyzer.data_frame)
            comp = Company(symbol)
            last_5 = stock_analyzer.data_frame.tail(5)
            print(comp.symbol)
            for index, row in last_5.iterrows():
                compData = CompanyData()
                compData.import_data(row)
                compData.trading_value = row['trading_value']
                compData.moving_average_10.ma_price = row['vol_ma10']
                compData.moving_average_10.ma_volume = row['price_ma10']
                compData.moving_average_10.window = 10
                compData.moving_average_20.ma_price = row['vol_ma20']
                compData.moving_average_20.ma_volume = row['price_ma20']
                compData.moving_average_20.window = 20
                compData.moving_average_50.ma_price = row['vol_ma50']
                compData.moving_average_50.ma_volume = row['price_ma50']
                compData.moving_average_50.window = 50
                compData.On_Balance_Volume = row['obv']
                compData.Volume_Oscillator = row['volume_osc']
                compData.Accumulation_Distribution = row['ad']
                compData.ATR_14 = row['atr_14']
                compData.ATR_MA5 = row['atr_ma5']
                compData.Bollinger_Bands.Middle = row['bb_middle']
                compData.Bollinger_Bands.BB_Upper = row['bb_upper']
                compData.Bollinger_Bands.BB_Lower = row['bb_lower']
                compData.Donchian_Channel.Middle = row['dc_middle']
                compData.Donchian_Channel.Upper_Channel = row['dc_upper']
                compData.Donchian_Channel.Lower_Channel = row['dc_lower']
                compData.RSI_14 = row['rsi_14']
                compData.ADX_14.ADX = row['adx_14']
                compData.ADX_14.plus_DI = row['plus_di']
                compData.ADX_14.minus_DI = row['minus_di']
                compData.MACD.MACD = row['macd']
                compData.MACD.signal = row['macd_signal']
                compData.MACD.histogram = row['macd_hist']
                # compData.StdDev_20 =
                comp.company_data.append(compData)
            # Store company data
            company_data[symbol] = comp
        except Exception as e:
            print("[Main][process_all_symbols] " + comp.symbol + " can't check")
            print(f"[Main][process_all_symbols] Reason: {e}")
            continue
    return company_data

def get_filtered_symbol():
    """Load symbols from filtered_stocks.csv"""
    try:
        # load the filtered sotcks CSV
        filtered_file = "filtered_stocks.csv"

        if os.path.exists(filtered_file):
            df = pd.read_csv(filtered_file)
            if 'symbol' in df.columns:
                symbols = df['symbol'].tolist()
                return symbols
            else:
                print(f"[tradings][get_filtered_symbol] 'symbol' column not found. Please run main.py firest to generate data.")
        else:
            print("[tradings][get_filtered_symbol] No filtered_stocks.csv found")
            return []
    except Exception as e:
        print(f"[tradings][get_filtered_symbol] Error loading filtered_stocks.csv: {e}")
        return []

def get_current_prices(symbols, company_data):
    """Get current prices for symbols from company data"""
    prices = {}
    for symbol in symbols:
       if symbol in company_data and company_data[symbol].company_data:
            # Get the lastest price from company data
            lastest_data = company_data[symbol].company_data[-1]
            if lastest_data and lastest_data.price and lastest_data.price.close_price:
                prices[symbol] = lastest_data.price.close_price
            else:
                # Fallback to average of open and close if close price not available
                if lastest_data.price and lastest_data.price.open_price:
                    prices[symbol] = (lastest_data.price.open_price + lastest_data.price.open_price) / 2 if lastest_data.price.close_price else lastest_data.price.open_price
                else:
                    # Last fallback to a default value
                    prices[symbol] = 100000
    return prices

def run_strategies(company_data):
    print(f"[tradings][main] Loaded company data for {len(company_data)} symbols")

    # Get all symbols
    symbols = get_filtered_symbol()
    if not symbols:
        print("[tradings][main] No symbols found, using all symbols from data")
    print(f"[tradings][main] Found {len(symbols)} symbols to process")

    # Get current prices (simplified)
    current_prices = get_current_prices(symbols, company_data)

    # Create strategies
    strategies = [
        # strategy1(),
        # strategy2(),
        # strategy3(),
        # strategy4(),
        # strategy5(),
        # strategy6(),
        # strategy7(),
        test_strategy()
    ]

    # Prepare data for strategies
    data = {
        'symbols': symbols,
        'company_data': company_data
    }
    # Execute each strategies
    for i, strategy in enumerate(strategies, 1):
        print(f"\n[tradings][main] Executing {strategy.name}...")
        strategy.execute_trades(data, current_prices)

        # Generate report
        report = strategy.get_report(current_prices)
        print(report)

        # Save report to file
        report_file = f"tradings/{strategy.name}_report.csv"
        with open(report_file, "w", encoding='utf-8') as f:
            f.write(report)

        print(f"[tradings][main] Report save to {report_file}")

    print("\n [tradings][main] All strategies executed successfully")

def run_trading_system(company_data):
    """Run the tradings system"""
    run_strategies(company_data)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Check if data.csv existws
    key_path = "../Secret/apikey.txt"
    if os.path.exists(key_path):
        register_user(key_path)

        company_data = process_all_symbols()
        run_trading_system(company_data)
