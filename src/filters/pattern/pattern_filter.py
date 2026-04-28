from src.enums.signal import Signal
from src.enums.trend import Trend

class PatternFilter:
    def __init__(self):
        pass

    def is_harmer(self, company_data, lower_wick_ratio=0.6, body_ratio=0.3):
        """
        Identify harmer candlestick patter
        :param company_data: Company data for current period
        :param lower_wick_ratio: Minimum ratio of lower wick to total range
        :param body_ratio: Maximum ratio of body to total range
        :return:Boolean indicating if pattern is present
        """
        open_price = company_data.open_price
        high_price = company_data.high_price
        low_price = company_data.low_price
        close_price = company_data.close_price

        total_range = high_price - low_price
        body_size = abs(close_price - open_price)
        lower_wick = min(open_price, close_price) - low_price
        upper_wick = high_price - max(open_price, close_price)

        # Check if it's a harmer pattern (long lower wick, small body, small upper wick
        if total_range > 0:
            return (lower_wick / total_range >= lower_wick_ratio and body_size / total_range <= body_ratio and
                    upper_wick / total_range <= body_ratio and
                    close_price > open_price) # Bullish close
        return False

    def is_shooting_star(self, company_data, upper_wick_ratio=0.6, body_ratio=0.3):
        """
        Identify shooting star candlestick pattern
        :param company_data: Company data for current period
        :param upper_wick_ratio: Minimum ratio of upper wck to total range
        :param body_ratio: Maximum ratio of body to total range
        :return: Boolean indicating if pattern is present
        """
        open_price = company_data.open_price
        high_price = company_data.high_price
        low_price = company_data.low_price
        close_price = company_data.close_price

        total_range = high_price - low_price
        body_size = abs(close_price - open_price)
        lower_wick = min(open_price, close_price) - low_price
        upper_wick = high_price - max(open_price, close_price)

        # Check if it's a shooting star pattern (long upper wick, small body, small lower wick)
        if total_range > 0:
            return (upper_wick / total_range >= upper_wick_ratio and
                    body_size / total_range <= body_ratio and
                    lower_wick / total_range <= body_ratio and
                    close_price < open_price) # Bearish close
        return False

    def is_engulfing(self, company_data_current, company_data_previous):
        """
        Identify engulfing candlestick pattern
        :param company_data_current:Current company data
        :param company_data_previous: Previous company data
        :return: Tuple of (is_bullish_engulfing, is_bearish_engulfing)
        """
        current_open = company_data_current.price.open_price
        current_close = company_data_current.price.close_price
        previous_open = company_data_previous.price.open_price
        previous_close = company_data_previous.price.close_price

        # Bullish engulfing: current candle completely engulfs previous bearish candle
        bullish_engulfing = (current_close > current_open and
                             previous_close < previous_open and
                             current_close > previous_open and
                             current_open < previous_open)

        # Bearish engulfing: current candle completely engulfs previous bullish candle
        bearish_engulfing = (current_close < current_open and
                             previous_close > previous_open and
                             current_close < previous_open and
                             current_open > previous_open)
        return bullish_engulfing, bearish_engulfing

    def is_there_white_soldiers(self, company_data_list):
        """
        Identify three white soldiers pattern
        :param company_data_list: List of company data (last 3 periods)
        :return: Boolean indicating if pattern is present
        """
        if len(company_data_list) < 3:
            return False

        # Check if all three candles are bullish and show upward progression
        for i in range(3):
            data = company_data_list[-(3-i)]
            if data.price.close_price <= data.price.open_price: # Not bullish
                return False

        # Check if each candle opens within or higher than previous candle's body and closes higher than previous candle
        for i in range(1, 3):
            current = company_data_list[-(3-i)]
            previous = company_data_list[-(3-i+1)]

            if (current.price.open_price < previous.price.open_price or
            current.price.open_price > previous.price.close_price or
            current.price.close_price <= previous.price.close_price):
                return False
        return True

    def is_threee_black_crows(self, company_data_list):
        """
        Identify three black crows pattern
        :param company_data_list: List of company data (last 3 periods)
        :return: Boolean indicating if pattern is present
        """
        if len(company_data_list) < 3:
            return False

        # Check if all three candles are bearish and show downward progression
        for i in range(3):
            data = company_data_list[-(3-i)]
            if data.price.close_price >= data.price.open_price: # Not bearish
                return False

        # Check if each candle opens within or lower than previous candle's body and closes lower than previous candle
        for i in range(1, 3):
            current = company_data_list[-(3-i)]
            previous = company_data_list[-(3-i+1)]
            if (current.price.open_price > previous.price.open_price or
            current.price.open_price < previous.price.close_price or
            current.price.close_price >= previous.price.close_price):
                return False

        return True

    def pattern_analysis(self, company_data_list):
        """
        Comprehensive pattern analysis
        :param company_data_list: List of company data
        :return: Signal enum value
        """
        if len(company_data_list) < 3:
            return Signal.HOLD

        current_data = company_data_list[-1]
        previous_data = company_data_list[-2]

        # Check for hammer pattern (bullish reversal)
        if self.is_harmer(current_data):
            return Signal.BUY

        # Check for shooting star pattern (bearish reversal)
        if self.is_shooting_star(current_data):
            return Signal.SELL

        # Check for engulfing patterns
        if len(company_data_list) >= 2:
            bullish_engulfing, bearish_engulfing = self.is_engulfing(current_data, previous_data)
            if bullish_engulfing:
                return Signal.BUY
            elif bearish_engulfing:
                return Signal.SELL

        # Check for three white soldiers (bullish continuation)
        if self.is_there_white_soldiers(company_data_list):
            return Signal.BUY

        # Check for three black crown (bearish continuation)
        if self.is_threee_black_crows(company_data_list):
            return Signal.SELL

        return Signal.HOLD