from Model import Company
from Enum.liquidity import Liquidity, Volume, Cash_Flow

class LiquidityFilter:
    def __init__(self):
        pass

    def check_minimum_liquidity(self, company_data, minimum_value=50):
        """
        Check minimum liquidity based on transaction value
        :param company_data:
        :param minimum_value:
        :return:
        """
        if company_data.trading_value > minimum_value:
            return Liquidity.Good
        return Liquidity.Weak

    def check_volume_trend(self, company_data_list, periods=5):
        """
        Check the volume trend in the short term.
        :param company_data_list:
        :param periods:
        :return:
        """
        if len(company_data_list) < periods:
            return Volume.Money_Out

        recent_data = company_data_list[-periods:]
        volumes = [data.volume for data in recent_data]

        # Calculate the average volume for the previous 3 periods and the 2 shortest periods.
        avg_previous = sum(volumes[:-2]) / (periods - 2) if periods > 2 else 0
        avg_recent = sum(volumes[-2:]) / 2 if len(volumes) >= 2 else 0

        if avg_recent > avg_previous * 1.1: # Volume increased by at least 10%.
            return Volume.Money_In
        elif avg_recent < avg_previous * 0.9: # Volume decreased by more than 10%.
            return Volume.Money_Out
        else:
            return Volume.Money_Out

    def check_smart_money(self, company_data, volume_ratio_threshold=1.5):
        """
        Check smart money flow based on the volume-to-MA20 ratio.
        :param company_data:
        :param volume_ratio_threshold:
        :return:
        """
        if company_data.volume == 0 or company_data.moving_average_20.ma_volume == 0:
            return Cash_Flow.Weak

        volume_ratio = company_data.volume / company_data.moving_average_20.ma_volume

        if volume_ratio > volume_ratio_threshold:
            return Cash_Flow.Smart_Money
        elif volume_ratio < 1.0:
            return Cash_Flow.Weak
        else:
            return Cash_Flow.Weak

    def check_volume_confirmation(self, company_data_list, volume_spike_threshold=2.0):
        """
        Check and confirm the volume spike.
        :param company_data_list:
        :param volume_spike_threshold:
        :return:
        """
        if len(company_data_list) < 3:
            return False

        current_data = company_data_list[-1]
        previous_data = company_data_list[-2]
        avg_previous = sum([data.volume for data in company_data_list[-5:-1]]) / 4 if len(company_data_list) >= 5 else previous_data.volume

        # Check if the current volume is unusually high compared to average.
        if current_data.volume > avg_previous * volume_spike_threshold:
            # Check if yesterday's volume was lower than average (cumulative).
            if previous_data.volume < avg_previous * 0.8:
                return True
        return False

    def check_liquidity_stability(self, company_data_list, periods=10):
        """
        Check the stability of liquidity.
        :param company_data_list:
        :param periods:
        :return:
        """
        if len(company_data_list) < periods:
            return Liquidity.Weak

        recent_data = company_data_list[-periods:]
        trading_values = [data.trading_value for data in recent_data]

        # Calculate the standard deviation of the transaction value.
        avg_value = sum(trading_values) / len(trading_values)
        variance = sum((value - avg_value) ** 2 for value in trading_values) / len(trading_values)
        std_dev = variance ** 0.5

        # If the standard deviation is less than 30% of the mean, it is considered stable.
        if std_dev < avg_value * 0.3:
            return Liquidity.Good
        else:
            return Liquidity.Weak

    def check_institutional_activity(self, company_data_list, periods=5):
        """
        Assess the activity of institutional investors through trading volume and value.
        :param company_data_list:
        :param periods:
        :return:
        """
        if len(company_data_list) < periods:
            return Cash_Flow.Weak

        recent_data = company_data_list[-periods:]

        # Check if there are multiple sessions with high volume and large transaction values.
        high_volume_days = 0
        for data in recent_data:
            if(data.volume > data.moving_average_20.ma_volume * 1.5 and data.trading_value > 100):
                high_volume_days += 1

        # If there are at least two sessions with high volume and large trading value.
        if high_volume_days >= 2:
            return Cash_Flow.Smart_Money
        else:
            return Cash_Flow.Weak
