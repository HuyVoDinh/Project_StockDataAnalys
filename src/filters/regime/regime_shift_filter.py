from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
import numpy as np

class RegimeShiftFilter:
    def __init__(self):
        pass

    def detect_volatility_regime_change(self, volatility_data_list, short_window=20, long_window=60):
        """
        Detect volatility regime changes that indicate market state shifts
        Professional traders adapt strategies based on volatility regimes
        :param volatility_data_list: List of volatility data
        :param short_window: Short-term volatility window
        :param long_window: Long-term volatility window
        :return: Tuple of (regime_change, volatility_outlook, transition_probability)
        """
        if len(volatility_data_list) < long_window:
            return False, "STABLE", 0

        # Extract volatility values
        volatilities = []
        for data in volatility_data_list[-long_window:]:
            if hasattr(data, 'volatility_value') and data.volatility_value is not None:
                volatilities.append(data.volatility_value)

        if len(volatilities) < long_window:
            return False, "STABLE", 0

        # Calculate short and long-term volatility
        short_vol = sum(volatilities[-short_window:]) / short_window
        long_vol = sum(volatilities) / len(volatilities)

        if long_vol == 0:
            return False, "STABLE", 0

        # Calculate volatility ratio
        vol_ratio = short_vol / long_vol

        # Detect regime change
        if vol_ratio > 1.5: # short-term volatility 50% higher than long-term
            regime_change = True
            volatility_outlook = "INCREASING"
        elif vol_ratio < 0.7: # Short-term volatility 30% lower than long-term
            regime_change = True
            volatility_outlook = "DECREASING"
        else:
            regime_change = False
            volatility_outlook = "STABLE"

        # Calculate transition probability
        transition_probability = min(100, abs(vol_ratio - 1) * 100)

        return regime_change, volatility_outlook, transition_probability

    def detect_trend_regime_change(self, price_data_list, window=50):
        """
        Detect trend regime changes from trending to mean-reverting
        Professional traders adjust strategies based on trend persistence
        :param price_data_list:  List of price data
        :param window: Analysis window
        :return: Tuple of (trend_change, new_trend_type, confidence)
        """
        if len(price_data_list) < window:
            return False, "NEUTRAL", 0

        # Extract prices
        prices = [data.price.close_price for data in price_data_list[-window:] if data.price.close_price > 0]

        if len(prices) < window *0.8: # Need at least 80% valid data
            return False, "NEUTRAL", 0

        # Calculate returns
        returns = [prices[i] - prices[i-1] for i in range(1, len(prices)) if prices[i-1] > 0]

        if len(returns) < 10:
            return False, "NEUTRAL", 0

        # Calculate trend strength (slope of price series)
        x = list(range(len(prices)))
        slope, intercept = np.polyfit(x, prices, 1)

        # Calculate trend consistency (autocorrelation proxy)
        if len(returns) >= 5:
            # Simple autocorrelation measure
            positive_returns = sum(1 for r in returns if r > 0)
            negative_returns = sum(1 for r in returns if r < 0)
            trend_consistency = abs(positive_returns - negative_returns) / len(returns)
        else:
            trend_consistency = 0.5

        # Calculate price efficiency (trend strength)
        price_efficiency = abs(slope) * len(prices) / (max(prices) - min(prices)) if max(prices) > min(prices) else 0

        # Detect trend regime
        if abs(slope) > 0.1 and trend_consistency > 0.6 and price_efficiency > 0.3:
            # Strong trending regime
            trend_change = False
            new_trend_type = "TRENDING" if slope > 0 else "TRENDING_DOWN"
        elif abs(slope) < 0.05 and trend_consistency < 0.4:
            # Mean-reverting regime
            trend_change = True
            new_trend_type = "MEAN_REVERTING"
        else:
            # Mixed regime
            trend_change = False
            new_trend_type = "NEUTRAL"

        # Calculate confidence
        confidence_factors = [
            min(100, abs(slope) * 500),      # Scale slope to 0-100
            trend_consistency * 100,         # Scale consistency to 0-100
            min(100, price_efficiency * 200) # Scale efficiency to 0-100
        ]

        confidence = sum(confidence_factors) / len(confidence_factors)

        return trend_change, new_trend_type, confidence

    def detect_liquidity_regime_change(self, volume_data_list, trade_data_list, window=30):
        """
        Detect liquidity regime changes that affect market dynamics
        Professional traders adjust position sizes based on liquidity conditions
        :param volume_data_list: List of volume data
        :param trade_data_list: List of trade data
        :param window: Analysis window
        :return: Tuple of (liquidity_change, liquidity_condition, market_impact)
        """
        if len(volume_data_list) < window or len(trade_data_list) < window:
            return False, "MODERATE", "NEUTRAL"

        # Extract volume data
        volumes = [data.volume for data in volume_data_list[-window:] if data.volume is not None]

        if len(volumes) < window * 0.7:
            return False, "MODERATE", "NEUTRAL"

        # Calculate volume metrics
        avg_volume = sum(volumes) / len(volumes)
        current_volume = sum(volumes[-5:] / 5 if len(volumes) >= 5 else avg_volume)

        if avg_volume == 0:
            return False, "MODERATE", "NEUTRAL"

        # Calculate volume ratio
        volume_ratio = current_volume / avg_volume

        # Extract trade size data
        trade_sizes = []
        for trade in trade_data_list[-window:]:
            if hasattr(trade, 'soze') and trade.size is not None:
                trade_sizes.append(trade.size)

        if len(trade_sizes) >= 10:
            avg_trade_size = sum(trade_sizes) / len(trade_sizes)
            large_trades = sum(1 for size in trade_sizes if size > avg_trade_size * 2)
            large_trade_ratio = large_trades / len(trade_sizes)
        else:
            large_trade_ratio = 0.1 # Default assumption

        # Detect liquidity regime change
        if volume_ratio > 1.5 and large_trade_ratio > 0.3:
            liquidity_change = True
            liquidity_condition = "HIGH_INSTRITUTIONAL"
        elif volume_ratio < 0.7 and large_trade_ratio < 0.1:
            liquidity_change = True
            liquidity_condition = "LOW_RETAIL"
        elif volume_ratio > 2.0:
            liquidity_change = True
            liquidity_condition = "SPIKE"
        else:
            liquidity_change = False
            liquidity_condition = "MODERATE"

        # Assess market impact
        if liquidity_condition == "HIGH_INSTRITUTIONAL":
            market_impact = "BULLISH" if volume_ratio > 1.8 else "NEUTRAL"
        elif liquidity_condition == "LOW_RETAIL":
            market_impact = "BEARISH"
        elif liquidity_condition == "SPIKE":
            market_impact = "VOLATILE"
        else:
            market_impact = "NEUTRAL"

        return liquidity_change, liquidity_condition, market_impact

    def detect_regime_transition_signals(self, price_data_list, volume_data_list, volatility_data_list, window=40):
        """
        Detect comprehensive regime transition signals combining multiple factors
        Professional traders use multi-factor analysis for regime detection
        :param price_data_list: List of price data
        :param volume_data_list:List of volume data
        :param volatility_data_list: List of volatility data
        :param window: Analysis window
        :return: Tuple of (transition_signal, regime_outlook, composite_score)
        """
        if len(price_data_list) < window or len(volume_data_list) < window or len(volatility_data_list) < window:
            return "HOLD", "STABLE", 50

        # Analyze each component
        vol_change, vol_outloook, vol_prob = self.detect_volatility_regime_change(volatility_data_list, 15,window)
        trend_change, trend_type, trend_conf = self.detect_trend_regime_change(price_data_list,window)
        vol_ratio = vol_prob / 100 # Convert to ratio

        # Extract price and volume data
        prices = [data.price.close_price for data in price_data_list[-20:] if data.price.close_price > 0]
        volumes = [data.volume for data in volume_data_list[-20:] if data.volume is not None]

        if len(prices) < 10 or len(volumes) < 10:
            return "HOLD", "STABLE", 50

        # Calculate price momentum
        if len(prices) >= 2 and prices[0] > 0:
            momentum = (prices[-1] - prices[0]) / prices[0]
        else:
            momentum = 0

        # Calculate volume trend
        if len(volumes) >= 2:
            avg_vol_early = sum(volumes[:10]) / 10
            avg_vol_late = sum(volumes[10:]) / 10
            volume_trend = (avg_vol_late - avg_vol_early) / avg_vol_early if avg_vol_early > 0 else 0
        else:
            volume_trend = 0

        # Composite regime analysis
        regime_signals = []

        # Volatility regime signal
        if vol_outloook == "INCREASING":
            regime_signals.append(("VOLATILITY", "REDUCE", vol_prob))
        elif vol_outloook == "DECREASING":
            regime_signals.append(("VOLATILITY", "ACCUMULATE", vol_prob))

        # Trend regime signal
        if trend_type == "TRENDING":
            regime_signals.append(("TREND", "FOLLOW", trend_conf))
        elif trend_type == "TRENDING_DOWN":
            regime_signals.append(("TREND", "SHORT", trend_conf))
        elif trend_type == "MEAN_REVERTING":
            regime_signals.append(("TREND", "REVERSION", "REVERT", trend_conf))

        # Momentum signal
        if abs(momentum) > 0.03: # 3% momentum
            signal = "BUY" if momentum > 0 else "SELL"
            regime_signals.append(("MOMENTUM", signal, min(100, abs(volume_trend) * 200)))

        # Volume signal
        if abs(volume_trend) > 0.2 : # 20% volume change
            signal = "CONFIRM" if volume_trend > 0 else "WARNING"
            regime_signals.append(("VOLUME", signal, min(100, abs(volume_trend) * 200)))

        if not regime_signals:
            return "HOLD", "STABLE", 50

        # Calculate composite score
        total_weighted_score = sum (score for _, _, score in regime_signals)
        total_signals = len(regime_signals)
        composite_score = total_weighted_score / total_signals if total_signals > 0 else 50

        # Determine regime outlook
        buy_signals = sum(1 for _, signal, _ in regime_signals if signal in ["FOLLOW", "ACCUMULATE", "BUY", "CONFIRM"])
        sell_signals = sum(1 for _, signal, _ in regime_signals if signal in ["SHORT", "REDUCE", "SELL", "WARNING"])

        if buy_signals > sell_signals and buy_signals >=2:
            regime_outlook = "BULLISH"
            transition_signal = "BUY"
        elif sell_signals > buy_signals and sell_signals >= 2:
            regime_outlook = "BEARISH"
            transition_signal = "SELL"
        elif abs(buy_signals - sell_signals) <= 1 and total_signals >= 3:
            regime_outlook = "VOLATILE"
            transition_signal = "REDUCE"
        else:
            regime_outlook = "STABLE"
            transition_signal = "HOLD"

        return transition_signal, regime_outlook, composite_score

    def adaptive_strategy_selection(self, regime_signals, current_strategy):
        """
        Select optimal strategy based on current regime signals
        Professional traders adapt their approach to market conditions
        :param regime_signals: List of regime signals
        :param current_strategy: Current strategy name
        :return: Tuple of (recommended_strategy, strategy_confidence, adjustment_reason)
        """
        if not regime_signals:
            return current_strategy, 70, "NO_CHANGE"

        # Count signal type
        volatility_signals = [s for s in regime_signals if s[0] == "VOLATILITY"]
        trend_signals = [s for s in regime_signals if s[0] == "TREND"]
        momentum_signals = [s for s in regime_signals if s[0] == "MOMENTUM"]

        # Strategy mapping based on regime signals
        if volatility_signals and any(s[1] == "INCREASING" for s in volatility_signals):
            # High volatility environment
            if trend_signals and any(s[1] == "MEAN_REVERTING" for s in trend_signals):
                recommended_strategy = "MEAN_REVERSION"
                reason = "HIGH_VOLATILITY_MEAN_REVERSION"
            else:
                recommended_strategy = "VOLATILITY_BREAKOUT"
                reason = "HIGH_VOLATILITY_BREAKOUT"
            confidence = 85
        elif trend_signals and any(s[1] in ["TRENDING", "TRENDING_DOWN"] for s in trend_signals):
            # Trending environment
            recommended_strategy = "TRENDING_FOLLOWING"
            reason = "STRONG_TREND"
            confidence = 90
        else:
            # DEfault to current strategy
            recommended_strategy = current_strategy
            reason = "STABLE_REGIME"
            confidence = 70

        return recommended_strategy, confidence, reason

    def regime_stress_testing(self, historical_regime_data, strategy_performance_data):
        """
        Test strategy performance across different historical regimes
        Professional traders validate strategies across market conditions
        :param historical_regime_data:  Historical regime classifications
        :param strategy_performance_data: Strategy performance in each regime
        :return: Tuple of (regime_fitness, performance_profile, risk_adjustment)
        """
        if not historical_regime_data or not strategy_performance_data:
            return "NEUTRAL", {}, "MODERATE"

        # Group performance by regime
        regime_performance = {}
        for regime, performance in zip(historical_regime_data, strategy_performance_data):
            if regime not in regime_performance:
                regime_performance[regime] = []
            regime_performance[regime].append(performance)

        # Calculate performance metrics for each regime
        performance_profile = {}
        for regime, performances in regime_performance.items():
            if performances:
                avg_return = sum(performances) / len(performances)
                std_dev = (sum((p - avg_return) ** 2 for p in performances) / len(performances)) ** 0.5
                sharpe_ratio = avg_return / std_dev if std_dev > 0 else 0

                performance_profile[regime] = {
                    'avg_return': avg_return,
                    'std_dev': std_dev,
                    'sharpe_ratio': sharpe_ratio,
                    'sample_size': len(performances)
                }

        # Determine regime fitness
        total_sharpe = sum(metrics['sharpe_ratio'] for metrics in performance_profile.values())
        regime_count = len(performance_profile)

        if regime_count > 0:
            avg_sharpe = total_sharpe / regime_count

            if avg_sharpe > 0.5:
                regime_fitness = "STRONG"
            elif avg_sharpe > 0.2:
                regime_fitness = "MODERATE"
            else:
                regime_fitness = "WEAK"
        else:
            regime_fitness = "NEUTRAL"

        # Determine risk adjustment
        high_volatility_performance = performance_profile.get("HIGH_VOLATILITY", {"sharpe_ratio": 0})
        low_volatility_performance = performance_profile.get("LOW_VOLATILITY", {"sharpe_ratio": 0})

        if high_volatility_performance["sharpe_ratio"] > low_volatility_performance["sharpe_ratio"] * 1.2:
            risk_adjustment = "AGGRESSIVE"
        elif high_volatility_performance["sharpe_ratio"] < low_volatility_performance["sharpe_ratio"] * 0.8:
            risk_adjustment = "CONSERVATIVE"
        else:
            risk_adjustment = "MODERATE"

        return regime_fitness, performance_profile, risk_adjustment





















