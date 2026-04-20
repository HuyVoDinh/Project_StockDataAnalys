from src.trading.strategy import Strategy
from src.setup.short_term.support_resistance_setup import support_resistance_setup

class Strategy7(Strategy):
    def __init__(self):
        # Support Resistance Strategy
        # Balanced approach with support/resistance confirmation
        super().__init__("Strategy7_SupportResistance", max_position=10, risk_per_trade=0.012)

    def identify_symbols(self, data):
        """Identify symbols using Support Resistance setup"""
        symbols = []
        market_data = data.get('market_data', [])

        # Process data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for support/resistance setup
                if support_resistance_setup(company, market_data) is not None:
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for support/resistance setup with additional risk management"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        market_data = data.get('market_data', [])

        if company and current_price > 0:
            # Check if symbol qualifies for support/resistance setup
            support_resistance_qualifies = support_resistance_setup(company, market_data) is not None

            # Additional risk management checks
            if support_resistance_qualifies:
                # Ensure haver at least 2.5:1 risk-reward ratio (conservative)
                stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                risk_per_share = abs(current_price - stop_loss)

                # Calculate potential reward (assuming 6% target for support/resistance setup)
                potential_reward = current_price * 0.06

                # Check risk-reward ratio
                if risk_per_share > 0 and (potential_reward / risk_per_share) >= 2.5:
                    # Check if have enough cash for minimum position
                    min_investment = current_price * 100
                    if self.portfolio.cash >= min_investment:
                        return True
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol no longer qualifies for support/resistance setup or risk management conditions are met"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        position = self.portfolio.positions.get(symbol)
        market_data = data.get('market_data', [])

        if company and current_price > 0 and position:
            # Check if symbol still qualifies for support/resistance setup
            support_resistance_qualifies = support_resistance_setup(company, market_data) is not None

            # If no longer qualifies for setup, consider selling
            if not support_resistance_qualifies:
                return True

            # risk management: Check if stop loss is hit
            stop_loss = self.get_stop_loss_price(symbol, position['purchase_price'], data)
            if current_price <= stop_loss:
                return True
            return False
        elif not company and symbol in self.portfolio.positions:
            # If dont have data for this symbol anymore, sell
            return True
        return False