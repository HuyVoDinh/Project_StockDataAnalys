from src.tradings.strategy import strategy
from src.setups.short_term.macd_divergence_setup import macd_divergence_setup
from src.setups.short_term.rsi_reversal_setup import rsi_reversal_setup

class strategy3(strategy):
    def __init__(self):
        # MACD Divergence and RSI Reversal strategy
        # Aggressive approach, 12 maximum positions, higher risk per trade
        super().__init__("Strategy3_MACD_RSI", max_position = 12, risk_per_trade=0.015)

    def identify_symbols(self, data):
        """Identify symbols using MACD Divergence and RSI Reversal setups"""
        symbols = []

        # Procees data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for either setups
                if macd_divergence_setup(company) is not None or rsi_reversal_setup(company) is not None:
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for either setups"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)

        if company and current_price > 0:
            # Check if symbol qualifies for either setups
            macd_qualifies = macd_divergence_setup(company) is not None
            rsi_qualifies = rsi_reversal_setup(company) is not None

            # Additional risk management checks
            if macd_qualifies or rsi_qualifies:
                # Ensure have at least 2:1 risk-reward ratio
                stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                risk_per_share = abs(current_price - stop_loss)

                # Calculate potential reward (assuming 5% target for short-term setups)
                potential_reward = current_price * 0.05

                # Check risk-reward ratio
                if risk_per_share > 0 and (potential_reward / risk_per_share) >= 2.0:
                    # Check if have enough cash for minimum position
                    min_investment = current_price * 100  # Minimum 100 shares
                    if self.portfolio.cash >= min_investment:
                        return True
            return False
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol qualifies for either setups"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        position = self.portfolio.position.get(symbol)

        if company and current_price > 0 and position:
            # Check uf symbol still qualifies for either setups
            macd_qualifies = macd_divergence_setup(company) is not None
            rsi_qualifies = rsi_reversal_setup(company) is not None

            # If no longer qualifies for any setups, consider selling
            if not macd_qualifies and not rsi_qualifies:
                return True

            # risk management: Check if stop loss is hit
            stop_loss = self.get_stop_loss_price(symbol, position['purchase_price'], data)
            if current_price <= stop_loss:
                return True

            # Check if have hold the position for too long (more than 5 tradings days)
            # This would require tracking purchasew data, which is not currently implemented
            take_profit_price = position['purchase_price'] * 1.08
            if current_price >= take_profit_price:
                return True

            return False

        elif not company and symbol and self.portfolio.position:
            # If don't have data for this symbol anymnore, sell it
            return True
        return False