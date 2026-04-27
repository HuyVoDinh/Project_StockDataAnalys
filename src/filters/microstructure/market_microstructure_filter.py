from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.liquidity import Liquidity

class MarketMicrostructureFilter:
    def __init__(self):
        pass

    def calculate_order_book_imbalance(self, bid_volume, ask_volume):
        """
        Calculate order book imbalance to detect buying/selling pressure
        Professional traders use this for short-term directional bias
        :param bid_volume: Total volume at bid levels
        :param ask_volume: Total volume at ask levels
        :return: Order book imbalance ratio (-1 to 1)
        """
        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            return 0

        imbalance = (bid_volume - ask_volume) / total_volume
        return max(-1, min(1, imbalance)) # Clamp to [-1, 1]

    def detect_liquidity_sweeps(self, trade_data_list, order_book_data_list, periods=50):
        """
        Detect liquidity sweep patterns that indicate institutional activity
        Professional traders watch for large orders that remove liquidity
        :param trade_data_list: List of trade data
        :param order_book_data_list: List of order book data
        :param periods: Number of periods to analyze
        :return: Tuple of (sweep_detected, sweep_intensity, direction_bias)
        """
        if len(trade_data_list) < periods or len(order_book_data_list) < periods:
            return False, 0, "NEUTRAL"

        # Extract trade sizes and prices
        large_trades = []
        for trade in trade_data_list[-periods:]:
            if hasattr(trade,'size') and hasattr(trade, 'price'):
                large_trades.append((trade.size, trade.price))

        if len(large_trades) < 5:
            return False, 0, "NEUTRAL"

        # Calculate average trade size
        avg_trade_size = sum(size for size, _ in large_trades) / len(large_trades)

        # Identify potential liquidity sweeps (trades 3x average size)
        sweep_trades = [(size, price) for size, price in large_trades if size > avg_trade_size * 3]

        if len(sweep_trades) < 2:
            return False, 0, "NEUTRAL"

        # Calculate sweep intensity
        sweep_intensity = min(100, len(sweep_trades) * 10) # Scale to 0-100

        # Determine directional bias based on sweep prices
        price_changes = []
        for i in range(1, len(sweep_trades)):
            _, prev_price = sweep_trades[i - 1]
            _, curr_price = sweep_trades[i]
            price_changes.append(curr_price - prev_price)

        if not price_changes:
            return True, sweep_intensity, "NEUTRAL"

        avg_price_change = sum(price_changes) / len(price_changes)

        if avg_price_change > 0:
            directional_bias = "BULLISH"
        elif avg_price_change < 0:
            directional_bias = "BEARISH"
        else:
            directional_bias = "NEUTRAL"

        return True, sweep_intensity, directional_bias

    def analyze_quote_stuffing(self, quote_data_list, periods=100):
        """
        Analyze for quote stuffing patterns that may indicate market manipulation
        Professional traders monitor for abnormal quoting activity
        :param quote_data_list: List of quote data
        :param periods: Number of periods to analyze
        :return: Tuple of (stuffing_detected, stuffing_intensity, market_impact)
        """
        if len(quote_data_list) < periods:
            return False, 0, "NEUTRAL"

        # Calculate quote frequence
        quote_count = len(quote_data_list[-periods:])
        avg_quotes_per_period = quote_count / periods

        # Normal quote rate (simplified assumption)
        normal_quote_rate = 10 # Quotes per period

        # Detect quote stuffing (excessive quoting)
        if avg_quotes_per_period > normal_quote_rate * 3: # 3x normal rate
            stuffing_detected = True
            stuffing_intensity = min(100, (avg_quotes_per_period / normal_quote_rate - 1) * 25)
        else:
            stuffing_detected = False
            stuffing_intensity = 0

        # Assess market impact
        if stuffing_intensity > 70:
            market_impact = "HIGH"
        elif stuffing_intensity > 40:
            market_impact = "MEDIUM"
        else:
            market_impact = "LOW"

        return stuffing_detected, stuffing_intensity, market_impact

    def detect_momentum_ignition(self, price_data_list, volume_data_list, periods=30):
        """
        Detect momentum ignition patterns that precede strong price moves
        Professional traders look for early signs of institutional accumulation.
        :param price_data_list: List of price data
        :param volume_data_list: List of volume data
        :param periods: Number of periods to analyze
        :return: Tuple of (ignition_detected, ignition_strength, expected_direction)
        """
        if len(price_data_list) < periods or len(volume_data_list) < periods:
            return False, 0, "NEUTRAL"

        # Extract recent data
        recent_prices = [data.price.close_price for data in price_data_list[-10:] if data.price.close_price > 0]
        recent_volumes = [data.volume for data in volume_data_list[-10:] if data.volume is not None]

        if len(recent_prices) < 5 or len(recent_volumes) < 5:
            return False, 0, "NEUTRAL"

        # Calculate price momentum
        if len(recent_prices) >= 2 and recent_prices[0] > 0:
            price_momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        else:
            price_momentum = 0

        # Calculate volume surge
        avg_volume = sum(recent_volumes[:-3]) / len(recent_volumes[:-3]) if len(recent_volumes) > 3 else 1
        recent_volume = sum(recent_volumes[:-3]) / 3 if len(recent_volumes) >= 3 else 0

        if avg_volume > 0:
            volume_surge = recent_volume / avg_volume
        else:
            volume_surge = 1

        # Detect momentum ignition (price + volume surge)
        if abs(price_momentum) > 0.02 and volume_surge > 2: # 2% price move + 2x volume
            ignition_detected = True
            ignition_strength = min(100, (abs(price_momentum) * 100 + volume_surge * 10))

            if price_momentum > 0:
                expected_direction = "UP"
            elif price_momentum < 0:
                expected_direction = "DOWN"
            else:
                expected_direction = "NEUTRAL"
        else:
            ignition_detected = False
            ignition_strength = 0
            expected_direction = "NEUTRAL"

        return ignition_detected, ignition_strength, expected_direction

    def analyze_spread_dynamics(self, bid_ask_data_list, periods=50):
        """
        Analyze bid-ask spread dynamics for market quality assessment
        Professional traders use spread analysis for execution quality
        :param bid_ask_data_list: List of bid-ask data
        :param periods: Number of periods to analyze
        :return: Tuple of (spread_quality, liquidity_condition, trading_signal)
        """
        if len(bid_ask_data_list) < periods:
            return "POOR", Liquidity.Weak, Signal.HOLD

        # Extract spreads
        spreads = []
        for data in bid_ask_data_list[-periods:]:
            if hasattr(data, 'bid') and hasattr(data, 'ask') and data.bid > 0 and data.ask > 0:
                spread = data.ask - data.bid
                spreads.append(spread)

        if len(spreads) < 10:
            return "POOR", Liquidity.Weak, Signal.HOLD

        # Calculate average spread
        avg_spread = sum(spreads) / len(spreads)

        # Calculate spread vp;ato;otu
        spread_variance = sum((s - avg_spread) ** 2 for s in spreads) / len(spreads)
        spread_std = spread_variance ** 0.5

        # Assess spread quality (lower is better)
        if avg_spread < 0.01 and spread_std < 0.005: # Tight spreads
            spread_quality = "EXCELLENT"
            liquidity = Liquidity.Good
        elif avg_spread < 0.02 and spread_std < 0.01: # Moderate spreads
            spread_quality = "GOOD"
            liquidity = Liquidity.Weak
        else:
            spread_quality = "POOR"
            liquidity = Liquidity.Weak

        # Generate trading signal based on spread dynamics
        recent_spreads = spreads[-5:]
        if len(recent_spreads) >= 2:
            spread_trend = recent_spreads[-1] - recent_spreads[0]

            if spread_trend < 0 and spread_quality in ["EXCELLENT", "GOOD"]: # Improving liquidity
                signal = Signal.BUY
            elif spread_trend > 0 and spread_quality == "POOR": # Deteriorating liquidity
                signal = Signal.SELL
            else:
                signal = Signal.HOLD
        else:
            signal = Signal.HOLD

        return spread_quality, liquidity, signal

    def microstructure_regime_detection(self, price_data_list, volume_data_list, trade_data_list, periods=100):
        """
        Detect market microstructure regimes for adaptive trading
        Professional traders adjust strategies based on market structure.
        :param price_data_list: List of price data
        :param volume_data_list: List of volume data
        :param trade_data_list: List of trade data
        :param periods: Number of periods to analyze
        :return: Tuple of (regime_type, regime_confidence, trading_recommendatin)
        """
        if (len(price_data_list) < periods or len(volume_data_list) < periods or len(trade_data_list) < periods):
            return "NORMAL", 50, "HOLD"

        # Calculate effective spread proxy
        price_changes = []
        for i in range(1, len(price_data_list[-periods:])):
            curr_price = price_data_list[-periods:][i].price.close_price
            prev_price = price_data_list[-periods:][i-1].price.close_price
            if curr_price > 0 and prev_price > 0:
                price_changes.append(abs(curr_price - prev_price) / prev_price)

        if len(price_changes) < 10:
            return "NORMAL", 50, "HOLD"

        avg_price_change = sum(price_changes) / len(price_changes)

        # Calculate volume participation rate
        volumes = [data.volume for data in volume_data_list[-periods:] if data.volume is not None]
        if len(volumes) >= 10:
            avg_volume = sum(volumes) / len(volumes)
            volume_volatility = (sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)) ** 0.5
            volume_stability = 1 / (1 + volume_volatility / avg_volume) if avg_volume > 0 else 0
        else:
            volume_stability = 0.5

        # Analyze trade size distribution
        trade_sizes = [data.size for data in trade_data_list[-periods:] if hasattr(data, 'size') and data.size is not None]
        if len(trade_sizes) >= 10:
            avg_trade_size = sum(trade_sizes) / len(trade_sizes)
            large_trades = sum(1 for size in trade_sizes if size > avg_trade_size * 2)
            large_trade_ratio = large_trades / len(trade_sizes)
        else:
            large_trade_ratio = 0

        # Determine regime based on metrics
        if avg_price_change > 0.02 and large_trade_ratio > 0.3: # High volatility + large trades
            regime_type = "VOLATILE_INSTITUTIONAL"
            regime_confidence = min(100, 80 + large_trade_ratio * 100)
            recommendation = "REDUCE_POSITION" # High volatility environment
        elif avg_price_change < 0.005 and volume_stability > 0.8: # Low volatility + stable volume
            regime_type = "STABLE_RETAIL"
            regime_confidence = min(100, 70 + volume_stability * 30)
            recommendation = "ACCUMULATE"  # Good environment for accumulation
        elif large_trade_ratio > 0.5: # Dominated by large trades
            regime_type = "INSTITUTIONAL_ACCUMULATION"
            regime_confidence = min(100, 85 + large_trade_ratio * 15)
            recommendation = "FOLLOW"  # Follow institutional flow
        else: # Normal market condition
            regime_type = "NORMAL"
            regime_confidence = 50
            recommendation = "HOLD"

        return regime_type, regime_confidence, recommendation