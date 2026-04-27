from src.enums.trend import Trend
from src.enums.signal import Signal

class MomentumFilter:
    def __init__(self):
        pass

    def price_momentum(self, company_data_list, periods=5):
        """
        Check price momentum over a specified period
        :param company_data_list: List of company data
        :param periods: Number of periods to calculate momentum
        :return: Trend enum value
        """
        if len(company_data_list) < periods:
            return Trend.Neutral

        # Get the closing prices for the specified periods
        closing_prices = [data.price.close_price for data in company_data_list[-periods:]]

        # Calculate momentum as the percentage change from first to last price
        momentum = (closing_prices[-1] - closing_prices[0]) / closing_prices[0] * 100

        # Define thresholds for strong momentum
        if momentum > 5: # 5% positive momentum
            return Trend.Strong_Up
        elif momentum > 2: # 2% positive momentum
            return Trend.Up
        elif momentum < -5: # 5% negative momentum
            return Trend.Down
        else:
            return Trend.Neutral

    def rsi_momentum(self, company_data, overbought=70, oversold=30):
        """
        Check RSI momentum to identify overbought/oversold conditions
        :param company_data: Company data for current period
        :param overbought: RSI level considered overbought
        :param oversold: RSI level considered oversold
        :return: Signal enum value
        """
        if company_data.RSI_14 is None:
            return Signal.HOLD

        if company_data.RSI_14 > overbought:
            return Signal.SELL # Overbought, potential reversal
        elif company_data.RSI_14 < oversold:
            return Signal.BUY # Oversold, potential reversal
        else:
            return Signal.HOLD # Neutral

    def macd_momentum(self, company_data_list, short_period=12, long_period=26, signal_period=9):
        """
        Check MACD momentum to identify trend changes
        :param company_data_list: List of company data
        :param short_period: Short EMA period
        :param long_period: Long EMA period
        :param signal_period: Signal line period
        :return: Signal enum value
        """
        if len(company_data_list) < max(short_period, long_period, signal_period):
            return Signal.HOLD

        # Get recent closing prices
        closing_prices = [data.price.close_price for data in company_data_list[-long_period:]]

        # Calculate EMAs
        short_ema = self._calculate_ema(closing_prices[-short_period:], short_period)
        long_ema = self._calculate_ema(closing_prices, long_period)

        # Calculate MACD line
        macd_line = short_ema - long_ema

        # Calculate signal line (EMA of MACD line)
        # For simplicity, use the current MACD value from company_data
        signal_line = company_data_list[-1].MACD.signal if company_data_list[-1].MACD.signal else 0

        # Calculate MACD histogram
        histogram = macd_line - signal_line

        # Check for bullish/bearish crossover
        if macd_line > signal_line and company_data_list[-2].MACD.MACD < company_data_list[-2].MACD.signal:
            return Signal.BUY # Bullish crossover
        elif macd_line < signal_line and company_data_list[-2].MACD.MACD > company_data_list[-2].MACD.signal:
            return Signal.SELL
        else:
            return Signal.HOLD

    def _calculate_ema(self, prices, period):
        """
        Calculate exponential Moving Average
        :param prices: List of prices
        :param period: EMA period
        :return: EMA value
        """
        if len(prices) < period:
            return 0

        # Calculate smoothing factor
        multiplier = 2 / (period + 1)

        # Calculate simple moving average for the first value
        sma = sum(prices[:period]) / period

        # Calculate EMA
        ema = sma
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def moving_average_trend(self, company_data, ma_periods=[10, 20, 50]):
        """
        Check trend based on moving average alignment
        :param company_data: Company data for current period
        :param ma_periods: List of moving average periods to check
        :return: Trend enum value
        """
        # Get current prie
        current_price = company_data.price.close_price

        # Get moving averages (simplified - assuming they exist in company_data)
        ma_values = []
        if 10 in ma_periods and company_data.moving_average_10.ma_price:
            ma_values.append(company_data.moving_average_10.ma_price)
        if 20 in ma_periods and company_data.moving_average_20.ma_price:
            ma_values.append(company_data.moving_average_20.ma_price)
        if 50 in ma_periods and company_data.moving_average_50.ma_price:
            ma_values.append(company_data.moving_average_50.ma_price)

        # Check if we have all required moving averages
        if len(ma_values) < len(ma_periods):
            return Trend.Neutral

        # Check if moving averages are aligned (ascending order)
        if all(ma_values[i] <= ma_values[i + 1] for i in range(len(ma_values) - 1)):
            # All MAs are ascending and price is above them
            if current_price > max(ma_values):
                return Trend.Strong_Up
            elif current_price > min(ma_values):
                return Trend.Up
        elif all(ma_values[i] >= ma_values[i+1] for i in range(len(ma_values) - 1)):
            # All MAs are descending and price is below them
            if current_price < min(ma_values):
                return Trend.Strong_Down
            elif current_price < max(ma_values):
                return Trend.Down

        return Trend.Neutral












