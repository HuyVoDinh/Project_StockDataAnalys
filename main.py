import os.path
import pickle
import subprocess
import sys
from time import sleep

from Setup.ShortTerm.AbsorptionSetup import absorption_setup
from Setup.ShortTerm.Ma20RetestSetup import ma20_retest_setup
from Setup.ShortTerm.BBSqueezeSetup import bb_squeeze_setup
from  Setup.ShortTerm.RSIReversalSetup import rsi_reversal_setup
from Setup.ShortTerm.VolumeSpikeSetup import volume_spike_setup
from Setup.ShortTerm.MACDDivergenceSetup import macd_divergence_setup
from Setup.LongTerm.LongTrendFollowingSetup import long_trend_following_setup
from Setup.LongTerm.FundamentalTechnicalSetup import fundamental_technical_setup
from Setup.MediumTerm.MA50SupportSetup import ma50_support_setup
from Setup.MediumTerm.BreakoutVolumeSetup import breakout_volume_setup
from Setup.MediumTerm.MultiTimeframeTrendSetup import multi_timeframe_trend_setup
from Model.Company import Company, CompanyData
from StockData.stock_analyzer import StockAnalyzer
from StockData.stock_data import StockData
import pandas as pd
from vnstock import register_user
from Filter.Volume.MarketCapVolumeFilter import filter_stocks_by_market_cap_and_volume, get_filtered_symbols

isRegistered = False

def process_all_symbols():
    # Init save data
    ##############  Volume  ######################
    symbol_list_1 = []
    symbol_list_2 = []
    symbol_list_3 = []
    symbol_list_4 = []
    symbol_list_5 = []
    symbol_list_6 = []
    symbol_list_7 = []
    symbol_list_8 = []
    symbol_list_9 = []
    symbol_list_10 = []
    symbol_list_11 = []
    demo_symbol_list = []

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

    for symbol in filter_symbol_list:
        try:
            stock_analyzer = StockAnalyzer(symbol)
            stock_analyzer.init_Stock()
            stock_analyzer.update_data_frame("2026-03-01", "2026-04-16")

            if stock_analyzer.data_frame is None:
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

        if ma20_retest_setup(comp) is not None:
            symbol_list_1.append(comp.symbol)

        if absorption_setup(comp) is not None:
            symbol_list_2.append(comp.symbol)

        if bb_squeeze_setup(comp) is not None:
            symbol_list_3.append(comp.symbol)

        if volume_spike_setup(comp) is not None:
            symbol_list_4.append(comp.symbol)

        if macd_divergence_setup(comp) is not None:
            symbol_list_5.append(comp.symbol)

        if rsi_reversal_setup(comp) is not None:
            symbol_list_6.append(comp.symbol)

        if ma50_support_setup(comp) is not None:
            symbol_list_7.append(comp.symbol)

        if multi_timeframe_trend_setup(comp) is not None:
            symbol_list_8.append(comp.symbol)

        if breakout_volume_setup(comp) is not None:
            symbol_list_9.append(comp.symbol)

        if long_trend_following_setup(comp) is not None:
            symbol_list_10.append(comp.symbol)

        if fundamental_technical_setup(comp) is not None:
            symbol_list_11.append(comp.symbol)

    ####### Export dataf
    df1 = pd.DataFrame(symbol_list_1, columns=['ma20_retest_setup'])
    df2 = pd.DataFrame(symbol_list_2, columns=['absorption_setup'])
    df3 = pd.DataFrame(symbol_list_3, columns=['bb_squeeze_setup'])
    df4 = pd.DataFrame(symbol_list_4, columns=['volume_spike_setup'])
    df5 = pd.DataFrame(symbol_list_5, columns=['macd_divergence_setup'])
    df6 = pd.DataFrame(symbol_list_6, columns=['rsi_reversal_setup'])
    df7 = pd.DataFrame(symbol_list_7, columns=['ma50_support_setup'])
    df8 = pd.DataFrame(symbol_list_8, columns=['multi_timeframe_trend_setup'])
    df9 = pd.DataFrame(symbol_list_9, columns=['breakout_volume_setup'])
    df10 = pd.DataFrame(symbol_list_10, columns=['long_trend_following_setup'])
    df11 = pd.DataFrame(symbol_list_11, columns=['fundamental_technical_setup'])

    result_data = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11], axis=1)

    # Save company data to file for trading system
    try:
        with open('company_data.pkl', 'wb') as f:
            pickle.dump(company_data, f)
    except Exception as e:
        print(f'[Main][process_all_symbols] Error saving company data: {e}')

    return result_data, company_data

def compare_result(input_data, output_data):
    """Compare input and output data to generate available"""
    # Get all symbols from input data
    input_symbols = set()
    for column in input_data.columns:
        input_symbols.update(input_data[column].dropna().tolist())

    # Get all symbols from output data
    output_symbols = set()
    for column in output_data.columns:
        output_symbols.update(output_data[column].dropna().tolist())

    # Categorize symbols
    available = input_symbols.intersection(output_symbols)
    unavailable = input_symbols.difference(output_symbols)
    potential = output_symbols.intersection(input_symbols)

    return available, unavailable, potential

def write_comparison_report(available, unavailable, potential, filename="comparison_report.txt"):
    """Write the comparison report to a text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Symbol Analysis report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Available Symbol ({len(available)}):\n)")
        f.write("-" * 30 + "\n")
        for symbol in available:
            f.write(f"{symbol}\n")
        f.write("\n")
        f.write(f"Unavailable Symbol ({len(unavailable)}):\n)")
        f.write("-" * 30 + "\n")
        for symbol in unavailable:
            f.write(f"{symbol}\n")
        f.write("\n")
        f.write(f"Potential Symbol ({len(potential)}):\n)")
        f.write("-" * 30 + "\n")
        for symbol in potential:
            f.write(f"{symbol}\n")
        f.write("\n")

def run_trading_system():
    """Run the trading system"""
    try:
        print("[Main][run_trading_system] Run the trading system")
        result = subprocess.run([sys.executable, "Trading/main.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[Main][run_trading_system] Trading system executed successfully")
            print(result.stdout)
        else:
            print("[Main][run_trading_system] Error running trading system")
            print(result.stderr)
    except Exception as e:
        print(f"[Main][run_trading_system] Error running trading system: {e}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Check if data.csv existws
    key_path = "Secret/apikey.txt"
    if os.path.exists(key_path):
        register_user(key_path)
        csv_file_path = "data.csv"

        if not os.path.exists(csv_file_path):
            print("[Main][main] No existing csv file found. Processing all symbols and creating new data.csv...")
            # Process all symbols and save to CSV
            result_data, company_data = process_all_symbols()
            result_data.to_csv(csv_file_path, index=False)
            print("[Main][main] Processing complete. Data saved to data.csv")
        else:
            print("[Main][main] Existing CSV file found. Loading input data...")
            # Load existing data
            input_data = pd.read_csv(csv_file_path)

            print("[Main][main] Processing all symbols to find potential opportunities...")
            # processs all symbols to get current results
            output_data, company_data = process_all_symbols()

            # Save current results for next day use
            output_data.to_csv("data_current", index=False)

            # Compare results
            available, unavailable, potential = compare_result(input_data, output_data)

            # write comparision report
            write_comparison_report(available, unavailable, potential)

            print("[Main][main] Analysis complete.")
            print(f"[Main][main] - Available symbols: {len(available)}")
            print(f"[Main][main] - Unavailable symbols: {len(unavailable)}")
            print(f"[Main][main] - Potential symbols: {len(potential)}")
            print("[Main][main] Detailed report saved to comparison_report.txt")
            print("[Main][main] Current data saved to data_current.csv for next day use")

        run_trading_system()
