from abc import ABC, abstractmethod
from src.tradings.portfolio import portfolio


class strategy(ABC):
    def __init__(self, name, max_position=10, risk_per_trade=0.01):
        self.name = name
        self.portfolio = portfolio(name)
        self.symbol = [] # Symbols identified by this strategy
        self.max_position = max_position # Maximum number of position to hold
        self.risk_per_trade = risk_per_trade # risk percentage per trade (1% of portfolio)

    @abstractmethod
    def identify_symbols(self, data):
        """Identify symbols based on strategy criteria"""
        pass

    @abstractmethod
    def should_buy(self, symbol, data):
        """Determine if we should buy a symbol"""
        pass

    @abstractmethod
    def should_sell(self, symbol, data):
        """Determine if we should sell a symbol"""
        pass

    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate position size based on risk management principles
        As a professional trader, I use the following approach:
        1. Determine risk amount (percentage of portfolio value based on strategy risk_per_trade)
        2. Calculate risk per share (entry_price - stop_loss_price)
        3. Position size = risk_amount / risk_per_share
        :param entry_price: Entry price of the stock
        :param stop_loss_price: Stop loss price for risk management
        :return: Calculated position size (number of shares)
        """

        if stop_loss_price >= entry_price:
            # Invalid stop loss (stop loss should be below entry price for long position)
            # Return a conservative position size based on available cash
            available_cash = self.portfolio.cash
            conservative_position = int(available_cash * 0.001 / entry_price) # 0.1% of available cash
            return max(100, conservative_position)

        # Calculate risk per share (absolute value to ensure positive number)
        risk_per_share = abs(entry_price - stop_loss_price)

        # Calculate risk amount (risk_per_trade percentage of current portfolio value)
        portfolio_value = self.portfolio.get_portfolio_value({})
        risk_amount = portfolio_value * self.risk_per_trade

        # Calculate position size based on risk management
        if risk_per_share > 0:
            position_size = int(risk_amount / risk_per_share)
            # Ensure position size is reasonable (at least 100 shares, max based on available cash)
            max_affordable = int(self.portfolio.cash * 0.25 / entry_price) # Max 25% of available cash for single position
            return max(100, min(position_size,max_affordable,10000)) # Minimum 100 shares, cap at 10000 or 25% cash
        else:
            # Fallback if risk_per_share calculation fails
            max_affordable = int(self.portfolio.cash * 0.01 / entry_price)
            return max(100, min(max_affordable,10000))  # Minimum 100 shares, cap at 10000

    def get_stop_loss_price(self, symbol, entry_price, data):
        """
        Determine stop loss price for a symbol based on technical analysis
        In a real implementation, this would be based on:
        - Support level
        - ATR
        - Recent swing lows
        - Moving averages
        :param symbol: The stock symbol
        :param entry_price: Entry price of the stock
        :param data: Market data for analysis
        :return: Calculated stop loss price
        """
        # Get company data for technical analysis
        company_data = data.get('company_data', {}).get(symbol)

        if company_data and len(company_data.company_data) >= 2:
            lastest_data = company_data.company_data[-1]
            # Use ATR for stop loss calculation if available
            atr = lastest_data.ATR_14
            if atr and atr > 0:
                # Set stop loss at 2x ATR below entry price for more conservative approach
                atr_stop = entry_price - (2.0 * atr)

                # Also consider swing low
                recent_data = company_data.company_data[-5:] # last 5 periods
                swing_lows = [d.price.low_price for d in recent_data]
                if swing_lows:
                    recent_swing_low = min(swing_lows)
                    # Ensure stop loss is below entry price but now too far
                    swing_stop = max(recent_swing_low, entry_price * 0.9) # At least 10% below entry

                    # Return the more conservative (lower) stop loss
                    return min(atr_stop, swing_stop)
                else:
                    return atr_stop

            # Fallback to recent swing low analysis
            recent_data = company_data.company_data[-5:] # Last 5 periods
            swing_lows = [d.price.low_price for d in recent_data]
            if swing_lows:
                recent_swing_low = min(swing_lows)
                # Ensure stop loss is below entry price but not too far
                stop_loss = max(recent_swing_low, entry_price * 0.9) # At least 10% below entry
                return stop_loss

        # Default fallback: 10% below entry price (more conservative)
        return entry_price * 0.90

    def get_confidence_level(self, symbol, data):
        """
        Determine confidence level for a symbol (0.5 to 2.0)
        Higher confidence = larger position size
        :param symbol:
        :param data:
        :return:
        """

        # Get company data for technical analysis
        company_data = data.get('company_data', {}).get(symbol)
        current_price = data.get('current_price', {}).get(symbol, 0)

        if not company_data or current_price <= 0 or len(company_data.company_data) < 2:
            return 1.0 # Default confidence level

        confidence = 1.0
        lastest_data = company_data.company_data[-1]
        previous_data = company_data.company_data[-2]

        # 1. volume confirmation (0.5 - 1.2)
        if lastest_data.volume > lastest_data.moving_average_20.ma_volume * 1.5:
            confidence *= 1.1 # High volume confirmation
        elif lastest_data.volume < lastest_data.moving_average_20.ma_volume * 0.8:
            confidence *= 0.9 # Lower volume confirmation

        # 2. Price action confirmation (0.9 - 1.1)
        # Check if close_price is in the upper half of the candle
        if lastest_data.price.close_price > (lastest_data.price.high_price + lastest_data.price.low_price) / 2:
            confidence *= 1.05 # Bullish price action

        # 3. RSI confirmation (0.8 - 1.2)
        if 50 <= lastest_data.RSI_14 <= 70:
            confidence *= 1.1 # RSI in bullish range
        elif lastest_data.RSI_14 > 70:
            confidence *= 0.9 # RSI overbought
        elif lastest_data.RSI_14 < 30:
            confidence *= 0.95 # RSI oversold (may reverse)

        # 4. Moving average confirmation (0.9 - 1.2)
        if lastest_data.price.close_price > lastest_data.moving_average_20.ma_price:
            confidence *= 1.05 # Price above 20-day MA
        if lastest_data.moving_average_10.ma_price > lastest_data.moving_average_20.ma_price:
            confidence *= 1.05 # 10-day MA above 20-day MA (bullish trend)

        # 5. volatility confirmation using ATR (0.8 - 1.2)
        if lastest_data.ATR_14 and lastest_data.ATR_14 > lastest_data.ATR_MA5:
            confidence *= 1.05 # Increasing volatility
        elif lastest_data.ATR_14 and lastest_data.ATR_14 < lastest_data.ATR_MA5 * 0.8:
            confidence *= 0.95 # Decreasing volatility

        # 6. Trend confirmation with ADX (1.0 - 1.3)
        if lastest_data.ADX_14.ADX and lastest_data.ADX_14.ADX > 25:
            # Strong trend
            if lastest_data.ADX_14.plus_DI and lastest_data.ADX_14.minus_DI:
                if lastest_data.ADX_14.plus_DI > lastest_data.ADX_14.minus_DI:
                    confidence *= 1.15 # Strong bullish trend
                else:
                    confidence *= 0.9 # Strong bearish trend
        elif lastest_data.ADX_14.ADX and lastest_data.ADX_14.ADX < 20:
            confidence *= 0.95 # Weak trend

        # Ensure confidence level stays within reasonable bounds
        return max(0.5,min(confidence, 2.0))

    def execute_trades(self, data, current_prices):
        """Execute trades based on strategy with professional position sizing"""
        # Add current prices to data for use in should_buy and sould_sell methods
        data_with_prices = data.copy()
        data_with_prices['current_prices'] = current_prices

        # Identify new symbols
        new_symbols = self.identify_symbols(data_with_prices)
        self.symbol = new_symbols

        # Check if we should sell any current positions
        # Check a copy of the keys to avoid modifying the dictionary during iteration
        position_to_check = list(self.portfolio.position.keys())
        for symbol in position_to_check:
            # Only sell if all condition in should_sell are met
            if self.should_sell(symbol, data_with_prices):
                # Sell at current price
                current_price = current_prices.get(symbol, 0)
                if current_price > 0:
                    print(f"[{self.name}] Selling {symbol} at {current_price:,.0f} VND")
                    self.portfolio.sell(symbol, current_price)

        # Check if we should buy any new symbols
        # Only buy if we haven't reached maximum positions
        current_positions = len(self.portfolio.position)
        available_slots = self.max_position - current_positions

        if new_symbols and self.portfolio.cash > 0 and available_slots > 0:
            # Limit new buys to available slots
            symbols_to_buy = [s for s in new_symbols if s not in self.portfolio.position]
            symbols_to_buy = symbols_to_buy[:available_slots]

            for symbol in symbols_to_buy:
                # Only buy if all conditions in should_buy are met
                if self.should_buy(symbol, data_with_prices):
                    current_price = current_prices.get(symbol, 0)
                    if current_price > 0:
                        # Determine stop loss price
                        stop_loss = self.get_stop_loss_price(symbol, current_price, data_with_prices)

                        # Calculate position size based on risk management
                        quantity = self.calculate_position_size(current_price, stop_loss)

                        # Adjust quantity based on confidence level
                        confidence = self.get_confidence_level(symbol, data_with_prices)
                        quantity = int(quantity * confidence)

                        # Ensure don't exceed available cash and implement position sizing limits
                        max_affordable = int(self.portfolio.cash * 0.25 / current_price) # Max 25% of available cash for single position
                        quantity = min(max_affordable, quantity, 10000) # Cap at 25% cash or 10000 shares, whichever is smaller

                        if quantity > 0:
                            # Final check to ensure don't exceed available cash
                            max_affordable_final = int(self.portfolio.cash / current_price)
                            quantity = min(quantity, max_affordable_final)

                            if quantity > 0:
                                cost = current_price * quantity
                                print(f"[{self.name}] Buying {quantity} shares of {symbol} at {current_price:,.0f} VND (Stop: {stop_loss:,.0f}) VND, Cost: {cost:,.0f} VND")
                                self.portfolio.buy(symbol, current_price, quantity)
                            else:
                                print(f"[{self.name}] Skipping {symbol} - insufficient funds")
                        else:
                            print(f"[{self.name}] Skipping {symbol} - position size calculation resulted in 0 shares")

    def get_report(self, current_prices):
        """Get strategy report"""
        return self.portfolio.get_portfolio_report(current_prices)