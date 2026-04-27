from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.enums.liquidity import Liquidity, Cash_Flow, Volume

class LiquidityStressFilter:
    def __init__(self):
        pass

    def liquidity_depth_analysis(self, order_book_data_list, price_levels=5):
        """
        Analyze liquidity depth to assess market impact and slippage risk
        Professional traders evaluate liquidity before entering large positions.
        :param order_book_data_list: List of order book data
        :param price_levels: Number of price levels to analyze
        :return: Tuple of (liquidity_depth_score, market_impact, slippage_risk)
        """
        if len(order_book_data_list) < price_levels:
            return 0, 0, RiskLevel.HIGH

        current_order_book = order_book_data_list[-1]

        # Extract bid and ask data
        if (hasattr(current_order_book, 'bids') and hasattr(current_order_book, 'asks') and
        current_order_book.bids and current_order_book.asks):
            bids = current_order_book.bids[:price_levels]
            asks = current_order_book.asks[:price_levels]
        else:
            return 0, 0, RiskLevel.HIGH

        # Calculate liquidity depth
        total_bid_volume = sum(volume for _, volume in bids)
        total_ask_volume = sum(volume for _, volume in asks)
        total_liquidity = total_bid_volume + total_ask_volume

        if total_liquidity == 0:
            return 0, 0, RiskLevel.HIGH

        # Calculate liquidity depth score (0 - 100)
        # Higher score for more balanced and deeper liquidity
        bid_ask_ratio = min(total_bid_volume, total_ask_volume) / max(total_bid_volume, total_ask_volume)
        liquidity_depth_score = min(100, (total_liquidity / 1000000) * bid_ask_ratio * 50) # Scale appropriately

        # Calculate market impact
        # Assuming a hypothetical trader size
        trade_size = total_liquidity * 0.01 # 1% of available liquidity
        if trade_size <= min(total_bid_volume, total_ask_volume):
            market_impact = trade_size / min(total_bid_volume, total_ask_volume)
        else:
            market_impact = 1.0 # Maximum impact

        # Asses slippage risk
        if liquidity_depth_score > 80:
            slippage_risk = RiskLevel.LOW
        elif liquidity_depth_score > 50:
            slippage_risk = RiskLevel.MEDIUM
        else:
            slippage_risk = RiskLevel.HIGH

        return liquidity_depth_score, market_impact, slippage_risk

    def trading_volume_stress_test(self, volume_data_list, atr_data_list, periods=30):
        """
        Stress test trading volume against normal market conditions
        Professional traders asses if volume can support their trading activity
        :param volume_data_list: List of volume data
        :param atr_data_list: List of ATR data
        :param periods: Number of periods to analyze
        :return: Tuple of (volume_capacity, stress_level, trading_recommendation)
        """
        if len(volume_data_list) < periods or len(atr_data_list) < periods:
            return 0, RiskLevel.HIGH, "AVOID"

        # Extract volume and ATR data
        volumes = [data.volume for data in volume_data_list[-periods:] if data.volume is not None]
        atrs = [data.ATR_14 for data in atr_data_list[-periods:] if data.ATR_14 is not None]

        if len(volumes) < 10 or len(atrs) < 10:
            return 0, RiskLevel.HIGH, "AVOID"

        # Calculate average volume and ATR
        avg_volume = sum(volumes) / len(volumes)
        avg_atr = sum(atrs) / len(atrs)

        if avg_volume == 0 or avg_atr == 0:
            return 0, RiskLevel.HIGH, "AVOID"

        # Calculate volume/ATR ratio (volume per unit of price movement)
        volume_atr_ratio = avg_volume / avg_atr

        # Asses volume capacity (ability to absorb trading activity)
        # Higher ratio indicates better capacity
        volume_capacity = min(100, volume_atr_ratio / 1000) # Scale apropriately

        # Calculate stress level
        if volume_capacity > 70:
            stress_level =  RiskLevel.LOW
            recommendation = "ACCEPT"
        elif volume_capacity > 40:
            stress_level = RiskLevel.MEDIUM
            recommendation = "CAUTION"
        else:
            stress_level = RiskLevel.HIGH
            recommendation = "AVOID"

        return volume_capacity, stress_level, recommendation

    def liquidity_shock_simulation(self, price_data_list, volume_data_list, shock_magnitude=0.1):
        """
        Simulate liquidity shock scenarios to test position resilience
        Professional traders stress test their positions under adverse conditions
        :param price_data_list:List of price data
        :param volume_data_list: List of volume data
        :param shock_magnitude: Magnitude of price shock to simulate (e.g., 0.1 = 10%)
        :return: Tuple of (shock_impact, resilience_score, risk_exposure)
        """
        if len(price_data_list) < 10 or len(volume_data_list) < 10:
            return 0, 0, RiskLevel.HIGH

        # Extract recent data
        recent_prices = [data.price.close_price for data in price_data_list[-10:] if data.price.close_price > 0]
        recent_volumes = [data.volume for data in volume_data_list[-10:] if data.volume is not None]

        if len(recent_prices) < 5 or len(recent_volumes) < 5:
            return 0, 0, RiskLevel.HIGH

        # Calculate price volatility
        avg_price = sum(recent_prices) / len(recent_prices)
        price_variance = sum((p - avg_price) ** 2 for p in recent_prices) / len(recent_prices)
        price_std = price_variance ** 0.5
        price_volatility = price_std / avg_price if avg_price > 0 else 0

        # Calculate volume volatility
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        volume_variance = sum((v - avg_volume) ** 2 for v in recent_volumes) / len(recent_volumes)
        volume_std = volume_variance ** 0.5
        volume_volatility = volume_std / avg_volume if avg_volume > 0 else 0

        # Simulate price shock impact
        # Shock impact is higher when volatility is low (less prepared for shocks)
        shock_impact = shock_magnitude * (1 / (1 + price_volatility)) * (1 / (1 * volume_volatility))

        # Calculate resilience score
        # Higher resilience when there's high liquidity and low volatility
        liquidity_score = min(100, avg_volume / 100000) # Scale volume to 0-100
        stability_score = max(0, 100 - (price_volatility * 1000)) # Inverse of volatility
        resilience_score = (liquidity_score * 0.6) + (stability_score * 0.4)

        if shock_impact < 0.05 and resilience_score > 70:
            risk_exposure = RiskLevel.LOW
        elif shock_impact < 0.1 and resilience_score > 50:
            risk_exposure = RiskLevel.MEDIUM
        else:
            risk_exposure = RiskLevel.HIGH

        return shock_impact, resilience_score, risk_exposure

    def market_maker_liquidity_assessment(self, spread_data_list, volume_data_list, periods=25):
        """
        Assess merket maker liquidity based on spreads and volume patterns
        Professional traders evaluate market quality for execution
        :param spread_data_list: List of spread data
        :param volume_data_list: List of volume data
        :param periods: Number of periods to analyze
        :return: Tuple of (market_quality, execution_cost, liquidity_rating)
        """
        if len(spread_data_list) < periods or len(volume_data_list) < periods:
            return 0, 0, Liquidity.Weak

        # Extract spread and volume data
        spreads = [data.spread for data in spread_data_list[-periods:] if data.spread is not None]
        volumes = [data.volume for data in volume_data_list[-periods:] if data.volume is not None]

        if len(spreads) < 10 or len(volumes) < 10:
            return 0, 0, Liquidity.Weak

        # Calculate average spread and volume
        avg_spread = sum(spreads) / len(spreads)
        avg_volume = sum(volumes) / len(volumes)

        if avg_volume == 0:
            return 0, 0, Liquidity.Weak

        # Calculate market quality score (0-100)
        # Lower spreads and higher volumes indicate better quality
        spread_score = max(0, 100 - (avg_spread * 1000)) # Scale appropriately
        volume_score = min(100, avg_volume / 100000) # Scale volume
        market_quality = (spread_score * 0.7) + (volume_score * 0,3)

        # Calculate execution cost
        # Execution cost includes spread cost and market impact
        spread_cost = avg_spread * 0.5 # Half the spread as cost
        market_impact = 0.001 * (1000000 / avg_volume) if avg_volume > 0 else 0.01 # Inverse of volume
        execution_cost = spread_cost + market_impact

        # Determine liquidity rating
        if market_quality > 80:
            liquidity_rating = Liquidity.Good
        elif market_quality > 60:
            liquidity_rating = Liquidity.Weak
        else:
            liquidity_rating = Liquidity.Weak

        return market_quality, execution_cost, liquidity_rating

    def liquidity_regime_transition(self, liquidity_data_list, periods=40):
        """
        Analyze liquidity regime transitions for strategic positioning.
        Professional traders adapt to changing liquidity conditions
        :param liquidity_data_list: List of liquidity data
        :param periods: Number of periods to analyze
        :return: Tuple of (regime_change, transition_probability, positioning_recommendation)
        """
        if len(liquidity_data_list) < periods:
            return False, 0, "HOLD"

        # Extract liquidity metrics
        liquidity_values = []
        volume_values = []

        for data in liquidity_data_list[-periods:]:
            if hasattr(data, "liquidity_value") and data.liquidity_value is not None:
                liquidity_values.append(data.liquidity_value)
            if hasattr(data, "volume") and data.volume is not None:
                volume_values.append(data.volume)

        if len(liquidity_values) < 20 or len(volume_values) < 20:
            return False, 0, "HOLD"

        # Split data into two halves for regime comparison
        mid_point = len(liquidity_values) // 2
        early_liquidity = liquidity_values[:mid_point]
        late_liquidity = liquidity_values[mid_point:]
        early_volume = volume_values[:mid_point]
        late_volume = volume_values[mid_point:]

        # Calculate average liquidity and volume for each period
        avg_early_liquidity = sum(early_liquidity) / len(early_liquidity)
        avg_late_liquidity = sum(late_liquidity) / len(late_liquidity)
        avg_early_volume = sum(early_volume) / len(early_volume)
        avg_late_volume = sum(late_volume) / len(late_volume)

        # Detect regime change
        liquidity_change = (avg_late_liquidity - avg_early_liquidity) / avg_early_liquidity if avg_early_liquidity > 0 else 0
        volume_change = (avg_late_volume - avg_early_volume) / avg_late_volume if avg_late_volume > 0 else 0

        # Regime change if significant change in both liquidity and volume
        regime_change = abs(liquidity_change) > 0.2 or abs(volume_change) > 0.2

        # Calculate transition probability
        transition_probability = min(100, (abs(liquidity_change) + abs(volume_change)) * 250) # Scale to 0-100

        # Positioning recommendation based on regime change
        if regime_change:
            if liquidity_change > 0.2 and volume_change > 0.2:
                recommendation = "ACCUMULATED" # Improving liquidity
            elif liquidity_change < -0.2 and volume_change < -0.2:
                recommendation = "REDUCE"       # Deteriorating liquidity
            else:
                recommendation = "CAUTION"      # Mixed signals
        else:
            recommendation = "HOLD"             # Stable regime

        return regime_change, transition_probability, recommendation

    