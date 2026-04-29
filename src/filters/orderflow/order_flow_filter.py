from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.liquidity import Liquidity

class OrderFlowFilter:
    def __init__(self):
        pass

    def calculate_volume_weighted_price(self, trade_data_list, periods=50):
        """
        Calculate volume-weighted average price to detect smart money flow
        Professional traders use VWAP to identify institutional activity
        :param trade_data_list: List of trade data
        :param periods: Number of periods to analyze
        :return: Tuple of (vwap, price_deviation, flow_direction)
        """
        if len(trade_data_list) < periods:
            return 0, 0, "NEUTRAL"

        # Extract trades with price and volume
        trades = []
        for trade in trade_data_list[-periods:]:
            if (hasattr(trade, "price") and hasattr(trade, "size") and
            trade.price > 0 and trade.size is not None and trade.size > 0):
                trades.append(trade)

        if len(trades) < 10:
            return 0, 0, "NEUTRAL"

        # Calculate VWAP
        total_value = sum(price * volume for price, volume in trades)
        total_volume = sum(volume for _, volume in trades)

        if total_volume == 0:
            return 0, 0, "NEUTRAL"

        vwap = total_value / total_volume

        # Calculate price deviation from VWAP
        current_price = trades[-1][0]
        price_deviation = (current_price - vwap) / vwap if vwap > 0 else 0

        # Determine flow direction
        if price_deviation > 0.01: # 1% above VWAP
            flow_direction = "ABOVE_VWAP"
        elif price_deviation < -0.01: # 1% below VWAP
            flow_direction = "BELOW_VWAP"
        else:
            flow_direction = "NEAR_VWAP"

        return vwap, price_deviation, flow_direction

    def detect_cumulative_delta(self, trade_data_list, periods=100):
        """
        Calculate cumulative delta to measure buying vs selling pressure
        Professional traders use delta to identify order flow imbalance
        :param trade_data_list: List of trade data
        :param period: Number of periods to analyze
        :return: Tuple of (cumulative_delta, delta_ratio, market_bias)
        """
        if len(trade_data_list) < periods:
            return 0, 0, "NEUTRAL"

        buy_volume = 0
        sell_volume = 0

        # Analyze trades for buying/selling pressure
        for i in range(1, len(trade_data_list[-periods:])):
            current_trade = trade_data_list[-periods:][i]
            previous_trade = trade_data_list[-periods:][i-1]

            if (hasattr(current_trade, "price") and hasattr(current_trade, "size") and
            hasattr(previous_trade, "price") and current_trade.price > 0 and
            previous_trade.price > 0 and current_trade.size is not None):
                price_change = current_trade.price - previous_trade.price

                if price_change > 0: # Price increased, likely buyer initiated
                    buy_volume += current_trade.size
                elif price_change < 0: # Price decreased, likely seller initiated
                    sell_volume += current_trade.size
                else: # No price change, neutral
                    # Distribute evenly or use other heuristics
                    buy_volume += current_trade.size / 2
                    sell_volume += current_trade.size / 2

        total_volume = buy_volume + sell_volume
        if total_volume == 0:
            return 0, 0, "NEUTRAL"

        # Calculate cumulative delta
        cumulative_delta = buy_volume - total_volume

        # Calculate delta ratio
        delta_ratio = cumulative_delta / total_volume

        # Determine market bias
        if delta_ratio > 0.1: # 10% buying pressure
            market_bias = "BULLISH"
        elif delta_ratio < -0.1: # 10% selling pressure
            market_bias = "BEARISH"
        else:
            market_bias = "NEUTRAL"

        return cumulative_delta, delta_ratio, market_bias

    def analyze_footprint_charts(self, trade_data_list, price_levels=10):
        """
        Analyze footprint chart patterns to identify key support/resistance
        Professional traders use footprint analysis for order flow insights
        :param trade_data_list: List of trade data
        :param price_levels: Number of price levels to analyze
        :return: Tuple of (key_levels, volume_profile, market_structure)
        """
        if len(trade_data_list) < 20:
            return [], {}, "NEUTRAL"

        # Group trades by price level
        price_volume_map = {}
        for trade in trade_data_list[-100:]: # Analyze last 100 trades
            if (hasattr(trade, "price") and hasattr(trade, "size") and
            trade.price > 0 and trade.size is not None):
                # Round price to nearest tick (simplified)
                rounded_price = round(trade.price, 2)

                if rounded_price not in price_volume_map:
                    price_volume_map[rounded_price] = 0
                price_volume_map[rounded_price] += trade.size

        if not price_volume_map:
            return [], {}, "NEUTRAL"

        # Identify key levels (high volume nodes)
        sorted_levels = sorted(price_volume_map.items(), key=lambda x: x[1], reverse=True)
        key_levels = [price for price, volume in sorted_levels[:price_levels]]

        # Create volume profile
        volume_profile = price_volume_map

        # Determine market structure
        if len(sorted_levels) >= 3:
            highest_volume_price = sorted_levels[0][0]
            second_highest_price = sorted_levels[1][0]
            third_highest_price = sorted_levels[2][0]

            # Check if levels are clustered (support/resistance zones)
            price_range = max(key_levels) - min(key_levels)
            avg_level_spacing = price_range / len(key_levels)

            if avg_level_spacing < (max(key_levels) - min(key_levels)) * 0.1:
                market_structure = "CONSOLIDATION"
            elif highest_volume_price > second_highest_price > third_highest_price:
                market_structure = "BULLISH_STACKING"
            elif highest_volume_price < second_highest_price < third_highest_price:
                market_structure = "BEARISH_STACKING"
            else:
                market_structure = "NEUTRAL"
        else:
            market_structure = "NEUTRAL"

        return key_levels, volume_profile, market_structure

    def detect_liquidity_voids(self, order_book_data_list, price_leves=20):
        """
        Detect liquidity voids that indicate potential breakout points
        Professional traders look for areas with little market depth
        :param order_book_data_list: List of order book data
        :param price_leves: Number of price levels to analyze
        :return: Tuple of (void_levels, void_intensity, breakout_potential)
        """
        if len(order_book_data_list) < 5:
            return [], 0, "LOW"

        current_order_book = order_book_data_list[-1]

        if not (hasattr(current_order_book, "bids") and hasattr(current_order_book, "asks")):
            return [], 0, "LOW"

        # Extract bid and ask levels
        bids = current_order_book.bids[:price_leves] if current_order_book.bids else []
        asks = current_order_book.asks[:price_leves] if current_order_book.asks else []

        if not bids or not asks:
            return [], 0, "LOW"

        # Calculate average volume per level
        bid_volumes = [volume for _, volume, _ in bids]
        ask_volumes = [volume for _, volume, _ in asks]

        if not bid_volumes or not ask_volumes:
            return [], 0, "LOW"

        avg_bid_volume = sum(bid_volumes) / len(bid_volumes)
        avg_ask_volume = sum(ask_volumes) / len(ask_volumes)
        avg_volume = (avg_bid_volume + avg_ask_volume) / 2

        if avg_volume == 0:
            return [], 0, "LOW"

        # Identify liquidity voids (levels with < 20% of average volume)
        void_levels = []
        for price, volume in bids:
            if volume < avg_volume * 0.2:
                void_levels.append(("BID", price, volume))

        for price, volume in asks:
            if volume < avg_volume * 0.2:
                void_levels.append(("ASK", price, volume))

        # Calculate void intensity
        void_intensity = min(100, len(void_levels) * 10) # Scale to 0-100

        # Assess breakout potential
        if len(void_levels) > 5:
            break_potential = "HIGH"
        elif len(void_levels) > 2:
            break_potential = "MEDIUM"
        else:
            break_potential = "LOW"

        return void_levels, void_intensity, break_potential

    def order_flow_imbalance(self, trade_data_list, time_window=30):
        """
        Calculate order flow imbalance over a specific time window
        Professional traders use this for short- term directional bias
        :param trade_data_list: List of trade data
        :param time_window: Time window in seconds for imbalance calculation
        :return: Tuple of (imbalance_ratio, buying_pressure, selling_pressure)
        """
        if len(trade_data_list) < 10:
            return 0, 0, 0

        # Filter trades within time window (assuming trades have timestamp)
        recent_trades = []
        for trade in trade_data_list[-50:]: # Check last 50 trades
            if hasattr(trade, "timestamp"):
                recent_trades.append(trade)

        if len(recent_trades) < 5:
            # Fallback to using all available trades
            recent_trades = trade_data_list[-10:] if len(trade_data_list) >= 10 else trade_data_list

        buying_volume = 0
        selling_volume = 0

        # Calculate buying vs selling volume
        for i in range(1, len(recent_trades)):
            current_trade = recent_trades[i]
            previous_trade = recent_trades[i - 1]

            if (hasattr(current_trade, "price") and hasattr(current_trade, "size") and
            hasattr(previous_trade,"price") and current_trade.price > 0 and
            previous_trade.price > 0 and current_trade.size is not None):
                price_change = current_trade.price - previous_trade.price

                if price_change > 0: # Buyer initiated
                    buying_volume += current_trade.size
                elif price_change < 0: # Seller initiated
                    selling_volume += current_trade.size
                # For no price change, we could use other methods but for simplicity, we'll distribute evenly
                else:
                    buying_volume += current_trade.size / 2
                    selling_volume += current_trade.size / 2

        total_volume = buying_volume + selling_volume
        if total_volume == 0:
            return 0, 0, 0

        # Calculate imbalance ratio (-1 to 1)
        imbalance_ratio = (buying_volume + selling_volume) / total_volume

        return imbalance_ratio, buying_volume, selling_volume

    def detect_institutional_activity(self, trade_data_list, volume_threshold_multiplier=5):
        """
        Detect institutional activity t hrough large trades and bloack traders
        Professional traders monitor for "elephant trades" that indicate smart money
        :param trade_data_list: List of trade data
        :param volume_threshold_multiplier: Multiplier for average volume to detect large trades
        :return: Tuple of (institutional_activity, activity_score, directional_bias)
        """
        if len(trade_data_list) < 20:
            return False, 0, "NEUTRAL"

        # Calculate average trade size
        trade_sizes = []
        for trade in trade_data_list[-100:]: # Last 100 trades
            if hasattr(trade, "size") and trade.size is not None:
                trade_sizes.append(trade.size)

        if len(trade_sizes) < 10:
            return False, 0, "NEUTRAL"

        avg_trade_size = sum(trade_sizes) / len(trade_sizes)

        # Identify large trades (institutional activity)
        large_trades = [size for size in trade_sizes if size > avg_trade_size * volume_threshold_multiplier]

        if len(large_trades) < 2:
            return False, 0, "NEUTRAL"

        # Calculate activity score
        activity_score = min(100, len(large_trades) * 15) # Scale to 0-100

        # Determine directional bias from large trades
        large_trade_prices = []
        for trade in trade_data_list[-100:]:
            if (hasattr(trade, "size") and hasattr(trade, "price") and
            trade.size is not None and trade.size > avg_trade_size * volume_threshold_multiplier):
                large_trade_prices.append(trade.price)

        if len(large_trade_prices) >= 2:
            price_trend = large_trade_prices[-1] - large_trade_prices[0]
            if price_trend > 0:
                directional_bias = "BULLISH"
            elif price_trend < 0:
                directional_bias = "BEARISH"
            else:
                directional_bias = "NEUTRAL"
        else:
            directional_bias = "NEUTRAL"

        return True, activity_score, directional_bias














