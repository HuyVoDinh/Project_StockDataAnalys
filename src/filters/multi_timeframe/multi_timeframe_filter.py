from src.enums.trend import Trend
from src.enums.signal import Signal

class MultiTimeframeFilter:
    def __init__(self):
        pass

    def timeframe_confirmation(self, price_data_dict, timeframes=['daily', 'weekly', 'monthly']):
        """
        Analyze trend confirmation across multiple timeframes
        Professional traders require confirmation across timeframes for higher probability trades.
        :param price_data_dict: Dictionary of price data by timeframe {timeframe: [data]}
        :param timeframes: List of timeframes to analyze
        :return: Tuple of (confirmation_level, dominant_trend, timeframe_alignment
        """
        if not price_data_dict:
            return "NO_CONFIRMATION", Trend.Sideway, {}

        trend_analysis = {}

        # Analyze each timeframe
        for timeframe in timeframes:
            if timeframe in price_data_dict and len(price_data_dict[timeframe]) >= 20:
                data_list = price_data_dict[timeframe]
                prices = [data.price.close_price for data in data_list[-20:] if data.price.close_price > 0]

                if len(prices) >= 5 and prices[0] > 0:
                    # Calculate trend
                    trend_return = (prices[-1] - prices[0]) / prices[0]

                    if trend_return > 0.05: # 5% threshold
                        trend_analysis[timeframe] = Trend.Strong_Up
                    elif trend_return > 0.02: # 2% threshold
                        trend_analysis[timeframe] = Trend.Up
                    elif trend_return < -0.05: # -5% threshold
                        trend_analysis[timeframe] = Trend.Strong_Down
                    elif trend_return < -0.02: # 5% threshold
                        trend_analysis[timeframe] = Trend.Down
                    else:
                        trend_analysis[timeframe] = Trend.Sideway
                else:
                    trend_analysis[timeframe] = Trend.Sideway
            else:
                trend_analysis[timeframe] = Trend.Sideway

        # Check for timeframe alignment
        bullish_timeframes = sum(1 for trend in trend_analysis.values() if trend in [Trend.Up, Trend.Strong_Up])
        bearish_timeframes = sum(1 for trend in trend_analysis.values() if trend in [Trend.Down, Trend.Strong_Down])
        neutral_timeframes = sum(1 for trend in trend_analysis.value() if trend == Trend.Sideway)

        # Determine dominant trend
        if bullish_timeframes > bearish_timeframes and bullish_timeframes >= neutral_timeframes:
            dominant_trend = Trend.Up if bullish_timeframes == 2 else Trend.Strong_Up
        elif bearish_timeframes > bullish_timeframes and bearish_timeframes >= neutral_timeframes:
            dominant_trend = Trend.Down if bearish_timeframes == 2 else Trend.Strong_Down
        else:
            dominant_trend = Trend.Sideway

        # Determine confirmation level
        if bullish_timeframes == 3: # All timeframes bullish
            confirmation_level = "STRONG_BULLISH"
        elif bearish_timeframes == 3: # All timeframes bearish
            confirmation_level = "STRONG_BEARISH"
        elif bullish_timeframes == 2 and bearish_timeframes == 0: # Two bullish, one neutral
            confirmation_level = "MODERATE_BULLISH"
        elif bearish_timeframes == 2 and bullish_timeframes == 0: # Two bearish, one neutral
            confirmation_level = "MODERATE_BEARISH"
        elif bullish_timeframes == 1 and bearish_timeframes == 0 and neutral_timeframes == 2: # One bullish, two neutral
            confirmation_level = "WEAK_BULLISH"
        elif bearish_timeframes == 1 and bullish_timeframes == 0 and neutral_timeframes == 2: # One bearish, two neutral
            confirmation_level = "WEAK_BEARISH"
        else:
            confirmation_level = "NO_CONFIRMATION"

        return confirmation_level, dominant_trend, trend_analysis

    def moving_average_alignment(self, ma_data_dict, timeframes=['daily', 'weekly', 'monthly']):
        """
        Analyze moving average alignment across multiple timeframes
        Professional traders look for aligned moving averages for trend confirmation
        :param ma_data_dict: Dictionary of MA data by timeframe {timeframe: {ma_period: [data]}}
        :param timeframes: List of timeframes to analyze
        :return: Tuple of (alignment_score, alignment_quality, dominant_direction)
        """
        if not ma_data_dict:
            return 0, 0, Trend.Sideway

        alignment_scores = {}

        # Analyze each timeframe
        for timeframe in timeframes:
            if timeframe in ma_data_dict:
                ma_data = ma_data_dict[timeframe]
                ma_values = []

                # Extract MA values for different periods
                for ma_period, data_list in ma_data.items():
                    if len(data_list) > 0 and hasattr(data_list[-1], 'ma_price') and data_list[-1].ma_price is not None:
                        ma_values.append(data_list[-1].ma_price)

                if len(ma_values) >= 3:
                    # Check if MAs are aligned (ascending order for uptrend, descending for downtrend)
                    sorted_values = sorted(ma_values)

                    # Calculate alignment score (0 - 100)
                    if ma_values == sorted_values: # Ascending order (bullish)
                        alignment_scores = 80
                        direction = Trend.Up
                    elif ma_values == sorted_values[::-1]: # Descending order (bearish)
                        alignment_scores = 80
                        direction = Trend.Down
                    else:
                        # Partial alignment
                        alignment_scores = 40
                        direction = Trend.Sideway

                    alignment_scores[timeframe] = (alignment_scores, direction)
                else:
                    alignment_scores[timeframe] = (0, Trend.Sideway)
            else:
                alignment_scores[timeframe] = (0, Trend.Sideway)

        # Calculate overall alignment score
        total_score = sum(score for score, _ in alignment_scores.values())
        valid_timeframes = sum(1 for score, _ in alignment_scores.values() if score > 0)

        if valid_timeframes > 0:
            alignment_score = total_score / valid_timeframes
        else:
            alignment_score = 0

        # Determine alignment quality
        if alignment_score > 70:
            alignment_quality = "HIGH"
        elif alignment_score > 50:
            alignment_quality = "MODERATE"
        elif alignment_score > 30:
            alignment_quality = "LOW"
        else:
            alignment_quality = "POOR"

        # Determine dominant direction
        bullish_timeframes = sum(1 for _, direction in alignment_scores.values() if direction in [Trend.Up, Trend.Strong_Up])
        bearish_timeframes = sum(1 for _, direction in alignment_scores.values() if direction in [Trend.Down, Trend.Strong_Down])

        if bullish_timeframes > bearish_timeframes:
            dominant_direction = Trend.Up
        elif bearish_timeframes > bullish_timeframes:
            dominant_direction = Trend.Down
        else:
            dominant_direction = Trend.Sideway

        return alignment_score, alignment_quality, dominant_direction

    def support_resistance_multiframe(self, sr_data_dict, timeframes=['daily', 'weekly', 'monthly']):
        """
        Analyze support/resistance levels across multiple timeframes
        Professional traders look for confluence of levels across timeframes
        :param sr_data_dict: Dictionary of S/R data by timeframe {timeframe: [support_levels], [resistance_levels]}
        :param timeframes: List of timeframes to analyze
        :return: Tuple of (confluence_score, key_levels, timeframe_importance)
        """
        if not sr_data_dict:
            return 0, [], {}

        all_support_levels = []
        all_resistance_levels = []
        timeframe_levels = []

        # Collect levels from each timeframe
        for timeframe in timeframes:
            if timeframe in sr_data_dict:
                support_levels, resistance_levels = sr_data_dict[timeframe]
                all_support_levels.extend(support_levels)
                all_resistance_levels.extend(resistance_levels)
                timeframe_levels[timeframe] = {
                    'support': support_levels,
                    'resistance': resistance_levels,
                    'importance': len(support_levels) + len(resistance_levels)
                }

        # Find confluence levels (levels that appear in multiple timeframes)
        confluence_support = {}
        confluence_resistance = {}

        # This is a simplified approach - in practice, you'd cluster similar levels
        for timeframe, levels in timeframe_levels.item():
            for support in levels['support']:
                if support not in confluence_support:
                    confluence_support[support] = []
                confluence_support[support].append(timeframe)

            for resistance in levels['resistance']:
                if resistance not in confluence_resistance:
                    confluence_resistance[resistance] = []
                confluence_resistance[resistance].append(timeframe)

        # Calculate confluence score based on how many timeframes each level appears in
        support_confluence_scores = {level: len(timeframes_list) for level, timeframes_list in confluence_support.items()}
        resistance_confluence_scores = {level: len(timeframes_list) for level, timeframes_list in confluence_resistance.items()}

        # Key levels are those appearing in 2+ timeframes
        key_support_levels = [level for level, score in support_confluence_scores.items() if score >= 2]
        key_resistance_levels = [level for level, score in resistance_confluence_scores.items() if score >= 2]
        key_levels = key_support_levels + key_resistance_levels

        # Calculate overall confluence score
        total_confluence = sum(support_confluence_scores.values()) + sum(resistance_confluence_scores.values())
        max_possible_confluence = len(timeframes) * (len(confluence_support) + len(confluence_resistance))

        if max_possible_confluence > 0:
            confluence_score = min(100, (total_confluence / max_possible_confluence) * 100)
        else:
            confluence_score = 0

        # Timeframe importance (higher timeframes are more important)
        timeframe_importance = {}
        importance_weights = {'monthly': 3, 'weekly': 2, 'daily': 1}

        for timeframe in timeframes:
            if timeframe in timeframe_levels:
                base_importance = timeframe_levels[timeframe]['importance']
                weighted_importance = base_importance * importance_weights.get(timeframe, 1)
                timeframe_importance[timeframe] = weighted_importance

        return confluence_score, key_levels, timeframe_importance

    def volatility_regime_multiframe(self, volatility_data_dict, timeframes=['daily', 'weekly', 'monthly']):
        """
        Analyze volatility regimes across multiple timeframes
        Professional traders adapt to different volatility environments
        :param volatility_data_dict: Dictionary of volatility data by timeframe {timeframe: [data]}
        :param timeframes: List of timeframes to analyze
        :return: Tuple of (volatility_regime, regime_consistency, risk_assesment
        """
        if not volatility_data_dict:
            return "MODERATE", 0, "NEUTRAL"

        volatility_analysis = {}

        # Analyze each timeframe
        for timeframe in timeframes:
            if timeframe in volatility_data_dict and len(volatility_data_dict[timeframe]) >= 20:
                vol_data = volatility_data_dict[timeframe]
                volatility_values = [data.volatility_value for data in vol_data[-20:]
                                     if hasattr(data, 'volatility_value') and data.volatility_value is not None]

                if len(volatility_values) >= 10:
                    avg_volatility = sum(volatility_values) / len(volatility_values)
                    current_volatility = volatility_values[-1]

                    # Classify volatility regime
                    if current_volatility > avg_volatility * 1.5:
                        regime = "HIGH"
                    elif current_volatility < avg_volatility * 0.7:
                        regime = "LOW"
                    else:
                        regime = "MODERATE"

                    volatility_analysis[timeframe] = {
                        'regime': regime,
                        'current': current_volatility,
                        'average': avg_volatility,
                        'trend': (current_volatility - avg_volatility) / avg_volatility if avg_volatility != 0 else 0
                    }
                else:
                    volatility_analysis[timeframe] = {
                        'regime': "MODERATE",
                        'current': 0,
                        'average': 0,
                        'trend': 0
                    }
            else:
                volatility_analysis[timeframe] = {
                    'regime': "MODERATE",
                    'current': 0,
                    'average': 0,
                    'trend': 0
                }

        # Determine dominant volatility regime
        high_count = sum(1 for data in volatility_analysis.values() if data['regime'] == 'HIGH')
        low_count = sum(1 for data in volatility_analysis.values() if data['regime'] == 'LOW')
        moderate_count = sum(1 for data in volatility_analysis.values() if data['regime'] == 'MODERATE')

        if high_count > low_count and high_count >= moderate_count:
            volatility_regime = "HIGH"
        elif low_count > high_count and low_count >= moderate_count:
            volatility_regime = "LOW"
        else:
            volatility_regime = "MODERATE"

        # Calculate regime consistency
        matching_timeframes = sum(1 for data in volatility_analysis.values() if data['regime'] == volatility_regime)
        regime_consistency = (matching_timeframes / len(timeframes)) * 100

        # Risk assessment based on volatility analysis
        if volatility_regime == "HIGH":
            risk_assessment = "HIGH" if regime_consistency > 60 else "MODERATE"
        elif volatility_regime == "LOW":
            risk_assessment = "LOW" if regime_consistency > 60 else "MODERATE"
        else:
            risk_assessment = "MODERATE"

        return volatility_regime, regime_consistency, risk_assessment

    def momentum_multiframe(self, momentum_data_dict, timeframes=['daily', 'weekly', 'monthly']):
        """
        Analyze momentum across multiple timeframes
        Professional traders look for consistent momentum across timeframs
        :param momentum_data_dict: Dictionary of momentum data by timeframe {timeframe: [data]}
        :param timeframes: List of timeframes to analyze
        :return: Tuple of (momentum_regime, momentum_consistency, momentum_quality)
        """
        if not momentum_data_dict:
            return Trend.Sideway, 0, 0

        momentum_analysis = {}

        # Analyze each timeframe
        for timeframe in timeframes:
            if timeframe in momentum_data_dict and len(momentum_data_dict[timeframe]) >= 15:
                mom_data = momentum_data_dict[timeframe]
                momentum_values = [data.momentum_value for data in mom_data[-15:]
                                   if hasattr(data, 'momentume_value') and data.momentume_value is not None]

                if len(momentum_values) >= 5:
                    avg_momentum = sum(momentum_values) / len(momentum_values)
                    current_momentum = momentum_values[-1]

                    # Classify momentum
                    if current_momentum > 0.05: # 5% threshold
                        momentum_trend = Trend.Strong_Up
                    elif current_momentum > 0.02: # 2% threshold
                        momentume_trend = Trend.Up
                    elif current_momentum < -0.05: # -5% threashold
                        momentum_trend = Trend.Strong_Down
                    elif current_momentum < -0.02: # -2% threshold
                        momentum_trend = Trend.Down
                    else:
                        momentum_trend = Trend.Sideway

                    momentum_analysis[timeframe] = {
                        'trend': momentum_trend,
                        'current': current_momentum,
                        'average': avg_momentum,
                        'strength': abs(current_momentum) * 100
                    }
                else:
                    momentum_analysis[timeframe] = {
                        'trend': Trend.Sideway,
                        'current': 0,
                        'average': 0,
                        'strength': 0
                    }
            else:
                momentum_analysis[timeframe] = {
                    'trend': Trend.Sideway,
                    'current': 0,
                    'average': 0,
                    'strength': 0
                }

        # Determine dominant momentum regime
        bullish_count = sum(1 for data in momentum_analysis.values() if data['trend'] in [Trend.Up, Trend.Strong_Up])
        bearish_count = sum(1 for data in momentum_analysis.values() if data['trend'] in [Trend.Down, Trend.Strong_Down])
        neutral_count = sum(1 for data in momentum_analysis.values() if data['trend'] == Trend.Sideway)

        if bullish_count > bearish_count and bullish_count >= neutral_count:
            momentum_regime = Trend.Strong_Up if bullish_count == 3 else Trend.Up
        elif bearish_count > bullish_count and bearish_count >= neutral_count:
            momentum_regime = Trend.Strong_Down if bearish_count == 3 else Trend.Down
        else:
            momentum_regime = Trend.Sideway

        # Calculate momentum consistency
        matching_timeframes = sum(1 for data in momentum_analysis.values() if data['trend'] == momentum_regime)
        momentum_consistency = (matching_timeframes / len(timeframes)) * 100

        # Calculate momentum quality (average strength)
        valid_strengths = [data['strength'] for data in momentum_analysis.values() if data['strength'] > 0]
        if valid_strengths:
            momentum_quality = sum(valid_strengths) / len(valid_strengths)
        else:
            momentum_quality = 0
        return momentum_regime, momentum_consistency, momentum_quality







































