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
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for either setup
                if ma20_retest_setup(company) is not None or volume_spike_setup(company) is not None:
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for either setup with additional risk management"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)

        if company and current_price > 0:
            # Check if symbol qualifies for either setup
            ma20_qualifies = ma20_retest_setup(company) is not None
            volume_qualifies = volume_spike_setup(company) is not None

            # Additional risk management checks
            if ma20_qualifies or volume_qualifies:
                # Ensure have at least 2:1 risk-reward ratio
                stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                risk_per_share = abs(current_price - stop_loss)

                # Calculate potential reward (assuming 5% target for short-term setup)
                potential_reward = current_price * 0.05

                # Check risk-reward ratio
                if risk_per_share > 0 and (potential_reward / risk_per_share) >= 2.0:
                    # Check if have enough cash for minimum position
                    min_investment = current_price * 100 # Minimum 100 shares
                    if self.portfolio.cash >= min_investment:
                        return True
            return False
        return False

    def should_sell(self, symbol, data):
        """Sell if symbol no longer qualifies for either setups or risk management conditions are met"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        position = self.portfolio.position.get(symbol)

        if company and current_price > 0 and position:
            # Check uf symbol still qualifies for either setup
            ma20_qualifies = ma20_retest_setup(company) is not None
            volume_qualifies = volume_spike_setup(company) is not None

            # If no longer qualifies for any setup, consider selling
            if not ma20_qualifies and not volume_qualifies:
                return True

            # Risk management: Check if stop loss is hit
            stop_loss = self.get_stop_loss_price(symbol, position['purchase_price'], data)
            if current_price <= stop_loss:
                return True

            # Check if have hold the position for too long (more than 5 trading days)
            # This would require tracking purchasew data, which is not currently implemented
            take_profit_price = position['purchase_price'] * 1.08
            if current_price >= take_profit_price:
                return True

            return False

        elif not company and symbol and self.portfolio.position:
            # If don't have data for this symbol anymnore, sell it
            return True
        return False