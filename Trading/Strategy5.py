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
        current_price = data.get('current_price', {}).get(symbol, 0)

        if company and current_price > 0:
            # Check if symbol qualifies for either setup
            absorption_qualifies = absorption_setup(company) is not None
            volume_qualifies = volume_spike_setup(company) is not None
            rsi_qualifies = rsi_reversal_setup(company) is not None

            # Additional risk management checks
            if absorption_qualifies or volume_qualifies or rsi_qualifies:
                # Ensure have at least 2:1 risk-reward ratio
                stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                risk_per_share = abs(current_price - stop_loss)

                # Calculate potential reward (assuming 5% target for short-term setup)
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
        """Check if symbol qualifies for either setup"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        position = self.portfolio.position.get(symbol)

        if company and current_price > 0 and position:
            # Check uf symbol still qualifies for either setup
            absorption_qualifies = absorption_setup(company) is not None
            volume_qualifies = volume_spike_setup(company) is not None
            rsi_qualifies = rsi_reversal_setup(company) is not None

            # If no longer qualifies for any setup, consider selling
            if not absorption_qualifies and not volume_qualifies and not rsi_qualifies:
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