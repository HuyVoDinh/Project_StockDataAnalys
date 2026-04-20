from src.enums.trend import Trend
from src.enums.signal import Emplitude

class PriceActionFilter:
    def __init__(self):
        pass

    def check_pin_bar(self, company_data):
        """
        Check for pin bars - strong reversal signals
        Pin bars have a small candle body and long upper/lower wicks.
        :param company_data:
        :return:
        """
        open_price = company_data.price.open_price
        high_price = company_data.price.high_price
        low_price = company_data.price.low_price
        close_price = company_data.price.close_price

        # Calculate the candle body and wick.
        body = abs(close_price - open_price)
        candle_range = high_price - low_price
        upper_wick = high_price - max(open_price, close_price)
        lower_wick = min(open_price, close_price) - low_price

        # Bullish pin bar (long lower wick, small candle body)
        if (lower_wick > body * 2 and lower_wick > candle_range * 0.6 and upper_wick < body):
            return Trend.Up
        elif (upper_wick > body * 2 and upper_wick > candle_range * 0.6 and lower_wick < body): # Bearish pin bar (long upper wick, small candle body)
            return Trend.Down
        return Trend.Sideway

    def check_engulfing_pattern(self, current_data, previous_data):
        """
        Checking the engulfing candlestick pattern - a signal of trend continuation.
        :param current_data:
        :param previous_data:
        :return:
        """
        curr_open = current_data.price.open_price
        curr_close = current_data.price.close_price
        prev_open = previous_data.price.open_price
        prev_close = previous_data.price.close_price

        # Bullish engulfing: A green candle engulfing the previous red candle.
        if (curr_close > curr_open and
            prev_close < prev_open and
            curr_close > prev_open and
            curr_open < prev_close):
            return Trend.Up
        # Bullish engulfing: a candlestick that breaks through the previous green candlestick.
        elif (curr_close < curr_open and
            prev_close > prev_open and
            curr_close < prev_open and
            curr_open > prev_close):
            return Trend.Down
        return Trend.Sideway

    def check_inside_bar(self, current_data, previous_data):
        """
        Check the inside bar pattern - accumulation signal
        The current candle is completely within the range of the previous candle
        :param current_data:
        :param previous_data:
        :return:
        """
        curr_high = current_data.price.high_price
        curr_low = current_data.price.low_price
        prev_high = previous_data.price.high_price
        prev_low = previous_data.price.low_price

        if curr_high < prev_high and curr_low > prev_low:
            return Emplitude.Tight # Inside bar - accumulation signal
        return Emplitude.Good

    def check_outside_bar(self, current_data, previous_data):
        """
        Check the outside bar pattern - a breakout signal.
        The current candle has broken out of the range of the previous candle.
        :param current_data:
        :param previous_data:
        :return:
        """
        curr_high = current_data.price.high_price
        curr_low = current_data.price.low_price
        prev_high = previous_data.price.high_price
        prev_low = previous_data.price.low_price

        if curr_high < prev_high and curr_low < prev_low:
            return Emplitude.Break # Outside bar - a breakout signal.
        return Emplitude.Good

    def check_doji(self, company_data):
        """
        Checking the doji candlestick - a signal of hesitation, a potential reversal
        The candlestick body is very small or absent.
        :param company_data:
        :return:
        """
        open_price = company_data.price.open_price
        close_price = company_data.price.close_price
        high_price = company_data.price.high_price
        low_price = company_data.price.low_price

        body = abs(close_price - open_price)
        candle_range = high_price - low_price

        # Doji: The candle body is less than 10% of the candle range.
        if body < candle_range * 0.1:
            # Doji with a long upper shadow - bearish
            upper_wick = high_price - max(open_price, close_price)
            lower_wick = min(open_price, close_price) - low_price
            if upper_wick > candle_range * 0.4:
                return Trend.Down
            # A doji has a long bottom shadow - bullish
            elif upper_wick > candle_range * 0.4:
                return Trend.Up
            # The perfect doji - hesitation
            else:
                return Trend.Sideway
        return Trend.Good

    def check_trend_continuation(self, current_data, previous_data):
        """
        Check for trend continuation signals
        :param current_data:
        :param previous_data:
        :return:
        """
        # Check if the closing price is in the same direction as the previous candle.
        if ((current_data.price.close_price > current_data.price.open_price) and
                (previous_data.price.close_price > previous_data.price.open_price)):
            return Trend.Up
        elif ((current_data.price.close_price < current_data.price.open_price) and
              (previous_data.price.close_price < previous_data.price.open_price)):
            return Trend.Down
        return Trend.Sideway