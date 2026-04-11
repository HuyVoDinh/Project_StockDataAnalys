from Trading.Strategy import Strategy
from Setup.ShortTerm.Ma20RetestSetup import ma20_retest_setup
from Setup.ShortTerm.BBSqueezeSetup import bb_squeeze_setup
from Setup.ShortTerm.MACDDivergenceSetup import macd_divergence_setup

class Strategy4(Strategy):
    def __init__(self):
        # MA20 Retest, Bollinger Band Squeeze, and MACD Divergence strategy
        # Balanced approach, 10 maximum positions
        super().__init__("Strategy4_MA20_BB_MACD", max_position=10, risk_per_trade=0.01)

    def identify_symbols(self,data):
        """Identify symbols using MA20 Retest, Bollinger Band Squeeze, and MACD Divergence setups"""
        symbols = []

        # Process data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for any setup
                if (ma20_retest_setup(company) is not None or bb_squeeze_setup(company) is not None or macd_divergence_setup(company) is not None):
                    symbols.append(symbol)
        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for any setup"""
        company = data['company_data'].get(symbol)
        if company:
            return (ma20_retest_setup(company) is not None or bb_squeeze_setup(
                company) is not None or macd_divergence_setup(company) is not None)
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol qualifies for any setup"""
        company = data['company_data'].get(symbol)
        if company:
            return (ma20_retest_setup(company) is None and bb_squeeze_setup(
                company) is None and macd_divergence_setup(company) is None)
        return True