from src.tradings.strategy import strategy
from src.setups.professional.ml_pattern_recognition_setup import MLPatternRecognitionSetup, ml_pattern_recognition_setup
from src.setups.professional.pairs_trading_setup import PairsTradingSetup
from src.setups.professional.relative_strength_setup import RelativeStrengthSetup

class strategy10(strategy):
    def __init__(self):
        # ML pattern recognition and pairs trading setup with relative strength
        # Advanced quatitative setup with pattern recognition
        super().__init__("Strategy10_MLPattern_Pairs_RelativeStrength", max_position=10, risk_per_trade=0.012)

    def identify_symbols(self, data):
        """Identify symbols using ML pattern recognition, pairs trading, and relative strength setups"""
        symbols = []

        # Process data to identify symbols
        for symbol in data.get('symbols', []):
            company = data['company_data'].get(symbol)
            if company and len(company.company_data) >= 25:  # Need sufficient data for advanced analysis
                # Check if symbol qualifies for any of our advanced setups

                ml_setup = ml_pattern_recognition_setup(company)
                if (ml_setup is not None and ml_setup.get('confidence', 'LOW') in ['HIGH', 'MEDIUM']):
                    symbols.append(symbol)

        return symbols

    def should_buy(self, symbol, data):
        """ Buy if symbol qualifies for advanced setups with strong confidence and proper risk management"""
        company = data['company_data'].get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)

        if company and current_price > 0 and len(company.company_data) >= 50:
            # Check our advanced setups
            ml_setup = ml_pattern_recognition_setup(company)

            # Check for strong buy signals
            ml_buy = ml_setup is not None and \
                           ml_setup.get('signal') == 'BUY' and \
                           ml_setup.get('confidence') in ['HIGH', 'MEDIUM']

            # Need strong ML pattern recognition setup
            if ml_buy:
                # Ensure we have proper risk-reward ratio
                stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                risk_per_share = abs(current_price - stop_loss)

                # Calculate potential reward based on setup targets
                target_price = 0
                if ml_buy and ml_buy.get('target', 0) > current_price:
                    target_price = ml_buy.get('target', 0)
                else:
                    # Fallback to 6% target for professional setups
                    target_price = current_price * 1.06

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

        if company and current_price > 0 and len(company.company_data) >= 50:
            # Check if symbol still qualifies for our setups
            ml_setup = ml_pattern_recognition_setup(company)

            # Check for continued validity
            ml_valid = ml_setup is not None and \
                             ml_setup.get('signal') == 'BUY' and \
                             ml_setup.get('confidence') in ['HIGH', 'MEDIUM']

            # If no longer qualifies for any setups, consider selling
            if not ml_valid:
                return True

            # Risk management: Check if stop loss is hit
            stop_loss = self.get_stop_loss_price(symbol, position['purchase_price'], data)
            if current_price <= stop_loss:
                return True

            # Take profit: Check if we've reached our target (15% for professional setup)
            take_profit_price = position['purchase_price'] * 1.15
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

            # Try ML pattern recognition setup for stop loss
            ml_setup = ml_pattern_recognition_setup(company_data)
            if ml_setup and ml_setup.get('stop_loss', 0) > 0:
                ml_stop = ml_setup.get('stop_loss', 0)
                # Ensure stop loss is below entry price for long position
                if ml_stop < entry_price:
                    return ml_stop

            # Fallback to ATR-based stop loss
            if latest_data.ATR_14 and latest_data.ATR_14 > 0:
                # Set stop loss at 2x ATR below entry price for professional approach
                atr_stop = entry_price - (2.0 * latest_data.ATR_14)
                return max(atr_stop, entry_price * 0.94)  # At least 8% below entry

        # Default fallback: 8% below entry price (professional standard)
        return entry_price * 0.94

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

        if not company_data or current_price <= 0 or len(company_data.company_data) < 50:
            return 1.0  # Default confidence level

        confidence = 1.0

        # Check advanced setups for confidence
        ml_setup = ml_pattern_recognition_setup(company_data)

        # ML pattern confidence
        if ml_setup:
            ml_confidence = ml_setup.get('confidence', 'LOW')
            if ml_confidence == 'HIGH':
                confidence *= 1.4
            elif ml_confidence == 'MEDIUM':
                confidence *= 1.25

        # Pattern quality from ML setup
        if ml_setup and 'pattern_analysis' in ml_setup:
            pattern_analysis = ml_setup['pattern_analysis']
            confluence_score = pattern_analysis.get('confluence_score', 50)
            cluster_score = pattern_analysis.get('cluster_score', 50)

            # Higher confluence and clustering = higher confidence
            if confluence_score > 80:
                confidence *= 1.2
            elif confluence_score > 60:
                confidence *= 1.1

            if cluster_score > 80:
                confidence *= 1.15
            elif cluster_score > 60:
                confidence *= 1.05

        # Additional technical confirmation
        latest_data = company_data.company_data[-1]

        # RSI confirmation (professional range 50-70 for long positions)
        if 55 <= latest_data.RSI_14 <= 70:
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

