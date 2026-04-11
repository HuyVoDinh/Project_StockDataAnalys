from Trading.Strategy import Strategy
from Setup.ShortTerm.AbsorptionSetup import absorption_setup
from Setup.ShortTerm.VolumeSpikeSetup import volume_spike_setup
from Setup.ShortTerm.RSIReversalSetup import rsi_reversal_setup

class Strategy5(Strategy):
    def __init__(self):
        # Absorption, Volume Spike, and RSI Reversal strategy
        # Diversified approach, 15 maximum position
        super().__init__("Strategy5_Absorption_Volume_RSI", max_position=15, risk_per_trade=0.01)
        
    def identify_symbols(self, data):
        """Identify symbols using Absorption, Volume Spike, and RSI Reversal setups"""
        symbols = []

        # Process data to identify symbols
        for symbols in data.get('symbols', []):
            company = data['company_data'].get(symbols)
            if company:
                # Check f symbol qualifies for any setup
                if (absorption_setup(company) is not None or volume_spike_setup(company) is not None or rsi_reversal_setup(company) is not None):
                    symbols.append(symbols)
        return symbols

    def should_buy(self, symbol, data):
        """Check if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return (absorption_setup(company) is not None or volume_spike_setup(company) is not None or rsi_reversal_setup(company) is not None)
        return False

    def should_sell(self, symbol, data):
        """Check if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return (absorption_setup(company) is None and volume_spike_setup(company) is None and rsi_reversal_setup(company) is None)
        return True