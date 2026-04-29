from src.enums.signal import Emplitude
from src.enums.trend import Trend
from src.enums.risk import RiskLevel

class AdvancedVolatilityFilter(object):
    def __init__(self):
        pass

    def volatility_regime_analysis(self, company_data_list, periods=20):
        """
        Advanced volatility regime analysis using multiple indicators
        Professional traders use this to determine if volatility is expanding or contracting
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (volatility_regime, volatility_trend, risk_level
        """
        if len(company_data_list) < periods:
            return Emplitude.Weak, Trend.Sideway, RiskLevel.HIGH

        recent_data = company_data_list[-periods:]

        # Calculate ATR-based volatility
        atr_values = [data.ATR_14 for data in recent_data if data.ATR_14 is not None]
        if not atr_values:
            return Emplitude.Weak, Trend.Sideway, RiskLevel.HIGH

        current_atr = atr_values[-1]
        avg_atr = sum(atr_values) / len(atr_values)
        atr_ratio = current_atr / avg_atr if avg_atr > 0 else 1

        # Calculate price-based volatility (standard deviation of returns)
        prices = [data.price.close_price for data in recent_data]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] > 0]

        if len(returns) < 2:
            return Emplitude.Weak, Trend.Sideway, RiskLevel.HIGH

        avg_return = sum(returns) / len(returns)
        variance = sum((r-avg_return)**2 for r in returns)
        std_dev = variance ** 0.5

        # Volatility regime classification
        if atr_ratio > 1.5 and std_dev > 0.003: # High volatility
            volatility_regime = Emplitude.Bulltrap
            risk_level = RiskLevel.HIGH
        elif atr_ratio < 0.7 and std_dev < 0.01: # Low volatility
            volatility_regime = Emplitude.Tight
            risk_level = RiskLevel.LOW
        else: # Moderate volatility
            volatility_regime = Emplitude.Good
            risk_level = RiskLevel.MEDIUM

        # Volatility trend
        if len(atr_values) >= 5:
            recent_avg = sum(atr_values[-5:]) / 5
            older_avg = sum(atr_values[-10:-5]) / 5 if len(atr_values) >= 10 else recent_avg
            if recent_avg > older_avg * 1.1:
                volatility_trend = Trend.Up # Volatility expanding
            elif recent_avg < older_avg * 0.9:
                volatility_trend = Trend.Down # Volatility contracting
            else:
                volatility_trend = Trend.Sideway # Stable volatility
        else:
            volatility_trend = Trend.Sideway

        return volatility_regime, volatility_trend, risk_level

    def volatility_contraction_expension(self, company_data_list, periods=30):
        """
        Identify volatility contraction and expansion phases
        Professional traders look for volatility contraction before breakouts
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (contraction_phase, expansion_phase, breakout_potential)
        """
        if len(company_data_list) < periods:
            return False, False, False

        # Calculate volatility for rolling windows
        window_size = 10
        volatility_history = []

        for i in range(window_size, len(company_data_list)):
            window_data = company_data_list[i-window_size:i]
            prices = [data.price.close_price for data in window_data]

            if len(prices) >= 2:
                returns = [(prices[j] - prices[j-1]) / prices[j-1] for j in range(1, len(prices)) if prices[j-1] > 0]
                if returns:
                    variance = sum((r - sum(returns) / len(returns)) ** 2 for r in returns) / len(returns)
                    std_dev = variance ** 0.5
                    volatility_history.append(std_dev)

        if len(volatility_history) < 5:
            return False, False, False

        # Check for contraction (declining volatility)
        recent_volatility = volatility_history[-5:]
        avg_recent = sum(recent_volatility) / len(recent_volatility)
        avg_older = sum(volatility_history[-10:-5]) / len(volatility_history[-10:-5]) if len(volatility_history) >= 10 else avg_recent

        contraction_phase = avg_recent < avg_older * 0.8
        expansion_phase = avg_recent > avg_older * 1.2

        # Breakout potential (low volatility + price consolidation)
        current_price = company_data_list[-1].price.close_price
        price_range = max([data.price.high_price for data in company_data_list[-5:]]) - min([data.price.low_price for data in company_data_list])
        normalized_range = price_range / current_price if current_price > 0 else 0

        breakout_potential = contraction_phase and normalized_range < 0.02 # Less than 2% range in consolidation

        return contraction_phase, expansion_phase, breakout_potential

    def volatility_mean_reversion(self, company_data_list, periods=20):
        """
        Identify mean reversion opportunities based on volatility
        Professional traders use this for contrarian strategies
        :param company_data_list: List of company data
        :param periods: Number of periods to analyze
        :return: Tuple of (mean_reversion_signal, strength, confidence)
        """
        if len(company_data_list) < periods:
            return Trend.Sideway, 0, 0

        recent_data = company_data_list[-periods:]
        prices = [data.price.close_price for data in recent_data]

        # Calculate Bollinger Bands
        if len(prices) >= 20:
            ma20 = sum(prices[-20:]) / 20
            bb_std = sum((p - ma20) ** 2 for p in prices[-20:]) / 20
            bb_std = bb_std ** 0.5

            upper_band = ma20 + (2 * bb_std)
            lower_band = ma20 - (2 * bb_std)

            current_price = prices[-1]

            # Bollinger Band positioning
            if current_price > upper_band:
                # Overbought - potential mean reversion to downside
                distance_from_upper = (current_price - upper_band) / current_price
                strength = min(distance_from_upper * 100, 100) # Cap at 100
                return Trend.Down, strength, 80 # 80% confidence
            elif current_price < lower_band:
                # Oversold - potential mean reversion to upside
                distance_from_lower = (lower_band - current_price) / current_price
                strength = min(distance_from_lower * 100, 100)  # Cap at 100
                return Trend.Up, strength, 80 # 80% confidence

        # Check for extreme volatility levels
        atr_values = [data.ATR_14 for data in recent_data if data.ATR_14 is not None]
        if atr_values and len(atr_values) >= 10:
            current_atr = atr_values[-1]
            avg_atr = sum(atr_values[-10:]) / 10

            if current_atr > avg_atr * 2:
                # Extremely high volatility - potential reversion
                return Trend.Sideway, 90, 70 # 70% confidence

        return Trend.Sideway, 0, 0

    def volatility_risk_adjusttment(self, company_data_list, position_size, account_value):
        """
        Adjust position sizing based on current volatility
        Professional risk management technique
        :param company_data_list: List of company
        :param position_size: Current position size
        :param account_value: Total account value
        :return: Tuple of (adjusted_size, risk_level, recommendation)
        """
        if len(company_data_list) < 10:
            return position_size, RiskLevel.MEDIUM, "HOLD"

        current_data = company_data_list[-1]
        recent_data = company_data_list[-10]

        # Calculate current volatility risk
        atr_values = [data.ATR_14 for data in recent_data if data.ATR_14 is not None]
        if not atr_values:
            return position_size, RiskLevel.MEDIUM, "HOLD"

        current_atr = atr_values[-1]
        avg_atr = sum(atr_values) / len(atr_values)
        atr_ratio = current_atr / avg_atr if avg_atr > 0 else 1

        current_price = current_data.price.close_price
        volatility_percentage = (current_atr / current_price * 100) if current_price > 0 else 0

        # Risk adjustment based on volatility
        if atr_ratio > 1.5 or volatility_percentage > 3: # High volatility
            adjusted_size = position_size * 0.5 # Reduce position by 50%
            risk_level = RiskLevel.HIGH
            recommendation = "REDUCE"
        elif atr_ratio < 0.8 or volatility_percentage < 1: # Low volatility
            adjusted_size = position_size * 1.2 # Increase position by 20%
            risk_level = RiskLevel.LOW
            recommendation = "INCREASE"
        else: # Moderate volatility
            adjusted_size = position_size
            risk_level = RiskLevel.MEDIUM
            recommendation = "HOLD"

        # Ensure position size doesn't exceed account limits
        max_position_value = account_value * 0.02 # Max 2% of account per postion
        current_position_value = current_price * adjusted_size
        if current_position_value > max_position_value:
            adjusted_size = max_position_value / current_price
            recommendation = "REDUCE" if recommendation != "REDUCE" else recommendation

        return adjusted_size, risk_level, recommendation

    def volatility_breakout_confirmation(self, company_data_list, company_data_current):
        """
        Confirm breakouts using volatility analysis
        Professional traders use this to avoid false breakouts
        :param company_data_list: List of historical company data
        :param company_data_current: Current company data
        :return: Tuple of (breakout_confirmed, direction, quality)
        """
        if len(company_data_list) < 20:
            return False, Trend.Sideway, 0

        recent_data = company_data_list[-20:]
        prices = [data.price.close_price for data in recent_data]

        if len(prices) < 20:
            return False, Trend.Sideway, 0

        # Calculate support/resistance levels
        high_20 = max([data.price.high_price for data in recent_data])
        low_20 = max([data.price.low_price for data in recent_data])
        range_20 = high_20 - low_20

        current_price = company_data_current.price.close_price
        previous_price = company_data_current[-2].price.close_price

        # Check for breakout
        upper_breakout = current_price > high_20 and previous_price <= high_20
        lower_breakout = current_price < low_20 and previous_price >= low_20

        if not (upper_breakout or lower_breakout):
            return False, Trend.Sideway, 0

        # Confirm breakout with volatility
        atr_values = [data.ATR_14 for data in recent_data if data.ATR_14 is not None]
        if not atr_values:
            return False, Trend.Sideway, 0

        avg_atr = sum(atr_values) / len(atr_values)

        # Breakout quality based on ATR
        if upper_breakout:
            breakout_strength = (current_price - high_20) / avg_atr if avg_atr > 0 else 0
            direction = Trend.Up
        else: # lower_breakout
            breakout_strength = (low_20 - current_price) / avg_atr if avg_atr > 0 else 0

        # Volume confirmation
        current_volume = company_data_current.volume
        avg_volume = sum([data.volume for data in recent_data[-10:]]) / 10

        volume_confirmation = current_volume > avg_volume * 1.5

        # Quality score (0-100)
        quality = min(breakout_strength * 20, 100) # Cap at 100
        if volume_confirmation:
            quality = min(quality * 1.3, 100) # Boost quality with volume confirmation

        breakout_confirmation = quality > 60 and volume_confirmation
        return breakout_confirmation, direction, quality