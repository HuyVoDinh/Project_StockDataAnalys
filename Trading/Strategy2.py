from numpy.ma.core import maximum

from Trading.Strategy import Strategy
from Setup.ShortTerm.AbsorptionSetup import absorption_setup
from Setup.ShortTerm.BBSqueezeSetup import bb_squeeze_setup

class Strategy2(Strategy):
    def __init__(self):
        # Absorption and Bollinger Band Squeeze strategy
        # Conservative approach, 6 maximum position, lower risk per trade
        super().__init__("Strategy2_Absorption_BBSqueeze", max_position=6, risk_per_trade=0.05)

    def identify_symbols(self, data):
        """Identify symbols using Absorption and Bollinger Band Squeeze setups"""
        symbols = []

        # Process data to identify  symbols
        for symbol in data.get('symbols',[]):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for either setup
                if absorption_setup(company) is not None or bb_squeeze_setup(company) is not None:
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return absorption_setup(company) is not None or bb_squeeze_setup(company) is not None
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return absorption_setup(company) is None and bb_squeeze_setup(company) is None
        return True