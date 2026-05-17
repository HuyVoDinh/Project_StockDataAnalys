from src.tradings.strategy import strategy
from src.setups.professional.reinforcement_learning_setup import reinforcement_learning_setup
from src.setups.professional.volatility_crush_setup import volatility_crush_setup
from src.setups.professional.mean_reversion_setup import mean_reversion_setup

class strategy10(strategy):
    def __init__(self):
        # Reinforcement learning and volatility crush setup with mean reversion
        # Advanced adaptive setup with volatility targeting
        super().__init__("Strategy11_ReinforcementLearning_VolatilityCrush", max_position=7, risk_per_trade=0.018)

    def identify_symbols(self, data):
        """Identify symbols using order flow, regime shift, and statistical arbitrage setups"""
        symbols = []

        # Process data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company and len(company.company_data) >= 30:  # Need sufficient data for advanced analysis
                # Check if symbol qualifies for any of our advanced setups
                rl_setup = reinforcement_learning_setup(company)
                volatility_setup = volatility_crush_setup(company)

                if (rl_setup is not None and rl_setup.get('confidence', 'LOW') in ['HIGH', 'MEDIUM']) or \
                        (volatility_setup is not None and volatility_setup.get('confidence', 'LOW') in ['LOW', 'MEDIUM']):
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """Buy if symbol qualifies for advanced setups with strong confidence and proper risk management"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_prices', {}).get(symbol, 0)

        if company and current_price > 0 and len(company.company_data) >= 30:
            # Check our advanced setups
            rl_setup = reinforcement_learning_setup(company)
            volatility_setup = volatility_crush_setup(company)

            # Check for strong buy signals
            rl_buy = rl_setup is not None and \
                            rl_setup.get('signal') == 'BUY' and \
                            rl_setup.get('confidence') in ['HIGH', 'MEDIUM']

            volatility_buy = volatility_setup is not None and \
                         volatility_setup.get('signal') == 'BUY' and \
                         volatility_setup.get('confidence') in ['MEDIUM', 'HIGH']

            # Need at least one strong setup
            if rl_buy or volatility_buy:
                # Ensure we have proper risk-reward ratio
                stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                risk_per_share = abs(current_price - stop_loss)

                # Calculate potential reward based on setup targets
                target_price = 0
                if rl_buy and rl_buy.get('target', 0) > current_price:
                    target_price = rl_buy.get('target', 0)
                elif volatility_buy and volatility_buy.get('target', 0) > current_price:
                    target_price = volatility_buy.get('target', 0)
                else:
                    # Fallback to 7% target for professional setups
                    target_price = current_price * 1.07

                potential_reward = target_price - current_price

                # Check risk-reward ratio (minimum 2:1 for professional setups)
                if risk_per_share > 0 and (potential_reward / risk_per_share) >= 2.0:
                    # Check if we have enough cash for minimum position
                    min_investment = current_price * 100  # Minimum 100 shares
                    if self.portfolio.cash >= min_investment:
                        return True
        return False

    def should_sell(self, symbol, data):
        """Sell it symbol no longer qualifies for setups or risk management conditions are met"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)
        position = self.portfolio.positions.get(symbol)

        if company and current_price > 0 and len(company.company_data) >= 20:
            # Check if symbol still qualifies for our setups
            rl_setup = reinforcement_learning_setup(company)
            volatility_setup = volatility_crush_setup(company)

            # Check for continued validity
            rl_valid = rl_setup is not None and \
                              rl_setup.get('signal') == 'BUY' and \
                              rl_setup.get('confidence') in ['HIGH', 'MEDIUM']

            volatility_valid = volatility_setup is not None and \
                           volatility_setup.get('signal') == 'BUY' and \
                           volatility_setup.get('confidence') in ['MEDIUM', 'HIGH']

            # If no longer qualifies for any setups, consider selling
            if not rl_valid and not volatility_valid:
                return True

            # Risk management: Check if stop loss is hit
            stop_loss = self.get_stop_loss_price(symbol, position['purchase_price'], data)
            if current_price <= stop_loss:
                return True

            # Take profit: Check if we've reached our target (14% for professional setup)
            take_profit_price = position['purchase_price'] * 1.14
            if current_price >= take_profit_price:
                return True

            # Time-based exit: Check if we've held the position for too long (more than 10 trading days)
            # This would require tracking purchase data, which is not currently implemented
            return False
        elif not company and symbol in self.portfolio.positions:
            # If we dont have data for this symbol anymore, sell it
            return True
        return False

    def get_stop_loss_price(self, symbol, entry_price, data):
        """Determine stop loss price for a symbol based on advanced technical analysis"""
        # Get company data for technical analysis
        company_data = data.get('company_data', {}).get(symbol)

        if company_data and len(company_data.company_data) >= 20:
            latest_data = company_data.company_data[-1]
            # Use our advanced setup to determine stop loss

            # Try reinforcement learning setup for stop loss
            rl_setup = reinforcement_learning_setup(company_data)
            if rl_setup and rl_setup.get('stop_loss', 0) > 0:
                rl_stop = rl_setup.get('stop_loss', 0)
                # Ensure stop loss is below entry price for long position
                if rl_stop < entry_price:
                    return rl_stop

            # Try market microstructure setup for stop loss
            volatility_setup = volatility_crush_setup(company_data)
            if volatility_setup and volatility_setup.get('stop_loss', 0) > 0:
                volatility_stop = volatility_setup.get('stop_loss', 0)
                # Ensure stop loss is below entry price for long position
                if volatility_stop < entry_price:
                    return volatility_stop

            # Fallback to ATR-based stop loss
            if latest_data.ATR_14 and latest_data.ATR_14 > 0:
                # Set stop loss at 2.5x ATR below entry price for professtional approach
                atr_stop = entry_price - (2.5 * latest_data.ATR_14)
                return max(atr_stop, entry_price * 0.93)  # At least 7% below entry

        # Default fallback: 7% below entry price (professional standard)
        return entry_price * 0.93

    def get_confidence_level(self, symbol, data):
        """
        Determine confidence level for a symbol based on advanced setups (0.5 to 2.0)
        Higher confidence = larger position size
        :param self:
        :param symbol:
        :param data:
        :return:
        """
        # Get company data for technical analysis
        company_data = data.get('company_data', {}).get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)

        if not company_data or current_price <= 0 or len(company_data.company_data) < 20:
            return 1.0  # Default confidence level

        confidence = 1.0

        # Check advanced setups for confidence
        rl_setup = reinforcement_learning_setup(company_data)
        volatility_setup = volatility_crush_setup(company_data)

        # orderflow pattern confidence
        if rl_setup:
            rl_confidence = rl_setup.get('confidence', 'LOW')
            if rl_confidence == 'HIGH':
                confidence *= 1.3
            elif rl_confidence == 'MEDIUM':
                confidence *= 1.15

        # regime shift confidence
        if volatility_setup:
            volatility_confidence = volatility_setup.get('confidence', 'LOW')
            if volatility_confidence == 'HIGH':
                confidence *= 1.25
            elif volatility_confidence == 'MEDIUM':
                confidence *= 1.1

        # Additional technical confirmation
        latest_data = company_data.company_data[-1]

        # RSI confirmation (professional range 50-70 for long positions)
        if 50 <= latest_data.RSI_14 <= 70:
            confidence *= 1.1
        elif latest_data.RSI_14 > 75:
            confidence *= 0.85  # Overbought
        elif latest_data.RSI_14 < 25:
            confidence *= 0.9  # Oversold (may reverse)

        # Moving average confirmation (price above key MAs)
        if latest_data.price.close_price > latest_data.moving_average_20.ma_price:
            confidence *= 1.1
        if latest_data.moving_average_10.ma_price > latest_data.moving_average_20.ma_price:
            confidence *= 1.1  # Bullish trend

        # Bollinger Band confirmation (price near upper band for momentum)
        if latest_data.Bollinger_Bands and latest_data.price.close_price > latest_data.Bollinger_Bands.BB_Upper:
            confidence *= 1.15 # Strong momentum

        # ADX confirmation (strong trend)
        if latest_data.ADX_14.ADX and latest_data.ADX_14.ADX > 25:
            # Strong trend
            if latest_data.ATR_14.plus_DI and latest_data.ADX_14.minus_DI:
                if latest_data.ADX_14.plus_DI > latest_data.ADX_14.minus_DI:
                    confidence *= 1.2  # Strong bullish trend
                else:
                    confidence *= 0.8  # Strong bearish trend

        # Ensure confidence level stays within reasonable bounds
        return max(0.5, min(confidence, 2.0))

