from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel

class ContrarianFilter:
    def __init__(self):
        pass

    def sentiment_extremes(self, sentiment_data_list, periods=30):
        """
        Indentify sentiment extremes for contrarian opportunities
        Professional contrarian traders buy whe others are fearful and sell when others are greedy.
        :param sentiment_data_list: List of sentiment data
        :param periods: Number of periods to analyze
        :return: Tuple of (extreme_level, contrarian_signal, confidence)
        """
        if len(sentiment_data_list) < periods:
            return "NEUTRAL", Signal.HOLD, 0

        # Extract sentiment scores (assuming -100 to 100 scale)
        sentiment_scores = []
        for data in sentiment_data_list[-periods:]:
            if hasattr(data, 'sentiment_score') and data.sentiment_score is not None:
                sentiment_scores.append(data.sentiment_score)

        if len(sentiment_scores) < 10:
            return "NEUTRAL", Signal.HOLD, 0

        # Calculate average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        # Identify extremes
        if avg_sentiment < -50: # Extreme fear
            extreme_level = "EXTREME_FEAR"
            contrarian_signal = Signal.BUY
            confidence = min(100, abs(avg_sentiment + 50) * 2) # Scale to 0-100
        elif avg_sentiment < -20: # Fear
            extreme_level = "FEAR"
            contrarian_signal = Signal.BUY
            confidence = min(100, abs(avg_sentiment + 20) * 3)
        elif avg_sentiment > 50: # Extreme greed
            extreme_level = "EXTREME_GREED"
            contrarian_signal = Signal.SELL
            confidence = min(100, abs(avg_sentiment - 50) * 2)
        elif avg_sentiment > 20: # GREED
            extreme_level = "EXTREME_FEAR"
            contrarian_signal = Signal.SELL
            confidence = min(100, abs(avg_sentiment - 20) * 3)
        else:
            extreme_level = "NEUTRAL"
            contrarian_signal = Signal.HOLD
            confidence = 0

        return extreme_level, contrarian_signal, confidence

    def crowded_trade_analysis(self, positioning_data_list, periods=25):
        """
        Analyze positioning data to identify crowded trades.
        Professional contrarians avoid crowded trades and look for opposite opportunities.
        :param positioning_data_list: List of positioning data
        :param periods: Number of periods to analyze
        :return: Tuple of (crowding_level, contrarian_opportunity, risk_level)
        """
        if len(positioning_data_list) < periods:
            return "MODERATE", False, RiskLevel.MEDIUM

        # Extract positioning metrics
        long_positions = []
        short_positions = []

        for data in positioning_data_list[-periods:]:
            if hasattr(data, 'long_interest') and data.long_interest is not None:
                long_positions.append(data.long_interest)
            if hasattr(data, 'short_interest') and data.short_interest is not None:
                short_positions.append(data.long_interest)

        if len(long_positions) < 10:
            return "MODERATE", False, RiskLevel.MEDIUM

        # Calculate average positioning
        avg_long = sum(long_positions) / len(long_positions)
        avg_short = sum(short_positions) / len(short_positions) if short_positions else 0

        # Net positioning
        net_positioning = avg_long - avg_short

        # Identify crowding
        if net_positioning > 70: #Extremely long
            crowding_level = "EXTREME_LONG"
            contrarian_opportunity = "SHORT"
            risk_level = RiskLevel.HIGH
        elif net_positioning > 50: # Very long
            crowding_level = "VERY_LONG"
            contrarian_opportunity = "SHORT"
            risk_level = RiskLevel.MEDIUM
        elif net_positioning < -70: # Extremely short
            crowding_level = "EXTREME_SHORT"
            contrarian_opportunity = "LONG"
            risk_level = RiskLevel.HIGH
        elif net_positioning < -50: # Very short
            crowding_level = "VERY_SHORT"
            contrarian_opportunity = "LONG"
            risk_level = RiskLevel.MEDIUM
        else: # Moderate positioning
            crowding_level = "MODERATE"
            contrarian_opportunity = "NONE"
            risk_level = RiskLevel.LOW

        return crowding_level, contrarian_opportunity, risk_level

    def mean_reversion_extremes(self, price_data_list, lookback_period=50, z_score_threshold=2.0):
        """
        Identify mean reversion opportunities at extreme price levels.
        Professional contrarians look for statistical extremes for reversal trades.
        :param price_data_list: List of price data
        :param lookback_period: Lookback period for mean calculation
        :param z_score_threshold: Z-score threshold for extreme levels
        :return: Tuple of (extreme_type, z_score, contrarian_signal_ strength)
        """
        if len(price_data_list) < lookback_period:
            return "NORMAL", 0, Signal.HOLD, 0

        # Extract prices
        prices = [data.price.close_price for data in price_data_list[-lookback_period:] if data.price.close_price > 0]

        if len(prices) < 20:
            return "NORMAL", 0, Signal.HOLD, 0

        mean_price = sum(prices) / len(prices)
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return "NORMAL", 0, Signal.HOLD, 0

        # Calcuate current z-score
        current_price = prices[-1]
        z_score = (current_price - mean_price) / std_dev

        # Identify extremes
        if z_score > z_score_threshold: # Overbought extreme
            extreme_type = "OVERBOUGHT"
            contrarian_signal = Signal.SELL
            strength = min(100, z_score * 20) # Scale to 0-100
        elif z_score < -z_score_threshold:
            extreme_type = "OVERSOLD"
            contrarian_signal = Signal.BUY
            strength = min(100, abs(z_score * 20))
        else: # Normal range
            extreme_type = "NORMAL"
            contrarian_signal = Signal.HOLD
            strength = 0

        return extreme_type, z_score, contrarian_signal, strength

    def contrary_momentum_divergence(self, price_data_list, momentum_data_list, periods=20):
        """
        Identify divergence between price trend and momentum for contrarian signals.
        Professional contrarians use momentum divergence to spot trend exhaustion.
        :param price_data_list: List of price data
        :param momentum_data_list: List of momentum data
        :param periods: Number of periods to analyze
        :return: Tuple of (divergence_type, quality, contrarian_signal)
        """
        if len(price_data_list) < periods or len(momentum_data_list) < periods:
            return "NORMAL", 0, Signal.HOLD

        # Calculate price trend
        price_prices = [data.price.close_price for data in price_data_list[-periods:] if data.price.close_price > 0]
        if len(price_prices) >= 2 and price_prices[0] > 0:
            price_trend = (price_prices[-1] - price_prices[0]) / price_prices[0]
        else:
            price_trend = 0

        # Calculate momentum trend
        momentum_values = []
        for data in momentum_data_list[-periods:]:
            if hasattr(data, "momentum_value") and data.momentum_value is not None:
                momentum_values.append(data.momentum_value)

        if len(momentum_values) >= 2:
            momentum_trend = (momentum_values[-1] - momentum_values[0]) / momentum_values[0] if momentum_values[0] != 0 else 0
        else:
            momentum_trend = 0

        # Identify divergence
        if price_trend > 0.05 and momentum_trend < 0: # Price making new highs, momentum making lower highs
            divergence_type = "BULLISH_DIVERGENCE"
            quality = min(100, (price_trend - momentum_values) * 500)
            contrarian_signal = Signal.SELL
        elif price_trend < -0.05 and momentum_trend > 0: # Price making new lows, momentum making higher lows
            divergence_type = "BEARISH_DIVERGENCE"
            quality = min(100, (momentum_trend - price_trend) * 500)
            contrarian_signal = Signal.BUY
        else:
            divergence_type = "NONE"
            quality = 0
            contrarian_signal = Signal.HOLD

        return divergence_type, quality, contrarian_signal

    def contrarian_timing_filter(self, volatility_data_list, volume_data_list, price_data_list, periods=15):
        """
        Timing filter for contrarian trades based on volatility and volume patterns.
        Professional contrarians time their entries carefully.
        :param volatility_data_list: List of volatility data
        :param volume_data_list: List of volume data
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Tuple of (timing)quality, entry_signal, confirmation)
        """
        if (len(volume_data_list) < periods or len(volume_data_list) < periods) or len(price_data_list) < periods:
            return 0, Signal.HOLD, False

        # Extract volatility data
        volatility_values = [data.volatility_value for data in volatility_data_list[-periods:]
                             if hasattr(data,'volatility_value') and data.volatility_value is not None]

        # Extract volume data
        volume_values = [data.volume for data in volume_data_list[-periods:] if data.volume is not None]

        # Extract price data
        price_prices = [data.price.close_price for data in price_data_list[-periods:] if data.price.close_price > 0]

        if (len(volatility_values) < 5 or len(volume_values) < 5 or len(price_prices) < 5):
            return 0, Signal.HOLD, False

        # Check for volatility contraction (good for contrarian entries)
        current_volatility = volatility_values[-1]
        avg_volatility = sum(volatility_values[:-5]) / len(volatility_values[:-5]) if len(volatility_values) >= 10 else current_volatility

        volatility_contraction = current_volatility < avg_volatility * 0.8

        # Check for volume pattern (increasing volume on contrarian move)
        current_volume = volume_values[-1]
        avg_volume = sum(volume_values[-5:]) / 5

        volume_confirmation = current_volume > avg_volume * 1.2

        # Check price action confirmation
        if len(price_prices) >= 3:
            # Look for reversal patterns
            recent_returns =[(price_prices[i]) - price_prices[i-1] / price_prices[i-1] for i in range(1, len(price_prices)-1)]

            # Check if recent move confirms contrarian singal
            if len(recent_returns) >= 3:
                recent_trend = sum(recent_returns[-3:]) # Last 3 periods
                confirmation = abs(recent_trend) > 0.01 # At least 1$ move
            else:
                confirmation = False
        else:
            confirmation = False

        # Calculate timing quality
        quality_factor = [
            40 if volatility_contraction else 0,    # 40% weight for volatility
            30 if volume_confirmation else 0,       # 30% weight for volume
            30 if confirmation else 0,              # 30% weight for price confirmation
        ]

        timing_quality = sum(quality_factor)

        # Entry signal based on quality
        if timing_quality > 80:
            entry_signal = Signal.BUY if recent_returns[-1] > 0 else Signal.SELL if recent_returns[-1] < 0 else Signal.HOLD
        elif timing_quality > 60:
            entry_signal = Signal.BUY if recent_returns[-1] > 0 else Signal.SELL if recent_returns[-1] < 0 else Signal.HOLD
        else:
            entry_signal = Signal.HOLD

        return timing_quality, entry_signal, confirmation