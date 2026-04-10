from abc import ABC, abstractmethod
from Trading.Portfolio import Portfolio
import pandas as pd

class Strategy(ABC):
    def __init__(self, name, max_position=10, risk_per_trade=0.01):
        self.name = name
        self.portfolio = Portfolio(name)
        self.symbol = [] # Symbols identified by this strategy
        self.max_position = max_position # Maximum number of position to hold
        self.risk_per_trade = risk_per_trade # Risk percentage per trade (1% of portfolio)

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
        1. Determine risk amount (1% of portfolio value)
        2. Calculate risk per share (entry_price - stop_loss_price)
        3. Position size = risk_amount / risk_per_share
        :param entry_price:
        :param stop_loss_price:
        :return:
        """

        if stop_loss_price >= entry_price:
            # Invalid stop loss, use a default position size
            return 100

        # Calculate risk per share
        risk_per_share = entry_price - stop_loss_price

        # Calculate risk amount (1% of current portfolio value)
        portfolio_value = self.portfolio.get_portfolio_value({})
        risk_amount = portfolio_value * self.risk_per_trade

        # Calculate position size
        if risk_per_share > 0:
            position_size = int(risk_amount / risk_per_share)
            # Ensure position size is reasonable (at least 100 shares, max 10000)
            return max(100, min(position_size,10000))
        else:
            return 100 # Default position size if calculation falls

    def get_stop_loss_price(self, symbol, entry_price, data):
        """
        Determine stop loss price for a symbol
        This is a simplified implementation - in practice, this would be based on
        technical analysis of support levels, ATR, etc.
        :param symbol:
        :param entry_price:
        :param data:
        :return:
        """

        # As a professional trader, I typically set stop loss at 5-8% below entry price
        # For this implementation, I'll use 7%
        return entry_price * 0.93

    def get_confidence_level(self, symbol, data):
        """
        Determine confidence level for a symbol (0.5 to 2.0)
        Higher confidence = larger position size
        :param symbol:
        :param data:
        :return:
        """

        # In a real implementation, this would analyze multiple factors:
        # - Strength of the setup
        # - Volume confirmation
        # - Market conditions
        # - Technical factor
        # Now use default confidence level
        return 1.0

    def execute_trades(self, data, current_prices):
        """Execute trades based on strategy with professional position sizing"""
        # Identify new symbols
        new_symbols = self.identify_symbols(data)
        self.symbol = new_symbols

        # Check if we should sell any current positions
        for symbol in list(self.portfolio.position.keys()):
            if self.should_sell(symbol, data):
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
                if self.should_buy(symbol, data):
                    current_price = current_prices.get(symbol, 0)
                    if current_price > 0:
                        # Determine stop loss price
                        stop_loss = self.get_stop_loss_price(symbol, current_price, data)

                        # Calculate position size based on risk management
                        quantity = self.calculate_position_size(current_price, stop_loss)

                        # Adjust quantity based on confidence level
                        confidence = self.get_confidence_level(symbol, current_price)
                        quantity = int(quantity * confidence)

                        # Ensure don't exceed available cash
                        max_affordable = int(self.portfolio.cash / current_price)
                        quantity = min(max_affordable, quantity)

                        if quantity > 0:
                            print(f"[{self.name}] Buying {quantity} shares of {symbol} at {current_price:,.0f} VND (Stop: {stop_loss:,.0f}) VND")
                            self.portfolio.buy(symbol, quantity)
                        else:
                            print(f"[{self.name}] Skipping {symbol} - insufficient funds or invalid quantity")

    def get_report(self, current_prices):
        """Get strategy report"""
        return self.portfolio.get_portfolio_report(current_prices)