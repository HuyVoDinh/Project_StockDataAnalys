from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel

class OptionFilter:
    def __init__(self):
        pass

    def calculate_implied_volatility_rank(self, current_iv, historical_ivs):
        """
        Calculate implied volatility rank and percentile
        Professional options traders use IV rank to identify overpriced options
        :param current_iv: Current implied volatility
        :param historical_ivs: List of historical implied volatilities
        :return: Tuple of (iv_rank, iv_percentile)
        """
        if not historical_ivs or len(historical_ivs) == 0:
            return 50, 50 # Neutral values

        # IV Rank = (Current IV - 52-week low) / (52-week high - 52-week low) * 100
        iv_low = min(historical_ivs)
        iv_high = max(historical_ivs)

        if iv_high == iv_low:
            iv_rank = 50
        else:
            iv_rank = ((current_iv - iv_low) / (iv_high - iv_low)) * 100

        # IV Percentile = % of time IV was below current level
        below_current = sum(1 for iv in historical_ivs if iv < current_iv)
        iv_percentile = (below_current / len(historical_ivs)) * 100 if historical_ivs else 50

        return iv_rank, iv_percentile

    def options_pricing_anomaly(self, theoretical_price, market_price, bid, ask):
        """
        Identify options pricing anomalies and mispricings
        Professional traders look for discrepancies between theoretical and market prices
        :param theoretical_price: Current market price of option
        :param market_price: Current market price of option
        :param bid: Current bid price
        :param ask: Current ask price
        :return: Tuple of (anomaly_type, mispricing_ratio, trading_signal)
        """
        if theoretical_price <= 0 or market_price <= 0:
            return "NONE", 0, Signal.HOLD

        # Calculate mispricing ratio
        mispricing_ratio = (market_price - theoretical_price) / theoretical_price

        # Calculate bid-ask spread
        spread = ask - bid if bid > 0 and ask > 0 else 0

        # Identify anomalies
        if mispricing_ratio > 0.1 and spread < market_price * 0.02: # 10% overpriced, tight spread
            anomaly_type = "OVERPRICED"
            trading_signal = Signal.SELL
        elif mispricing_ratio < -0.1 and spread < market_price * 0.02: # 10% underpriced, tight spread
            anomaly_type = "UNDERPRICED"
            trading_signal = Signal.BUY
        else:
            anomaly_type = "NORMAL"
            trading_signal = Signal.HOLD

        return anomaly_type, mispricing_ratio, trading_signal

    def volatility_skew_analysis(self, strike_prices, implied_volatilities):
        """
        Analyze volatility skew for trading opportunities.
        Professional traders use skew to identify directional biases
        :param strike_prices: List of strike prices
        :param implied_volatilities: List of corresponding implied volatilities
        :return: Tuple of (skew_measure, directional_bias, skew_trading_signal)
        """
        if len(strike_prices) != len(implied_volatilities) or len(strike_prices) < 3:
            return 0, "NEUTRAL", Signal.HOLD

        # Calculate slope of IV vs strike price (skew)
        # This requires linear regression - simplified approach
        n = len(strike_prices)
        if n < 3:
            return 0, "NEUTRAL", Signal.HOLD

        # Calculate means
        mean_strike = sum(strike_prices) / n
        mean_iv = sum(implied_volatilities) / n

        # Calculate slope (skew)
        numerator = sum((strike_prices[i] - mean_strike) * implied_volatilities[i] - mean_iv for i in range(n))
        denominator = sum((strike_prices[i] - mean_strike) ** 2 for i in range(n))

        if denominator == 0:
            skew_measure = 0
        else:
            skew_measure = numerator / denominator

        # Determine directioal bias
        if skew_measure > 0.05: # positive skew - higher IV for higher strikes
            directional_bias = "BEARISH"
            trading_signal = Signal.SELL # Sell calls, buy puts
        elif skew_measure < -0.05: # Negative skew - higher IV for lower strikes
            directional_bias = "BULLISH"
            trading_signal = Signal.BUY  # Buy calls, sell puts
        else:
            directional_bias = "NEUTRAL"
            trading_signal = Signal.HOLD

        return skew_measure, directional_bias, trading_signal

    def options_liquidity_assessment(self, bid, ask, volume, open_interest):
        """
        Assess options liquidity for execution quality
        Professional traders evaluate options liquidity before trading
        :param bid: Current bid
        :param ask: Current ask
        :param volume: Current trading volume
        :param open_interest: Current open interest
        :return: Tuple of (liquidity_score, execution_quality, trading_recommendation)
        """
        if bid <= 0 or ask <= 0:
            return 0, "POOR", "AVOID"

        # Calculate spread as percentage
        spread_pct = (ask - bid) / ((ask + bid) / 2 if (ask + bid) > 0 else 1)

        # Calculate liquidity metrics
        # Higher volume and open interest indicate better liquidity
        volume_score = min(100, volume / 100) # Scale volume
        oi_score = min(100, open_interest / 1000) # Scale open interest
        spread_score = max(0, 100 - (spread_pct * 1000)) # Inverse of spread

        # Overal liquidity score
        liquidity_score = (volume_score * 0.4) + (oi_score * 0.4) + (spread_score * 0.2)

        # Determine execution quality
        if liquidity_score > 80:
            execution_quality = "EXCELLENT"
            recommendation = "ACCEPT"
        elif liquidity_score > 60:
            execution_quality = "GOOD"
            recommendation = "ACCEPT"
        elif liquidity_score > 40:
            execution_quality = "FAIR"
            recommendation = "CAUTION"
        else:
            execution_quality = "POOR"
            recommendation = "AVOID"

        return liquidity_score, execution_quality, recommendation

    def expiration_risk_analysis(self, days_to_expirations, gamma, vega):
        """
        Analyze expiration-related risks for options positions
        Professional traders manage gamme and vega risks near expiration
        :param days_to_expirations: Days until option expiration
        :param gamma: Option gamme
        :param vega: Option vega
        :return: Tuple of (expiration_risk, risk_level, hedging_recommendation)
        """
        if days_to_expirations <= 0:
            return 0, RiskLevel.VERY_HIGH, "CLOSE_POSITION"

        # Calculate gamme risk (acceleration of delta changes)
        gamma_risk = abs(gamma) * (1 / days_to_expirations) if days_to_expirations > 0 else 0

        # Calculate vega risk (sensitivity to volatility changes)
        vega_risk = abs(vega) * (1 / days_to_expirations) if days_to_expirations > 0 else 0

        # Overall expiration risk
        expiration_risk = (gamma_risk * 0.7) + (vega_risk * 0.3)

        # Determine risk level
        if days_to_expirations <= 3:
            if expiration_risk > 0.1:
                risk_level = RiskLevel.VERY_HIGH
                recommendation = "CLOSE_POSITION"
            elif expiration_risk > 0.05:
                risk_level = RiskLevel.HIGH
                recommendation = "REDUCE_POSITION"
            else:
                risk_level = RiskLevel.MEDIUM
                recommendation = "MONITOR_CLOSELY"
        elif days_to_expirations <= 7:
            if expiration_risk > 0.15:
                risk_level = RiskLevel.HIGH
                recommendation = "REDUCE_POSITION"
            elif expiration_risk > 0.08:
                risk_level = RiskLevel.MEDIUM
                recommendation = "MONITOR_CLOSELY"
            else:
                risk_level = RiskLevel.LOW
                recommendation = "HOLD"
        else:
            if expiration_risk > 0.2:
                risk_level = RiskLevel.MEDIUM
                recommendation = "MONITOR_CLOSELY"
            else:
                risk_level = RiskLevel.LOW
                recommendation = "HOLD"

        return expiration_risk, risk_level, recommendation














