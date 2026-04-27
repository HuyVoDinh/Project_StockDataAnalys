from src.enums.trend import Trend, MarketState
from src.enums.risk import RiskLevel
from src.enums.signal import Signal

class MarketRegimeFilter:
    def __init__(self):
        pass

    def market_regime_classification(self, market_index_data_list, sector_data_dict, periods=50):
        """
        Classify the current market regime based on multiple factors
        Professional traders adapt their strategies based on market regime
        :param market_index_data_list: List of market index data
        :param sector_data_dict: Dictionary of sector data
        :param periods: Number of periods to analyze
        :return: Tuple of (market_regime, volatility_regime, sector_rotation)
        """
        if len(market_index_data_list) < periods:
            return MarketState.EARLY_TREND, Trend.Weak, {}

        recent_data = market_index_data_list[-periods:]

        # Calculate market trend
        prices = [data.price.close_price for data in recent_data]
        if len(prices) >= 20:
            ma20 = sum(prices[-20:]) / 20
            current_price = prices[-1]

            # Trend strength
            trend_ratio = (current_price - ma20) / ma20 if ma20 > 0 else 0

            if trend_ratio > 0.05: # Bull market (5% above MA20)
                market_regime = MarketState.MID_TREND if trend_ratio > 0.1 else MarketState.EARLY_TREND
            elif trend_ratio < -0.05: # Bear market (5% below MA220)
                market_regime = MarketState.LATE_TREND
            else: # Sideway market
                market_regime = MarketState.EARLY_TREND
        else:
            market_regime = MarketState.EARLY_TREND

        # Calculate market volatility
        if len(prices) >= 10:
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] > 0]
            if returns:
                avg_return = sum(returns) / len(returns)
                variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
                std_dev = variance ** 0.5

                if std_dev > 0.02: # High volatility (>2% daily)
                    volatility_regime = Trend.Fomo
                elif std_dev < 0.005: # Low volatility (<0.5% daily)
                    volatility_regime = Trend.Weak
                else: # Moderate volatility
                    volatility_regime = Trend.Good
            else:
                volatility_regime = Trend.Weak
        else:
            volatility_regime = Trend.Weak

        # Sector rotation analysis
        sector_strength = {}
        if sector_data_dict:
            for sector, data_list in sector_data_dict.items():
                if len(data_list) >= 10:
                    sector_prices = [data.price.close_price for data in data_list[-10:]]
                    if len(sector_prices) >= 2 and sector_prices[0] > 0:
                        sector_return = (sector_prices[-1] - sector_prices[0]) / sector_prices[0]
                        if sector_return > 0.05: # Strong sector (>5% return)
                            sector_strength[sector] = Trend.Strong_Up
                        elif sector_return > 0.02: # Good sector (>2% return)
                            sector_strength[sector] = Trend.Up
                        elif sector_return < -0.05: # Weak sector (<-5% return)
                            sector_strength[sector] = Trend.Strong_Down
                        elif sector_return < -0.02: # Poor sector (<-2% return)
                            sector_strength[sector] = Trend.Down
                        else: # Neutral sector
                            sector_strength[sector] = Trend.Sideway

        return market_regime, volatility_regime, sector_strength

    def market_breadth_analysis(self, stock_data_list, market_trend, periods=20):
        """
        Analyze market breadth to confirm market trend
        Professional traders use this to validata market direction
        :param stock_data_list: List of stock data
        :param market_trend: Current market trend
        :param periods: Number of periods to analyze
        :return: Tuple of (breadth_ratio, confirmation, quality)
        """
        if not stock_data_list or len(stock_data_list) < 10:
            return 0, False, 0

        advancing = 0
        declining = 0
        unchanged = 0

        # Analyze recent performance of stocks
        for stock_data in stock_data_list[:50]: # Limit to first 5- stocks for performance
            if hasattr(stock_data, 'company_data') and len(stock_data.company_data) >= periods:
                recent_data = stock_data.company_data[-periods:]
                if len(recent_data) >= 2:
                    current_price = recent_data[-1].price.close_price
                    previous_price = recent_data[-2].price.close_price

                    if current_price > previous_price * 1.01: # Up more than 1%
                        advancing += 1
                    elif current_price < previous_price * 0.99: # Down more than 1%
                        declining += 1
                    else:
                        unchanged += 1

        total = advancing + declining + unchanged
        if total == 0:
            return 0, False, 0

        breadth_ratio = advancing / total if total > 0 else 0

        # Confirmation based on market trend
        if market_trend in [Trend.Up, Trend.Strong_Up]:
            confirmation = breadth_ratio > 0.6 # 60%+ advancing
        elif market_trend in [Trend.Down, Trend.Strong_Down]:
            confirmation = breadth_ratio < 0.4 # 40%+ declining
        else:
            confirmation = 0.4 <= breadth_ratio <= 0.6 # Balanced market

        # Quality based on participation
        quality = min(100, (total / len(stock_data_list)) * 100) if stock_data_list else 0

        return breadth_ratio, confirmation, quality

    def risk_regime_analysis(self, market_index_data_list, volatility_threshold=0.02):
        """
        Analyze the current risk regime in the market
        Professional traders adjust risk exposure based on market risk
        :param market_index_data_list: List of market index data
        :param volatility_threshold: Threshold for high volatility
        :return: Tuple of (risk_regime, risk_level, recommendation)
        """
        if len(market_index_data_list) < 10:
            return Trend.Sideway, RiskLevel.MEDIUM, "HOLD"

        recent_data = market_index_data_list[-10:]
        prices = [data.price.close_price for data in recent_data]

        if len(prices) < 2:
            return Trend.Sideway, RiskLevel.MEDIUM, "HOLD"

        # Calculate market volatility
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] > 0]
        if not returns:
            return Trend.Sideway, RiskLevel.MEDIUM, "HOLD"

        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5

        # Risk regime classification
        if std_dev > volatility_threshold * 2: # Very high volatility
            risk_regime = Trend.Fomo
            risk_level = RiskLevel.VERY_HIGH
            recommendation = "REDUCE_RISK"
        elif std_dev > volatility_threshold: #  high volatility
            risk_regime = Trend.Good
            risk_level = RiskLevel.HIGH
            recommendation = "MODERATE_RISK"
        elif std_dev > volatility_threshold * 0.5: # Very low volatility
            risk_regime = Trend.Weak
            risk_level = RiskLevel.VERY_LOW
            recommendation = "INCREASE_RISK"
        else: # Moderate volatility
            risk_regime = Trend.Sideway
            risk_level = RiskLevel.MEDIUM
            recommendation = "HOLD_RISK"

        return risk_regime, risk_level, recommendation

    def regime_adaptation_strategy(self, market_regime, volatility_regime, risk_regime):
        """
        Provide strategy adaptation recommendation based on market regime
        Professional traders use this to adjust their approach
        :param market_regime: Current market regime
        :param volatility_regime: Current volatility regime
        :param risk_regime: Current risk regime
        :return: Tuple of (strategy_type, position_sizing, risk_management)
        """
        # Strategy type based on regime combination
        if market_regime == MarketState.MID_TREND and volatility_regime == Trend.Good and risk_regime == Trend.Sideway:
            strategy_type = "TREND_FOLLOWING"
            position_sizing = "AGGRESSIVE"
            risk_management = "MODERATE"
        elif market_regime == MarketState.LATE_TREND and volatility_regime == Trend.Fomo and risk_regime == Trend.Fomo:
            strategy_type = "DEFENSIVE"
            position_sizing = "CONSERVATIVE"
            risk_management = "STRICT"
        elif market_regime == MarketState.EARLY_TREND and volatility_regime == Trend.Weak and risk_regime == Trend.Weak:
            strategy_type = "BREAKOUT"
            position_sizing = "MODERATE"
            risk_management = "FLEXIBLE"
        else:
            strategy_type = "MIXED"
            position_sizing = "MODERATE"
            risk_management = "BALANCED"

        return strategy_type, position_sizing, risk_management

    def market_health_indicator(self, market_index_data_list, volume_data_list, periods=30):
        """
        Calculate overall market health indicator
        Professional traders use this as a macro filter
        :param market_index_data_list: List of market index data
        :param volume_data_list: List of market volume data
        :param periods: Number of periods to analyze
        :return: Tuple of (health_score, health_status, components)
        """
        if len(market_index_data_list) < periods or len(volume_data_list) < periods:
            return 0, "NEUTRAL", {}

        recent_prices = [data.price.close_price for data in market_index_data_list[-periods:]]
        recent_volumes = [data.volume for data in market_index_data_list[-periods:] if data.volume is not None]

        if len(recent_prices) < 10 or len(recent_volumes) < 10:
            return 0, "NEUTRAL", {}

        # Price trend health (40% weight)
        price_returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] for i in range(1, len(recent_prices)) if recent_prices[i-1] > 0]
        if price_returns:
            avg_price_return = sum(price_returns) / len(price_returns)
            price_health = min(100, max(0, (avg_price_return + 0.01) * 5000)) # Scale to 0-100
        else:
            price_health = 50

        # Volume health (30% weight)
        if len(recent_volumes) >= 5:
            recent_avg_volume = sum(recent_volumes[-5:]) / 5
            older_avg_volume = sum(recent_volumes[-10:-5]) / 5 if len(recent_volumes) >= 10 else recent_avg_volume
            volume_trend = (recent_avg_volume - older_avg_volume) / older_avg_volume if older_avg_volume > 0 else 0
            volume_health = min(100, max(0, (volume_trend + 0.01) * 500)) # Scale to 0-100
        else:
            volume_health = 50

        # Momentum health (30% weight)
        if len(recent_prices) >= 10:
            short_term_return = (recent_prices[-1] - recent_prices[-5]) / recent_prices[-5] if recent_prices[-5] > 0 else 0
            long_term_return = (recent_prices[-1] - recent_prices[-10]) / recent_prices[-10] if recent_prices[-10] > 0 else 0
            momentum_alignment = 1 if (short_term_return > 0 and long_term_return > 0) else (-1 if (short_term_return < 0 and long_term_return < 0) else 0)
            momentum_health = 50 + (momentum_alignment * 25) # 25, 50, or 75
        else:
            momentum_health = 50

        # Overall health score
        health_score = (price_health * 0.4) + (volume_health * 0.3) + (momentum_health * 0.3)

        # Health status
        if health_score > 70:
            health_status = "HEALTHY"
        elif health_score > 30:
            health_status = "NEUTRAL"
        else:
            health_status = "UNHEALTHY"

        # Components breakdown
        components = {
            "price_health": price_health,
            "volume_health": volume_health,
            "momentum_health": momentum_health,
        }
        return health_score, health_status, components