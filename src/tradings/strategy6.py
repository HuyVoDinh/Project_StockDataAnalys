from src.tradings.strategy import strategy
from src.setups.short_term.price_action_setup import price_action_setup

class strategy6(strategy):
    def __init__(self):
        # Price Action Strategy
        # Conservative approach with strong signal confirmation
        super().__init__("Strategy6_PriceAction", max_position=8, risk_per_trade=0.015)

    def identify_symbols(self, data):
        """Identify symbols using Price Action setups"""
        symbols = []
        market_data = data.get('market_data', [])

        # Process data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for price action setups
                if price_action_setup(company, market_data) is not None:
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for price action setups with additional risk management"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        market_data = data.get('market_data', [])

        if company and current_price > 0:
            # Check if symbol qualifies for price action setups
            price_action_qualifies = price_action_setup(company, market_data) is not None

            # Additional risk management checks
            if price_action_qualifies:
                # Ensure haver at least 2.5:1 risk-reward ratio (conservative)
                stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                risk_per_share = abs(current_price - stop_loss)

                # Calculate potential reward (assuming 6% target for price action setups)
                potential_reward = current_price * 0.06

                # Check risk-reward ratio
                if risk_per_share > 0 and (potential_reward / risk_per_share) >= 2.5:
                    # Check if havee enough cash for minimum position
                    min_investment = current_price * 100
                    if self.portfolio.cash >= min_investment:
                        return True
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol no longer qualifies for price action setups or risk management conditions are met"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        position = self.portfolio.positions.get(symbol)
        market_data = data.get('market_data', [])

        if company and current_price > 0 and position:
            # Check if symbol still qualifies for price action setups
            price_action_qualifies = price_action_setup(company, market_data) is not None

            # If no longer qualifies for setups, consider selling
            if not price_action_qualifies:
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