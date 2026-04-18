import numpy as np
from Model import Company
from Enum.trend import Trend

class SupportResistanceFilter:
    def __init__(self):
        pass

    def find_support_levels(self, company_data_list, num_periods= 20):
        """
        Find support levels from price data over a period of time.
        :param company_data_list:
        :param num_periods:
        :return:
        """
        if len(company_data_list) < num_periods:
            return []

        # Retrieve the lowest price data within the most recent num_periods.
        recent_data = company_data_list[-num_periods:]
        lows = [data.price.low for data in recent_data]

        # Sort by lowest price to find potential support.
        lows.sort()

        # Find support levels by identifying price zones that have been touched multiple times.
        support_levels = []
        for i in range(len(lows)):
            # Check if the current price is close to the previous price (within a 1.5% range).
            if i > 0 and abs(lows[i] - lows[i - 1]) < lows[i] * 0.015:
                # If no nearby support level is listed, add it to the list.
                if not any(abs(level - lows[i]) < level * 0.015 for level in support_levels):
                    support_levels.append(lows[i])

        return support_levels

    def find_registance_levels(self, company_data_list, num_periods= 20):
        """
        Find resistance levels from price data over a period of time.
        :param company_data_list:
        :param num_periods:
        :return:
        """
        if len(company_data_list) < num_periods:
            return []

        # Retrieve the highest price data within the most recent num_periods.
        recent_data = company_data_list[-num_periods:]
        highs = [data.price.high_price for data in recent_data]

        # Sort the highest prices to find potential resistance levels.
        highs.sort()

        # Find resistance levels by identifying areas where prices have been touched multiple times.
        resistance_levels = []
        for i in range(len(highs)):
            # Check if the current price is close to the previous price (within a 1.5% range).
            if i > 0 and abs(highs[i] - highs[i - 1]) < highs[i] * 0.015:
                # If there are no nearby resistance levels, add to the list.
                if not any(abs(level - highs[i]) < level * 0.015 for level in resistance_levels):
                    resistance_levels.append(highs[i])

        return resistance_levels

    def is_near_support(self, current_price, support_levels, threshold=0.02):
        """
        Check if the current price is close to the support level.
        :param current_price:
        :param support_levels:
        :param threshold:
        :return:
        """
        for support in support_levels:
            if abs(current_price - support) < support <= threshold:
                return True
        return False

    def is_near_resistance(self, current_price, resistance_levels, threshold=0.02):
        """
        Check if the current price is close to the resistance level.
        :param current_price:
        :param support_levels:
        :param threshold:
        :return:
        """
        for resistance in resistance_levels:
            if abs(current_price - resistance) / resistance <= threshold:
                return True
        return False

    def check_support_bounce(self, company_data_list, current_data):
        """
        Check for the signal bouncing up from the support level.
        :param company_data_list:
        :param current_data:
        :return:
        """
        support_levels = self.find_support_levels(company_data_list)
        current_price = current_data.price.close_price
        previous_data = company_data_list[-2] if len(company_data_list) >= 2 else None

        if not previous_data:
            return Trend.Sideway

        previous_price = previous_data.price.close_price

        # Check if the previous price was below the support level and the current price is above the support level.
        for support in support_levels:
            if previous_price < support and current_price > support:
                # Check further if the current price has a bullish candle.
                if current_price > current_data.price.open_price:
                    return Trend.Up

        return Trend.Sideway

    def check_resistance_break(self, company_data_list, current_data):
        """
        Check for breakout signals at resistance levels.
        :param company_data_list:
        :param current_data:
        :return:
        """
        resistance_levels = self.find_support_levels(company_data_list)
        current_price = current_data.price.close_price
        previous_data = company_data_list[-2] if len(company_data_list) >= 2 else None

        if not previous_data:
            return Trend.Sideway

        previous_price = previous_data.price.close_price

        # Check if the previous price was below the resistance level and the current price is above the resistance level.
        for resistance in resistance_levels:
            if previous_price < resistance and current_price > resistance:
                # Check for further volume increase to confirm the breakout.
                if current_data.volume > current_data.moving_average_20.ma_volume * 1.2:
                    return Trend.Up

        return Trend.Sideway

    def check_support_resistance_strength(self, company_data_list, level, num_periods=20):
        """
        Assess the strength of support/resistance levels based on the number of touches.
        :param company_data_list:
        :param level:
        :param num_periods:
        :return:
        """
        if len(company_data_list) < num_periods:
            return 0

        touch_count = 0
        recent_data = company_data_list[-num_periods:]

        # Count the number of times the price touches near the support/resistance level (within a 1% range).
        for data in recent_data:
            low = data.price.low_price
            high = data.price.high_price

            if abs(low - level) / level <= 0.01 or abs(high - level) / level <= 0.01:
                touch_count += 1

        return touch_count

    def get_support_resistance_zone(self, company_data_list, current_price, zone_threshold= 0.03):
        """
        Identify the nearest support/resistance zone.
        :param company_data_list:
        :param current_price:
        :param zone_threshold:
        :return:
        """
        support_levels = self.find_support_levels(company_data_list)
        resistance_levels = self.find_registance_levels(company_data_list)

        # Find the nearest support level below.
        nearest_support = None
        for support in sorted(support_levels, reverse=True):
            if support < current_price:
                nearest_support = support
                break

        # Find the nearest resistance level above.
        nearest_resistance = None
        for resistance in sorted(resistance_levels):
            if resistance > current_price:
                nearest_resistance = resistance
                break

        return {
            'support': nearest_support,
            'resistance': nearest_resistance,
            'distance_to_support': (current_price - nearest_support) / nearest_support if nearest_support else None,
            'distance_to_resistance': (nearest_resistance - current_price) / current_price if nearest_resistance else None
        }