from Trading.Strategy import Strategy
from Setup.ShortTerm.Ma20RetestSetup import ma20_retest_setup
from Setup.ShortTerm.BBSqueezeSetup import bb_squeeze_setup
from Setup.ShortTerm.MACDDivergenceSetup import macd_divergence_setup

class Strategy4(Strategy):
    def __init__(self):
        # MA20 Retest, Bollinger Band Squeeze, and MACD Divergence strategy
        # Balanced approach, 10 maximum positions
        super().__init__("Strategy4_MA20_BB_MACD", max_position=10, risk_per_trade=0.01)

    def identify_symbols(self,data):
        """Identify symbols using MA20 Retest, Bollinger Band Squeeze, and MACD Divergence setups"""
        symbols = []

        # Process data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company:
                # Check if symbol qualifies for any setup
                if (ma20_retest_setup(company) is not None or bb_squeeze_setup(company) is not None or macd_divergence_setup(company) is not None):
                    symbols.append(symbol)
        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for any setup"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)

        if company and current_price > 0:
            # Check if symbol qualifies for either setup
            ma20_qualifies = ma20_retest_setup(company) is not None
            bb_qualifies = bb_squeeze_setup(company) is not None
            macd_qualifies = macd_divergence_setup(company) is not None

            # Additional risk management checks
            if macd_qualifies or bb_qualifies or ma20_qualifies:
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
        """Sell if symbol qualifies for any setup"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        position = self.portfolio.position.get(symbol)

        if company and current_price > 0 and position:
            # Check uf symbol still qualifies for either setup
            macd_qualifies = macd_divergence_setup(company) is not None
            bb_qualifies = bb_squeeze_setup(company) is not None
            ma20_qualifies = ma20_retest_setup(company) is not None

            # If no longer qualifies for any setup, consider selling
            if not macd_qualifies and not ma20_qualifies and not bb_qualifies:
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