from Trading.Strategy import Strategy
from Setup.ShortTerm.MACDDivergenceSetup import macd_divergence_setup
from Setup.ShortTerm.RSIReversalSetup import rsi_reversal_setup

class Strategy3(Strategy):
    def __init__(self):
        # MACD Divergence and RSI Reversal strategy
        # Aggressive approach, 12 maximum positions, higher risk per trade
        super().__init__("Trategy3_MACD_RSI", max_position = 12, risk_per_trade=0.015)

    def identify_symbols(self, data):
        """Identify symbols using MACD Divergence and RSI Reversal setups"""
        symbols = []

        # Procees data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for either setup
                if macd_divergence_setup(company) is not None or rsi_reversal_setup(company) is not None:
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return macd_divergence_setup(company) is not None or rsi_reversal_setup(company) is not None
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        if company:
            return macd_divergence_setup(company) is None and rsi_reversal_setup(company) is None
        return True