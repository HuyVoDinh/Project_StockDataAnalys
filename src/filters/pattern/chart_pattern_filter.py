from tenacity.stop import stop_base

from src.enums.trend import Trend
from src.enums.signal import Signal

class ChartPatternFilter:
    def __init__(self):
        pass

    def detect_head_and_shoulder(self, price_data_list, periods=30):
        """
        Detect Head and Shoulders pattern for potential trend reversal
        Professional traders use this  classic reversal pattern.
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Tuple of (pattern_type, confidence, target_price, stop_loss)
        """
        if len(price_data_list) < periods:
            return "NONE", 0, 0, 0

        # Extract high and low prices
        highs = [data.price.high_price for data in price_data_list[-periods:]]
        lows = [data.price.low_price for data in price_data_list[-periods:]]
        closes = [data.price.close_price for data in price_data_list[-periods:]]

        if len(highs) < 10:
            return "NONE", 0, 0, 0

        # Look for Head and Shoulders pattern (bearish)
        # Pattern: Left Shoulder -> Head -> Right Shoulder -> Neckline Break
        pattern_confidence = 0
        left_shoulder_high = 0
        head_high = 0
        right_shoulder_high = 0
        neckline = 0

        # Simplified detection - in practice, this would be more sophisticated
        # Looking for 5 key points: L5_low, L5, high, Head_high, R5_high, R5_low, Neckline
        if len(highs) >= 10:
            # find potential shoulders and head
            left_shoulder_idx = len(highs) // 4
            head_idx = len(highs) // 2
            right_shoulder_idx = 3 * len(highs) // 4
            left_shoulder_high = highs[left_shoulder_idx]
            head_high = highs[head_idx]
            right_shoulder_high = highs[right_shoulder_idx]

            # Check if head is higher than shoulder
            if head_high > left_shoulder_high * 1.02 and head_high > right_shoulder_high * 1.02:
                # Check for neckline (support line connection lows)
                left_shoulder_low = lows[left_shoulder_idx]
                right_shoulder_low = lows[right_shoulder_idx]
                neckline = (left_shoulder_low + right_shoulder_low) / 2

                # Check if price has broken below neckline
                current_price = closes[-1]
                if current_price < neckline * 0.99: # 1% below neckline
                    pattern_confidence = 85
                    target_price = head_high - (head_high - neckline) # Measured move
                    stop_loss = head_high * 1.01 # Above head

                    return "HEAD_AND_SHOULDERS", pattern_confidence, target_price, stop_loss

        # Look for Inverse Head and Shoulders pattern (bullish)
        left_shoulder_low = 0
        head_low = 0
        right_shoulder_low = 0

        if len(lows) >= 10:
            left_shoulder_idx = len(lows) // 4
            head_idx = len(lows) // 2
            right_shoulder_idx = 3 * len(lows) // 4
            left_shoulder_low = lows[left_shoulder_idx]
            head_low = lows[head_idx]
            right_shoulder_low = lows[right_shoulder_idx]

            # Check if head is lower than shoulders
            if head_low < left_shoulder_low * 0.98 and head_low < right_shoulder_low * 0.98:
                # Check for neckline (resistance line connecting highs)
                left_shoulder_high = highs[left_shoulder_idx]
                right_shoulder_high = highs[right_shoulder_idx]
                neckline = (left_shoulder_high + right_shoulder_high) / 2

                # Check if price has broken above neckline
                current_price = closes[-1]
                if current_price > neckline * 1.01: # 1% above neckline
                    pattern_confidence = 85
                    target_price = head_low + (neckline - head_low) # Measured move
                    stop_loss = head_low * 0.99 # Below head

                    return "INVERSE_HEAD_AND_SHOULDERS", pattern_confidence, target_price, stop_loss

        return "NONE", 0, 0, 0

    def detect_double_top_bottom(self, price_data_list, periods=25):
        """
        Detect Double Top/Bottom patterns for potential trend reversal
        Professional traders use these reliable reversal pattern.
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Tuple of (pattern_type, confidence, target_price, stop_loss)
        """
        if len(price_data_list) < periods:
            return "NONE", 0, 0, 0

        # Extract high and low prices
        highs = [data.price.high_price for data in price_data_list[-periods:]]
        lows = [data.price.low_price for data in price_data_list[-periods:]]
        closes = [data.price.close_price for data in price_data_list[-periods:]]

        if len(highs) < 8:
            return "NONE", 0, 0, 0

        # Detect Double Top (bearish)
        # Look for two similar highs with a moderate trough between them
        for i in range(2, len(highs) - 5):
            for j in range(i + 3, len(highs) - 2):
                # Check if highs are similar (within 3%)
                if abs(highs[i] - highs[j]) / highs[i] < 0.03:
                    # Check for trough between the highs
                    trough_between = min(lows[i+1:j])
                    # Check if there's a neckline (support level)
                    neckline = trough_between

                    # Check if price has broken below neckline
                    current_price = closes[-1]
                    if current_price < neckline * 0.99: # 1% below neckline
                        # Measured move target
                        target_price = highs[i] - (highs[i] - neckline)
                        stop_loss = max(highs[i], highs[j]) * 1.01 # Above the ghigher high

                        confidence = min(100, 80 + (abs(highs[i] - highs[j]) / highs[j]) * 1000)
                        return "DOUBLE_TOP", confidence, target_price, stop_loss

        # Detect Double Bottom (bullish)
        # Look for two similar lows with a moderate peak between them
        for i in range(2, len(lows) - 5):
            for j in range(i + 3, len(lows) - 2):
                # Check if lows are similar (within 3%)
                if abs(lows[i] - lows[j]) / lows[i] < 0.03:
                    # Check for peak between the lows
                    peak_between = max(highs[i+1:j])
                    # Check if there's a neckline (resistance level)
                    neckline = peak_between

                    # Check if price has broken above neckline
                    current_price = closes[-1]
                    if current_price > neckline * 1.01: # 1% above neckline
                        # Measured move target
                        target_price = lows[i] + (neckline - lows[i])
                        stop_loss = min(lows[i], lows[j]) * 0.99 # Below the lower low

                        confidence = min(100, 80 + (abs(lows[i] - lows[j]) / lows[i]) * 1000)
                        return "DOUBLE_BOTTOM", confidence, target_price, stop_loss

        return "NONE", 0, 0, 0

    def detect_triangle_patterns(self, price_data_list, periods=30):
        """
        Detect triangle patterns (symmetrical, ascending, descending)
        Professional traders use triangles for continuation patterns
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Tuple of (pattern_type, confidence, target_price, stop_loss)
        """
        if len(price_data_list) < periods:
            return "NONE", 0, 0, 0

        # Extract high and low prices
        highs = [data.price.high_price for data in price_data_list[-periods:]]
        lows = [data.price.low_price for data in price_data_list[-periods:]]
        closes = [data.price.close_price for data in price_data_list[-periods:]]

        if len(highs) < 10:
            return "NONE", 0, 0, 0

        # Detect symmetrical triangle
        # Converging support and resistance lines
        upper_trendline = []
        lower_trendline = []

        # Simplified approach - look for conerging highs and lows
        recent_highs = highs[-10:]
        recent_lows = lows[-10:]

        if len(recent_highs) >= 5 and len(recent_lows) >= 5:
            # Check if highs are declining
            high_slope = (recent_highs[-1] - recent_highs[0]) / len(recent_highs)
            # Check if lows are rising
            low_slope = (recent_lows[-1] - recent_lows[0]) / len(recent_lows)

            # If highs declining and lows rising, potential symmetrical triangle
            if high_slope < 0 and low_slope > 0:
                # Check for convergence
                high_range = max(recent_highs) - min(recent_highs)
                low_range = max(recent_lows) - min(recent_lows)

                if high_range > 0 and low_range > 0:
                    convergence = 1 - (abs(high_slope) + abs(low_slope)) / (high_range + low_range)

                    if convergence > 0.3: # Significant convergence
                        # Breakout target (height of  triangle applied to breakout point)
                        triangle_height = max(recent_highs) - min(recent_lows)
                        breakout_point = (max(recent_highs) + min(recent_lows)) / 2

                        # Check for breakout
                        current_price = closes[-1]
                        if current_price > breakout_point * 1.01: # Bullish breakout
                            target_price = breakout_point + triangle_height
                            stop_loss = min(recent_lows) * 0.99
                            confidence = min(100, 80 + convergence * 100)
                            return "SYM_TRIANGLE_BULLISH", confidence, target_price, stop_loss
                        elif current_price < breakout_point * 0.99: # Bearish breakout
                            target_price = breakout_point - triangle_height
                            stop_loss = max(recent_highs) * 1.01
                            confidence = min(100, 70 + convergence * 100)
                            return "SYM_TRIANGLE_BEARISH", confidence, target_price, stop_loss

        # Detect descending triangle (bearish)
        # Falling resistance, horizontal support
        if len(recent_lows) >= 5:
            # Check if lows are relatively flat (horizontal support)
            low_variance = sum((l - sum(recent_lows) / len(recent_lows)) ** 2 for l in recent_lows) / len(recent_lows)
            avg_low = sum(recent_lows) / len(recent_lows)

            # Check if highs are falling
            high_slope = (recent_highs[-1] - recent_highs[0]) / len(recent_highs)

            if low_variance / avg_low < 0.02 and high_slope < 0: # Low variance in lows, falling highs
                # Potential breakdown below support
                current_price = closes[-1]
                if current_price < avg_low * 0.995: # Slightly below support
                    triangle_height = max(recent_highs) - avg_low
                    target_price = avg_low - triangle_height
                    stop_loss = max(recent_highs) * 1.01
                    confidence = min(100, 75 + (abs(high_slope) * 1000))
                    return "DESC_TRIANGLE", confidence, target_price, stop_loss

        return "NONE", 0, 0, 0

    def detect_flag_patterns(self, price_data_list, periods=25):
        """
        Detect flag patterns (bullish and bearish flags)
        Professional traders use flags for continuation patterns
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Tuple of (pattern_type, confidence, target_price, stop_loss)
        """
        if len(price_data_list) < periods:
            return "NONE", 0, 0, 0

        # Extract prices
        closes = [data.price.close_price for data in price_data_list[-periods:]]

        if len(closes) < 10:
            return "NONE", 0, 0, 0

        # Detect bullish flag
        # Look for strong uptrend followed by consolidation (flag)
        if len(closes) >= 15:
            # Check for strong uptrend in first 10 periods
            trend_start = closes[0]
            trend_end = closes[9]
            trend_strength = (trend_end - trend_start) / trend_start

            if trend_strength > 0.05: # 5% uptrend
                # Check for consolidation in next 5 periods (flag)
                flag_highs = [data.price.high_price for data in price_data_list[-15:-5]]
                flag_lows = [data.price.low_price for data in price_data_list[-15:-5]]

                if len(flag_highs) >= 5 and len(flag_lows) >= 5:
                    # Check if flag is relatively narrow (consolidation)
                    flag_height = max(flag_highs) - min(flag_lows)
                    trend_height = trend_end - trend_start

                    if flag_height < trend_height * 0.5: # Flag is smaller than trend
                        # Check for breakout above flag
                        current_price = closes[-1]
                        flag_resistance = max(flag_highs)

                        if current_price > flag_resistance * 1.005: # Breakout
                            # Target: Flag pole height added to breakout point
                            target_price = current_price + trend_height
                            stop_loss = min(flag_lows) * 0.99
                            confidence = min(100, 80 + trend_strength * 500)
                            return "BULL_FLAG", confidence, target_price, stop_loss

        # Detect bearish flag
        # Look for strong downtrend followed by consolidation (flag)
        if len(closes) >= 15:
            # Check for strong downtrend in first 10 periods
            trend_start = closes[0]
            trend_end = closes[9]
            trend_strength = (trend_end - trend_start) / trend_start

            if trend_strength < -0.05: # 5% downtrend
                # Check for consolidation in next 5 periods (flag)
                flag_highs = [data.price.high_price for data in price_data_list[-15:-5]]
                flag_lows = [data.price.low_price for data in price_data_list[-15:-5]]

                if len(flag_highs) >= 5 and len(flag_lows) >= 5:
                    # Check if flag is relatively narrow (consolidation)
                    flag_height = max(flag_highs) - min(flag_lows)
                    trend_height = trend_start - trend_end # Absolute value

                    if flag_height < trend_height * 0.5: # Flag is smaller than trend
                        # Check for breakdown below flag
                        current_price = closes[-1]
                        flag_support = min(flag_lows)

                        if current_price < flag_support * 0.995: # Breakdown
                            # Target: Flag pole height subtracted from breakdown point
                            target_price = current_price - trend_height
                            stop_loss = max(flag_highs) * 1.01
                            confidence = min(100, 80 + abs(trend_strength) * 500)
                            return "BEAR_FLAG", confidence, target_price, stop_loss

        return "NONE", 0, 0, 0

    def pattern_analysis(self, price_data_list, periods=30):
        """
        Comprehensive pattern analysis combining all patterns detection methods
        Professional traders use multiple pattern confirmations for higher probabiity setups
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Dictionary of detected patterns with details
        """
        if len(price_data_list) < periods:
            return {}

        patterns = {}

        # Detect all patterns
        hns_pattern, hns_conf, hns_target, hns_stop = self.detect_head_and_shoulder(price_data_list, periods)
        if hns_pattern != "NONE":
            patterns[hns_pattern] = {
                'confidence': hns_conf,
                'target_price': hns_target,
                'stop_loss': hns_stop,
                'signal': Signal.SELL if 'HEAD_AND_SHOULDERS' in hns_pattern else Signal.BUY
            }

        dt_pattern, dt_conf, dt_target, dt_stop = self.detect_double_top_bottom(price_data_list, periods)
        if dt_pattern != "NONE":
            patterns[dt_pattern] = {
                'confidence': dt_conf,
                'target_price': dt_target,
                'stop_loss': dt_stop,
                'signal': Signal.SELL if dt_pattern == "DOUBLE_TOP" else Signal.BUY
            }

        tri_pattern, tri_conf, tri_target, tri_stop = self.detect_triangle_patterns(price_data_list, periods)
        if tri_pattern != "NONE":
            patterns[tri_pattern] = {
                'confidence': tri_conf,
                'target_price': tri_target,
                'stop_loss': tri_stop,
                'signal': Signal.BUY if 'BULLISH' in tri_pattern or tri_pattern == "ASC_TRIANGLE" else Signal.SELL
            }

        flag_pattern, flag_conf, flag_target, flag_stop = self.detect_flag_patterns(price_data_list, periods)
        if flag_pattern != "NONE":
            patterns[flag_pattern] = {
                'confidence': flag_conf,
                'target_price': flag_target,
                'stop_loss': flag_stop,
                'signal': Signal.BUY if flag_pattern == "BULL_FLAG" else Signal.SELL
            }
        return patterns