from src.setups.professional.market_microstructure_setup import market_microstructure_strategy
from src.tradings.strategy import strategy
from src.setups.professional.multi_timeframe_setup import MultiTimeframeSetup
from src.setups.professional.harmonic_pattern_setup import HarmonicPatternSetup, harmonic_pattern_setup
from src.setups.professional.market_regime_setup import MarketRegimeSetup

class strategy8(strategy):
    def __init__(self):
        # Multi-timeframe and harmonic pattern setup with market microstructure analysis
        # High confidence, professional-grade setup
        super().__init__("Strategy8-MultiTimeframe-Harmonic-Microstructure", max_position=6, risk_per_trade=0.015)

        def identify_symbols(self, data):
            """Identify symbols using multi-timeframe, harmonic pattern, and market microstructure setups"""
            symbols = []

            # Process data to identify symbols
            for symbol in data.get('symbols', []):
                company = data['company_data'].get(symbol)
                if company and len(company. company_data) >= 50: # Need sufficient data for advanced analysis
                    # Check if symbol qualifies for any of our advanced setups
                    # Note: For multi-timeframe setup, we would need multi-timeframe data which is not available here
                    # For this implementation, we'll focus on harmonic pattern and market microstructure setup

                    harmonic_setup = harmonic_pattern_setup(company)
                    microstructure_setup = market_microstructure_strategy(company, None, None, None)

                    if (harmonic_setup is not None and harmonic_setup.get('confidence', 'LOW') in ['HIGH', 'MEDIUM']) or \
                            (microstructure_setup is not None and microstructure_setup.get('confidence', 'LOW') in ['MEDIUM', 'HIGH']):
                        symbols.append(symbol)

            return symbols

        def should_buy(self, symbol, data):
            """ Buy if symbol qualifies for advanced setups with strong confidence and proper risk management"""
            company = data['company_data'].get(symbol)
            current_price = data.get('current_price', {}).get(symbol, 0)

            if company and current_price > 0 and len(company.company_data) >= 50:
                # Check our advanced setups
                harmonic_setup = harmonic_pattern_setup(company)
                microstructure_setup = market_microstructure_strategy(company, None, None, None)

                # Check for strong buy signals
                harmonic_buy = harmonic_setup is not None and \
                    harmonic_setup.get('signal') == 'BUY' and \
                    harmonic_setup.get('confidence') in ['HIGH', 'MEDIUM']

                microstructure_buy = microstructure_setup is not None and \
                    microstructure_setup.get('signal') == 'BUY' and \
                    microstructure_setup.get('confidence') in ['MEDIUM', 'HIGH']

                # Need at least one strong setup
                if harmonic_buy or microstructure_buy:
                    # Ensure we have proper risk-reward ratio
                    stop_loss = self.get_stop_loss_price(symbol, current_price, data)
                    risk_per_share = abs(current_price - stop_loss)

                    # Calculate potential reward based on setup targets
                    target_price = 0
                    if harmonic_setup and harmonic_setup.get('target', 0) > current_price:
                        target_price = harmonic_setup.get('target', 0)
                    elif microstructure_setup and microstructure_setup.get('target', 0) > current_price:
                        target_price = microstructure_setup.get('target', 0)
                    else:
                        # Fallback to 8% target for professional setups
                        target_price = current_price * 1.08

                    potential_reward = target_price - current_price

                    # Check risk-reward ratio (minimum 2:1 for professional setups)
                    if risk_per_share > 0 and (potential_reward / risk_per_share) >= 2.0:
                        # Check if we have enough cash for minimum position
                        min_investment = current_price * 100 # Minimum 100 shares
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
                harmonic_setup = harmonic_pattern_setup(company)
                microstructure_setup = market_microstructure_strategy(company, None, None, None)

                # Check for continued validity
                harmonic_valid = harmonic_setup is not None and \
                               harmonic_setup.get('signal') == 'BUY' and \
                               harmonic_setup.get('confidence') in ['HIGH', 'MEDIUM']

                microstructure_valid = microstructure_setup is not None and \
                                     microstructure_setup.get('signal') == 'BUY' and \
                                     microstructure_setup.get('confidence') in ['MEDIUM', 'HIGH']

                # If no longer qualifies for any setups, consider selling
                if not harmonic_valid and not microstructure_valid:
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

                # Try harmonic pattern setup for stop loss
                harmonic_setup = harmonic_pattern_setup(company_data)
                if harmonic_setup and harmonic_setup.get('stop_loss', 0) > 0:
                    harmonic_stop = harmonic_setup.get('stop_loss', 0)
                    # Ensure stop loss is below entry price for long position
                    if harmonic_stop < entry_price:
                        return harmonic_stop

                # Try market microstructure setup for stop loss
                microstructure_setup = market_microstructure_strategy(company_data, None, None, None)
                if microstructure_setup and microstructure_setup.get('stop_loss', 0) > 0:
                    microstructure_stop = microstructure_setup.get('stop_loss', 0)
                    # Ensure stop loss is below entry price for long position
                    if microstructure_stop < entry_price:
                        return microstructure_stop

                # Fallback to ATR-based stop loss
                if latest_data.ATR_14 and latest_data.ATR_14 > 0:
                    # Set stop loss at 2.5x ATR below entry price for professtional approach
                    atr_stop = entry_price - (2.5 * latest_data.ATR_14)
                    return max(atr_stop, entry_price * 0.92) # At least 8% below entry

            # Default fallback: 8% below entry price (professional standard)
            return entry_price * 0.92

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
                return 1.0 # Default confidence level

            confidence = 1.0

            # Check advanced setups for confidence
            harmonic_setup = harmonic_pattern_setup(company_data)
            microstructure_setup = market_microstructure_strategy(company_data, None, None, None)

            # Harmonic pattern confidence
            if harmonic_setup:
                harmonic_confidence = harmonic_setup.get('confidence', 'LOW')
                if harmonic_confidence == 'HIGH':
                    confidence *= 1.3
                elif harmonic_confidence == 'MEDIUM':
                    confidence *= 1.15

            # Market microstructure confidence
            if microstructure_setup:
                microstructure_confidence = microstructure_setup.get('confidence', 'LOW')
                if microstructure_confidence == 'HIGH':
                    confidence *= 1.25
                elif microstructure_confidence == 'MEDIUM':
                    confidence *= 1.1

            # Additional technical confirmation
            latest_data = company_data.company_data[-1]

            # RSI confirmation (professional range 50-70 for long positions)
            if 55 <= latest_data.RSI_14 <= 65:
                confidence *= 1.1
            elif latest_data.RSI_14 > 70:
                confidence *= 0.85 # Overbought
            elif latest_data.RSI_14 < 30:
                confidence *= 0.9 # Oversold (may reverse)

            # Moving average confirmation (price above key MAs)
            if latest_data.price.close_price > latest_data.moving_average_20.ma_price:
                confidence *= 1.05
            if latest_data.moving_average_10.ma_price > latest_data.moving_average_20.ma_price:
                confidence *= 1.05 # Bullish trend

            # ADX confirmation (strong trend)
            if latest_data.ADX_14.ADX and latest_data.ADX_14.ADX > 30:
                # Strong trend
                if latest_data.ATR_14.plus_DI and latest_data.ADX_14.minus_DI:
                    if latest_data.ADX_14.plus_DI > latest_data.ADX_14.minus_DI:
                        confidence *= 1.2 # Strong bullish trend
                    else:
                        confidence *= 0.8 # Strong bearish trend

            # Ensure confidence level stays within reasonable bounds
            return max(0.5, min(confidence, 2.0))