from src.enums.signal import Signal
from src.enums.trend import Trend
import math

class HarmonicPatternFilter:
    def __init__(self):
        # Fibonacci ratios for harmonic patterns
        self.GARTLEY_RATIOS = {
            'AB': 0.618,
            'BC': 0.382, # or 0.886
            'CD': 1.272, # or 1.618
            'AD': 0.786
        }

        self.BUTTERFLY_RATIOS = {
            'AB': 0.786,
            'BC': 0.382, # or 0.886
            'CD': 1.618, # or 2.618
            'AD': 1.272  # or 1.618
        }

        self.BAT_RATIOS = {
            'AB': 0.382, # or 0.5
            'BC': 0.382, # or 0.886
            'CD': 1.618, # or 2.618
            'AD': 0.886
        }

        self.CRAB_RATIOS = {
            'AB': 0.382, # or 0.618
            'BC': 0.382, # or 0.886
            'CD': 2.24,  # or 3.168
            'AD': 1.618
        }

        # Tolerance for ratio matching (+- 5%)
        self.TOLERANCE = 0.05

    def calculate_retracement(self, point1, point2):
        """
        Calculate retracement ratio between two points
        :param point1: First price point
        :param point2: Second price point
        :return: Retracement ratio
        """
        if point1 == 0:
            return 0
        return abs(point2 - point1) / abs(point1)

    def check_fibonacci_ratio(self, actual_ratio, target_ratio):
        """
        Check if actual ratio matches target Fibonacci ratio within tolerance
        :param actual_ratio: Actual calculated ratio
        :param target_ratio: Target Fibonacci ratio
        :return: Boolean indication match
        """
        return abs(actual_ratio - target_ratio) <= (target_ratio * self.TOLERANCE)

    def detect_gartly_pattern(self, price_points):
        """
        Detect Gartley harmonic pattern
        Professional traders use this for high-probability reversal setups.
        :param price_points: List of 5 price points [X, A, B, C, D]
        :return: Tuple of (detected, confidence, target_price, stop_loss)
        """
        if len(price_points) != 5:
            return False, 0, 0, 0

        X, A, B, C, D = price_points

        # Calculate Fibonacci retracements
        AB_ratio = self.calculate_retracement(A, B)
        BC_ratio = self.calculate_retracement(B, C)
        CD_ratio = self.calculate_retracement(C, D)
        AD_ratio = self.calculate_retracement(A, D)

        # Check if ratios match Gartley pattern
        ab_match = self.check_fibonacci_ratio(AB_ratio, self.GARTLEY_RATIOS['AB'])
        bc_match = (self.check_fibonacci_ratio(BC_ratio, 0.382) or self.check_fibonacci_ratio(BC_ratio, 0.886))
        cd_match = (self.check_fibonacci_ratio(CD_ratio, 1.272) or self.check_fibonacci_ratio(CD_ratio, 1.618))
        ad_match = self.check_fibonacci_ratio(AD_ratio, self.GARTLEY_RATIOS['AD'])

        # Pattern completion requires all ratios to match
        if ab_match and bc_match and cd_match and ad_match:
            # Determine pattern type (bullish or bearish)
            if A > X and C < A and B > D: # Bullish Gartley
                target_price = D + (A - D) * 0.786
                stop_loss = X * 0.99 # Below X point
                confidence = 90
                return True, confidence, target_price, stop_loss
            elif A < X and C > A and B < D: # Bearish Gartley
                # Target: 0.786 retracement of AD leg
                target_price = D - (D - A) * 0.786
                stop_loss = X * 1.01 # Above X point
                confidence = 90
                return True, confidence, target_price, stop_loss

        return False, 0, 0, 0

    def detect_butterfly_pattern(self, price_points):
        """
        Detect Butterfly harmonic pattern
        Professional traders use this for extended targets
        :param price_points: List of 5 price points [X, A, B, C, D]
        :return: Tuple of (detected, confidence, target_price, stop_loss)
        """
        if len(price_points) != 5:
            return False, 0, 0, 0

        X, A, B, C, D = price_points

        # Calculate Fibonacci retracements
        AB_ratio = self.calculate_retracement(A, B)
        BC_ratio = self.calculate_retracement(B, C)
        CD_ratio = self.calculate_retracement(C, D)
        AD_ratio = self.calculate_retracement(A, D)

        # Check if ratios match Butterfly pattern
        ab_match = self.check_fibonacci_ratio(AB_ratio, self.BUTTERFLY_RATIOS['AB'])
        bc_match = (self.check_fibonacci_ratio(BC_ratio, 0.382) or self.check_fibonacci_ratio(BC_ratio, 0.886))
        cd_match = (self.check_fibonacci_ratio(CD_ratio, 1.618) or self.check_fibonacci_ratio(CD_ratio, 2.618))
        ad_match = (self.check_fibonacci_ratio(AD_ratio, 1.272) or self.check_fibonacci_ratio(AD_ratio, 1.618))

        # Pattern completion requires all ratios to match
        if ab_match and bc_match and cd_match and ad_match:
            # Determine pattern type (bullish or bearish)
            if A > X and C < A and B > D:  # Bullish Butterfly
                # Target: Extension beyond D point
                target_price = X + (A - X) * 1.272 # or 1.618
                stop_loss = A * 0.99  # Below A point
                confidence = 85
                return True, confidence, target_price, stop_loss
            elif A < X and C > A and B < D:  # Bearish Butterfly
                # Target: Extension beyond D point
                target_price = X - (X - A) * 1.272 # or 1.618
                stop_loss = A * 1.01  # Above A point
                confidence = 85
                return True, confidence, target_price, stop_loss

        return False, 0, 0, 0

    def detect_bat_pattern(self, price_points):
        """
        Detect Bat harmonic pattern
        Professional traders use this for precise reversal point
        :param price_points: List of 5 price points [X, A, B, C, D]
        :return: Tuple of (detected, confidence, target_price, stop_loss)
        """
        if len(price_points) != 5:
            return False, 0, 0, 0

        X, A, B, C, D = price_points

        # Calculate Fibonacci retracements
        AB_ratio = self.calculate_retracement(A, B)
        BC_ratio = self.calculate_retracement(B, C)
        CD_ratio = self.calculate_retracement(C, D)
        AD_ratio = self.calculate_retracement(A, D)

        # Check if ratios match Bat pattern
        ab_match = (self.check_fibonacci_ratio(AB_ratio, 0.382) or self.check_fibonacci_ratio(AB_ratio, 0.5))
        bc_match = (self.check_fibonacci_ratio(BC_ratio, 0.382) or self.check_fibonacci_ratio(BC_ratio, 0.886))
        cd_match = (self.check_fibonacci_ratio(CD_ratio, 1.618) or self.check_fibonacci_ratio(CD_ratio, 2.618))
        ad_match = self.check_fibonacci_ratio(AD_ratio, self.BAT_RATIOS['AD'])

        # Pattern completion requires all ratios to match
        if ab_match and bc_match and cd_match and ad_match:
            # Determine pattern type (bullish or bearish)
            if A > X and C < A and B > D:  # Bullish Bat
                # Target: 0.886 retracement of AD leg
                target_price = D + (A - D) * 0.886
                stop_loss = C * 0.99  # Below C point
                confidence = 95
                return True, confidence, target_price, stop_loss
            elif A < X and C > A and B < D:  # Bearish Bat
                # Target: 0.886 retracement of AD leg
                target_price = D - (D - A) * 0.886
                stop_loss = C * 1.01  # Above C point
                confidence = 95
                return True, confidence, target_price, stop_loss

        return False, 0, 0, 0

    def detect_crab_pattern(self, price_points):
        """
        Detect Crab harmonic pattern
        Professional traders use this for extreme extension targets
        :param price_points: List of 5 price points [X, A, B, C, D]
        :return: Tuple of (detected, confidence, target_price, stop_loss)
        """
        if len(price_points) != 5:
            return False, 0, 0, 0

        X, A, B, C, D = price_points

        # Calculate Fibonacci retracements
        AB_ratio = self.calculate_retracement(A, B)
        BC_ratio = self.calculate_retracement(B, C)
        CD_ratio = self.calculate_retracement(C, D)
        AD_ratio = self.calculate_retracement(A, D)

        # Check if ratios match Crab pattern
        ab_match = (self.check_fibonacci_ratio(AB_ratio, 0.382) or self.check_fibonacci_ratio(AB_ratio, 0.618))
        bc_match = (self.check_fibonacci_ratio(BC_ratio, 0.382) or self.check_fibonacci_ratio(BC_ratio, 0.886))
        cd_match = (self.check_fibonacci_ratio(CD_ratio, 2.24) or self.check_fibonacci_ratio(CD_ratio, 3.618))
        ad_match = self.check_fibonacci_ratio(AD_ratio, self.CRAB_RATIOS['AD'])

        # Pattern completion requires all ratios to match
        if ab_match and bc_match and cd_match and ad_match:
            # Determine pattern type (bullish or bearish)
            if A > X and C < A and B > D:  # Bullish Crab
                # Target: Extreme extension at 1.618 of XA leg
                target_price = X + (A - X) * 1.618
                stop_loss = D * 0.99  # Below D point
                confidence = 90
                return True, confidence, target_price, stop_loss
            elif A < X and C > A and B < D:  # Bearish Crab
                # Target: Extreme extension at 1.618 of XA leg
                target_price = X - (X - A) * 1.618
                stop_loss = D * 1.01  # Above D point
                confidence = 90
                return True, confidence, target_price, stop_loss

        return False, 0, 0, 0

    def find_harmonic_patterns(self, price_data_list, periods=50):
        """
        Find harmonic patterns in price data
        Professional traders scan for multiple harmonic patterns for confluence
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Dictionary of detected harmonic patterns
        """
        if len(price_data_list) < periods:
            return {}

        # Extract closing prices
        closes = [data.price.close_price for data in price_data_list[-periods:]]

        if len(closes) < 10:
            return {}

        patterns = {}

        # Look for potential harmonic patterns by scanning for 5-point structures
        for i in range(len(closes) - 9):
            # Extract 5 potential point for pattern formation
            # We need at least 5 points: X, A, B, C, D
            if i + 9 < len(closes):
                potential_points = closes[i:i+10]

                # Try different combinations of 5 points from these 10
                for j in range(6): # Try different starting points
                    if j + 5 <= len(potential_points):
                        points = potential_points[j:j+5]

                        # Check each harmonic pattern
                        gartley_detected, g_conf, g_target, g_stop = self.detect_gartly_pattern(points)
                        if gartley_detected:
                            pattern_key = f"GARTLEY_{i+j}"
                            patterns[pattern_key] = {
                                'type': 'GARTLEY',
                                'confidence': g_conf,
                                'target_price': g_target,
                                'stop_loss': g_stop,
                                'points': points,
                                'signal': Signal.BUY if points[1] > points[0] else Signal.SELL
                            }

                        butterfly_detected, b_conf, b_target, b_stop = self.detect_butterfly_pattern(points)
                        if butterfly_detected:
                            pattern_key = f"BUTTERFLY_{i+j}"
                            patterns[pattern_key] = {
                                'type': 'BUTTERFLY',
                                'confidence': b_conf,
                                'target_price': b_target,
                                'stop_loss': b_stop,
                                'points': points,
                                'signal': Signal.BUY if points[1] > points[0] else Signal.SELL
                            }

                        bat_detected, bat_conf, bat_target, bat_stop = self.detect_bat_pattern(points)
                        if bat_detected:
                            pattern_key = f"BAT_{i+j}"
                            patterns[pattern_key] = {
                                'type': 'BAT',
                                'confidence': bat_conf,
                                'target_price': bat_target,
                                'stop_loss': bat_stop,
                                'points': points,
                                'signal': Signal.BUY if points[1] > points[0] else Signal.SELL
                            }

                        carb_detected, c_conf, c_target, c_stop = self.detect_crab_pattern(points)
                        if carb_detected:
                            pattern_key = f"CARB_{i+j}"
                            patterns[pattern_key] = {
                                'type': 'CARB',
                                'confidence': c_conf,
                                'target_price': c_target,
                                'stop_loss': c_stop,
                                'points': points,
                                'signal': Signal.BUY if points[1] > points[0] else Signal.SELL
                            }

        return patterns


    def harmonic_convergence_analysis(self, price_data_list, periods=50):
        """
        Analyze convergence of multiple harmonic patterns for higher probability setups
        Professional traders look for confluence of multiple harmonic patterns
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Tuple of (convergence_score, best_setup, risk_level
        """
        if len(price_data_list) < periods:
            return 0, None, "LOW"

        # Find all harmonic patterns
        patterns = self.find_harmonic_patterns(price_data_list, periods)

        if not patterns:
            return 0, None, "LOW"

        # Calculate convergence score based on:
        # 1. Number of patterns found
        # 2. Average confidence of patterns
        # 3. Agreement in direction (buy/sell signals)
        # 4. Proximity of target prices

        pattern_count = len(patterns)
        total_confidence = sum(pattern['confidence'] for pattern in patterns.values())
        avg_confidence = total_confidence / pattern_count if pattern_count > 0 else 0

        # Count buy vs sell signals
        buy_signals = sum(1 for pattern in patterns.values() if pattern['signal'] == Signal.BUY)
        sell_signals = sum(1 for pattern in patterns.values() if pattern['signal'] == Signal.SELL)

        # Calculate signal agreement
        signal_agreement = abs(buy_signals - sell_signals) / pattern_count if pattern_count > 0 else 0

        # Calculate target price clustering (patterns with similar targets are more reliable)
        targets = [pattern['target_price'] for pattern in patterns.values()]
        if len(targets) > 1:
            target_variance = sum(t - sum(targets) / len(targets)**2 for t in targets) / len(targets)
            target_clustering = 1 / (1 + target_variance) # Higher clustering = lower variance
        else:
            target_clustering = 0.5 # Neutral clustering

        # Convergence score (0-100)
        convergence_score = (
        (pattern_count * 10) * 0.3 +    # Up to 30 points for pattern count
        (avg_confidence * 0.4) +        # Up to 40 points for average confidence
        (signal_agreement * 50 * 0.2) + # Up to 20 points for signal agreement
        (target_clustering * 10 * 0.1)  # Up do 10 points for target clustering
        )

        # Determine best setup
        if buy_signals > sell_signals:
            best_setup = "BULLISH"
            signal_direction = Signal.BUY
        elif sell_signals > buy_signals:
            best_setup = "BEARISH"
            signal_direction = Signal.SELL
        else:
            best_setup = "NEUTRAL"
            signal_direction = Signal.HOLD

        # Determine risk level based on convergence score
        if convergence_score > 80:
            risk_level = "LOW"
        elif convergence_score > 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Find the pattern with highest confidence as the primary setup
        best_pattern = None
        highest_confidence = 0
        for pattern in patterns.values():
            if pattern['confidence'] > highest_confidence:
                highest_confidence = pattern['confidence']
                best_pattern = pattern

        return convergence_score, {
            'setup_type': best_setup,
            'signal': signal_direction,
            'primary_pattern': best_pattern,
            'pattern_count': pattern_count,
            'avg_confidence': avg_confidence,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
        }, risk_level
