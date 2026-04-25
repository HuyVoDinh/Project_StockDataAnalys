from src.setups.test_setup import liquidity_setup
from src.tradings.strategy import strategy
from src.setups.short_term.macd_divergence_setup import macd_divergence_setup
from src.setups.short_term.rsi_reversal_setup import rsi_reversal_setup

class test_strategy(strategy):
    def __init__(self):
        # MACD Divergence and RSI Reversal strategy
        # Aggressive approach, 12 maximum positions, higher risk per trade
        super().__init__("Test_Strategy", max_position = 12, risk_per_trade=0.015)

    def identify_symbols(self, data):
        """Identify symbols using MACD Divergence and RSI Reversal setups"""
        symbols = []

        # Procees data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for either setups
                if liquidity_setup(company) is not None:
                    symbols.append(symbol)
            else:
                print(f"[test_strategy][identify_symbols] company data of {symbol} not found")
        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for either setups"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_prices', {}).get(symbol, 0)

        if company and current_price > 0:
            # Check if symbol qualifies for either setups
            liquidity_qualifies = liquidity_setup(company) is not None

            # Additional risk management checks
            if liquidity_qualifies:
                # Ensure have at least 2:1 risk-reward ratio
                return True
            return False
        else:
            print(f"[test_strategy][should_buy] Symbol {symbol} not found")
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol qualifies for either setups"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_prices', {}).get(symbol, 0)
        position = self.portfolio.position.get(symbol)

        if company and current_price > 0 and position:
            # Check uf symbol still qualifies for either setups
            liquidity_qualifies = liquidity_setup(company) is not None
            # If no longer qualifies for any setups, consider selling
            if not liquidity_qualifies:
                return True
            return False
        elif not company and symbol and self.portfolio.position:
            # If don't have data for this symbol anymnore, sell it
            return True
        else:
            print(f"[test_strategy][should_sell] Symbol {symbol} not found")
        return False