from Trading.Strategy import Strategy
from Setup.ShortTerm.Ma20RetestSetup import ma20_retest_setup
from Setup.ShortTerm.VolumeSpikeSetup import volume_spike_setup

class Strategy1(Strategy):
    def __init__(self):
        # MA retest and volume spike strategy
        # Moderate risk, 8 maximum position
        super().__init__("Strategy_1_MA20_Volume", max_position=9, risk_per_trade=0.01)

    def identify_symbols(self, data):
        """Identify symbols using MA20 Retest and Volume spike setups"""
        symbols = []

        # Process data to identify symbols
        for symbols in data.get('symbols', []):
            company = data['company_data'].get(symbols)
            if company:
                # Check if symbol qualifies for either setup
                if ma20_retest_setup(company) is not None or volume_spike_setup(company) is not None:
                    symbols.append(symbols)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return ma20_retest_setup(company) is not None or volume_spike_setup(company) is not None
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return ma20_retest_setup(company) is None and volume_spike_setup(company) is None
        return False