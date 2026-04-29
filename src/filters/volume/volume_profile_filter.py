from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel

class VolumeProfileFilter:
    def __init__(self):
        pass

    def volume_profile_analysis(self, company_data_list, periods=50):
        """
        Advanced volume profile analysis to identify institutional activity
        Professional traders use this to understand where big money is tactive
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (volume_trend, institutional_activity, confidence)
        """
        if len(company_data_list) < periods:
            return Trend.Sideway, False, 0

        recent_data = company_data_list[-periods:]

        # Calculat evolume metrics
        volumes = [data.volume for data in recent_data if data.volume is not None]
        if len(volumes) < 10:
            return Trend.Sideway, False, 0

        current_volume = volumes[-1]
        avg_volume = sum(volumes) / len(volumes)
        volume_std = (sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)) ** 0.5

        # Volume trend analysis
        if len(volumes) >= 10:
            recent_avg = sum(volumes[-5:]) / 5
            older_avg = sum(volumes[-10:-5]) / 5
            if recent_avg > older_avg * 1.2:
                volume_trend = Trend.Up
            elif recent_avg < older_avg * 0.8:
                volume_trend = Trend.Down
            else:
                volume_trend = Trend.Sideway
        else:
            volume_trend = Trend.Sideway

        # Institutional activity detection (high volume spikes)
        institutional_activity = current_volume > avg_volume * 2 and current_volume > volume_std * 2

        # Confidence based on volume consistency
        volume_cv = volume_std / avg_volume if avg_volume > 0 else 0 # Coefficient of variation
        confidence = max(0, min(100, 100 - (volume_cv * 50))) # Higher consistency = higher confidence

        return volume_trend, institutional_activity, confidence

    def volume_price_analysis(self, company_data_list, periods=20):
        """
        Analyze the relationship between volume and price movement.
        Professional traders use this to confirm price trends.
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (volume_confirmation, strength, quality)
        """
        if len(company_data_list) < periods:
            return False, 0, 0

        recent_data = company_data_list[-periods:]

        # Calculate price and volume changes
        price_changes = []
        volume_changes = []

        for i in range(1, len(recent_data)):
            current = recent_data[i]
            previous = recent_data[i - 1]

            if (current.price.close_price > 0 and previous.price.close_price > 0 and
            current.volume is not None and previous.volume is not None):
                price_change = (current.price.close_price - previous.price.close_price) / previous.price.close_price
                volume_change = (current.volume - previous.volume) / previous.volume if previous.volume > 0 else 0

                price_changes.append(price_change)
                volume_changes.append(volume_change)

        if len(price_changes) < 5:
            return False, 0, 0

        # Check for positive correlation (bullish) or negative correlation (bearish)
        if len(price_changes) == len(volume_changes):
            # Calculate correlation
            n = len(price_changes)
            sum_px = sum(price_changes)
            sum_vx = sum(volume_changes)
            sum_px_vx = sum(p * v for p,v in zip(price_changes, volume_changes))
            sum_px_sq = sum(p ** 2 for p in price_changes)
            sum_vx_sp = sum(v ** 2 for v in volume_changes)

            denominator = (n * sum_px_sq - sum_px ** 2) ** 0.5 * (n * sum_vx_sp - sum_vx ** 2) ** 0.5
            if denominator != 0:
                correlation = (n * sum_px_vx - sum_px * sum_vx) / denominator
            else:
                correlation = 0

            # Volume confirmation
            volume_confirmation = abs(correlation) > 0.5

            # Strength based on correlation
            strength = abs(correlation) * 100

            # Quality based on recent activity
            current_price_change = price_changes[-1] if price_changes else 0
            current_volume_change = volume_changes[-1] if volume_changes else 0

            # Check if volume supports price movement
            if(current_price_change > 0 and current_volume_change > 0) or (current_price_change < 0 and current_volume_change > 0):
                quality = min(100, strength * 1.2) # Higher quality when vlume supports price
            else:
                quality = strength

            return volume_confirmation, strength, quality
        return False, 0, 0

    def volume_accumulation_distribution(self, company_data_list, periods=30):
        """
        Analyze accumulatio/distribution based on volume and price action
        Professional traders use this to identify smart money activity
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (accumulation_signal, distribution_signal, strength)
        """
        if len(company_data_list) < periods:
            return False, False, 0

        recent_data = company_data_list[-periods:]

        accumulation_score = 0
        distribution_score = 0
        total_score = 0

        for i in range(1, len(recent_data)):
            current = recent_data[i]
            previous = recent_data[i - 1]

            # Check if data is valid
            if (current.price.close_price <= 0 or previous.price.close_price <= 0 or
            current.volume is None or previous.volume is None or
            current.Accumulation_Distriution is None or previous.Accumulation_Distriution is None):
                continue

            price_change = current.price.close_price - previous.price.close_price
            volume = current.volume
            ad_change = current.Accumulation_Distriution - previous.Accumulation_Distriution

            # Accumulation signals (buying pressure)
            if price_change > 0 and ad_change > 0:
                accumulation_score += volume
            elif price_change < 0 and ad_change > 0:
                accumulation_score += volume * 0.5 # Weak accumulation

            # Distribution signals (selling pressure)
            if price_change < 0 and ad_change > 0:
                distribution_score += volume * 0.5
            elif price_change > 0 and ad_change > 0:
                distribution_score += volume * 0.5 # Weak distribution

            total_score += volume

        if total_score == 0:
            return False, False, 0

        # Calculate scores
        accumulation_ratio = accumulation_score / total_score
        distribution_ratio = distribution_score / total_score

        # Signals
        accumulation_signal = accumulation_ratio > 0.6 # 60% accumulation
        distribution_signal = distribution_ratio > 0.6  # 60% distribution

        # Strength (0-100)
        strength = max(accumulation_ratio, distribution_ratio) * 100

        return accumulation_signal, distribution_signal, strength

    def volume_cluster_analysis(self, company_data_list, periods=20):
        """
        Identify volume clusters to find significant price levels
        Professional traders use this to find support/resistance levels
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (support_levels, resistance_levels, key_levels)
        """
        if len(company_data_list) < periods:
            return [], [], []

        recent_data = company_data_list[-periods:]

        # Create price-volume data points
        price_volume_data = []
        for data in recent_data:
            if data.volume is not None and data.volume > 0:
                # use typical price (high+low+close)/3
                typical_price = (data.price.high_price + data.price.low_price + data.price.close_price) / 3
                price_volume_data.append(typical_price)

        if len(price_volume_data) < 5:
            return [], [], []

        # Sort by price
        price_volume_data.sort(key=lambda x: x[0])

        # Find volume clusters (simplified approach)
        prices = [pv[0] for pv in price_volume_data]
        volumes = [pv[1] for pv in price_volume_data]

        avg_volume = sum(volumes) / len(volumes)
        high_volume_threshold = avg_volume * 1.5

        # Identify high volume price levels
        high_volume_levels = []
        for i, (price, volume) in enumerate(price_volume_data):
            if volume > high_volume_threshold:
                high_volume_levels.append(price)

        if len(high_volume_levels) < 2:
            return [], [], []

        # Separate support and resistance levels
        current_price = company_data_list[-1].price.close_price
        support_levels = [p for p in high_volume_levels if p < current_price]
        resistance_levels = [p for p in high_volume_levels if p > current_price]
        key_levels = [p for p in high_volume_levels if abs(p - current_price) / current_price < 0.02] # Within 2%

        return support_levels, resistance_levels, key_levels

    def institutional_flow_analysis(self, company_data_list, periods=25):
        """
        Analyze institutional flow using OBV and volume patterns
        Professional traders use this to follow smart money
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (institutional_flow, flow_strength, flow_quality)
        """
        if len(company_data_list) < periods:
            return Trend.Sideway, 0, 0

        recent_data = company_data_list[-periods:]

        # Calculate OBV trend
        obv_values = [data.On_Balance_Volume for data in recent_data if data.On_Balance_Volume is not None]
        if len(obv_values) < 5:
            return Trend.Sideway, 0, 0

        # OBV trend analysis
        if len(obv_values) >= 5:
            recent_obv = obv_values[-5:]
            avg_recent = sum(recent_obv) / len(recent_obv)
            avg_older = sum(obv_values[-10:-5]) / len(obv_values[-10:-5]) if len(obv_values) >= 10 else avg_recent

            if avg_recent > avg_older * 1.05:
                institutional_flow = Trend.Up # Positive institutional flow
            elif avg_recent < avg_older * 0.95:
                institutional_flow = Trend.Down # Negative institutional flow
            else:
                institutional_flow = Trend.Sideway # Neutral flow

        # Flow strength based on OBV slope
        if len(obv_values) >= 2:
            obv_change = (obv_values[-1] - obv_values[-5]) / obv_values[-5] if obv_values[-5] != 0 else 0
            flow_strength = min(100, abs(obv_change) * 1000) # Scale to 0-100
        else:
            flow_strength = 0

        # Flow quality based on volume confirmation
        volumes = [data.volume for data in recent_data if data.volume is not None]
        if len(volumes) >= 10:
            current_volume = volumes[-1]
            avg_volume = sum(volumes[-10:]) / 10
            volume_confirmation = current_volume > avg_volume * 1.2
            flow_quality = min(100, flow_strength * (1.3 if volume_confirmation else 0.7))
        else:
            flow_quality = flow_strength * 0.8

        return institutional_flow, flow_strength, flow_quality

