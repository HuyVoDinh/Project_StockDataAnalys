from src.filters.regime.regime_shift_filter import RegimeShiftFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.filters.momentum.momentum_filter import MomentumFilter
from src.filters.risk.risk_filter import RiskFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.filters.volatility.volatility_filter import VolatilityFilter
from src.models.company import CompanyData


class RegimeShiftSetup:
    def __init__(self):
        self.regime_filter = RegimeShiftFilter()
        self.volatility_filter = VolatilityFilter()
        self.momentum_filter = MomentumFilter()
        self.risk_filter = RiskFilter()

    def check_setup(self, company: CompanyData, volatility_data_list=None, trade_data_list=None):
        """
        Professional Regim Shift Setup
        This setup adapts to changing market conditions and regime transitions

        Key components:
        1. Volatility regime change detection
        2. Trend regime change identification
        3. Liquidity regime analysis
        4. Multi-factor regime transition signals
        5. Adaptive setup selection
        :param company:
        :param volatility_data_list:
        :param trade_data_list:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 30:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # Need volatility and trade data for regime analysis
        if not volatility_data_list:
            # Create mock volatility data from price data if not available
            volatility_data_list = self._create_volatility_data(company_data_list)

        if not trade_data_list:
            # Create mock trade data from volume data if not available
            trade_data_list = self._create_trade_date(company_data_list)

        volume_data_list = [data for data in company_data_list if hasattr(data,'volume') and data.volume is not None]

        # 1. Volatility regime change detection
        vol_change, vol_outlook, vol_transition_prob = self.regime_filter.detect_volatility_regime_change(volatility_data_list, short_window=15, long_window=45)

        # 2. Trend regime change identification
        trend_change, trend_type, trend_confidence = self.regime_filter.detect_trend_regime_change(company_data_list, window=35)

        # 3. Liquidity regime analysis
        liquidity_change, liquidity_condition, market_impact = self.regime_filter.detect_liquidity_regime_change(volume_data_list, trade_data_list, window=25)

        # 4. Multi-factor regime transition signals
        transition_signal, regime_outlook, composite_score = self.regime_filter.detect_regime_transition_signals(
            company_data_list, volume_data_list, volatility_data_list, window=30)

        # 5. Current market state assessment
        current_trend = self.trend_filter.price_momentum(company_data_list, periods=20)
        volatility_regime, volatility_trend, volatility_risk = self.volatility_filter.volatility_regime_analysis(company_data_list, periods=25)
        momentum_regime = self.momentum_filter.momentum_regime(company_data_list, periods=15)

        # 6. Adaptive strategy selection
        regime_signals = [
            ("VOLATILITY", vol_outlook, vol_transition_prob),
            ("TREND", trend_type, trend_confidence),
            ("LIQUIDITY", liquidity_condition, 80 if liquidity_change else 50) # Simplified score
        ]

        current_strategy = "DEFAULT"
        recommended_strategy, strategy_confidence, adjustment_reason = self.regime_filter.adaptive_strategy_selection(
            regime_signals, current_strategy
        )

        # 7. Entry signal generation based on regime analysis
        signal = Signal.HOLD
        direction = "NEUTRAL"

        # Combine regime signals for trading decision
        buy_signals = 0
        sell_signals = 0

        # Volatility regime signal
        if vol_outlook == "DECREASING": # Favorable for long positions
            buy_signals += 1
        elif vol_outlook == "INCREASING": # Favorable for short positions or volatility strategies
            sell_signals += 1

        # Trend regime signal
        if trend_type == "TRENDING":
            buy_signals += 1
        elif trend_type == "TRENDING_DOWN":
            sell_signals += 1
        elif trend_type == "MEAN_REVERTING":
            # Mean reversion signal depends on current price vs recent average
            recent_prices = [data.price.close_price for data in company_data_list[-10:] if data.price.open_price > 0]
            if len(recent_prices) >= 5 and recent_prices[0] > 0:
                avg_recent_price = sum(recent_prices) / len(recent_prices)
                if current_price > avg_recent_price * 1.02: # 2% above average
                    sell_signals += 1
                elif current_price < avg_recent_price * 0.98:
                    buy_signals += 1

        # Liquidity regime singal
        if liquidity_condition == "HIGH_INSTITUTIONAL":
            if market_impact == "BULLISH":
                buy_signals += 1
            elif market_impact == "BEARISH":
                sell_signals += 1
        elif liquidity_condition == "LOW_RETAIL":
            sell_signals += 1 # Retail-driven markets often reverse

        # Transition signal
        if transition_signal == "BUY":
            buy_signals += 1
        elif transition_signal == "SELL":
            sell_signals += 1
        elif transition_signal == "REDUCE":
            # Reduce position size in volatile regimes
            pass # Handled in position sizing

        # Market state confirmation
        if current_trend in [Trend.Up, Trend.Strong_Up]:
            buy_signals += 1
        elif current_trend in [Trend.Down, Trend.Strong_Down]:
            sell_signals += 1

        # Generate final signal
        signal_threshold = 3 # Need at least confirming signals

        if buy_signals >= signal_threshold and buy_signals > sell_signals:
            signal = Signal.BUY
            direction = "LONG"
        elif sell_signals >= signal_threshold and sell_signals > buy_signals:
            signal = Signal.SELL
            direction = "SHORT"
        else:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 8. Risk management based on regime analysis
        # Position sizing adjusted for regime conditions
        regime_risk_factor = self._calculate_regime_risk_factor(volatility_risk, liquidity_condition, trend_confidence)

        # Base position size on signal strength and regime quality
        signal_strength = max(buy_signals, sell_signals)
        position_sizing_factor = min(1.0, (signal_strength / 5) * (composite_score / 100) * regime_risk_factor)

        # Adjust for recommended strategy
        if recommended_strategy == "MEAN_REVERSION":
            position_sizing_factor *= 0.8 # Lower size for mean reversion
        elif recommended_strategy == "VOLATILITY_BREAKOUT":
            position_sizing_factor *= 1.2 # Higher size for breakout strategies
        elif recommended_strategy == "TREND_FOLLOWING":
            position_sizing_factor *= 1.0 # Standard size for trend following

        # Stop loss based on regime conditions and volatility
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            # Adjust stop distance based on volatility regime
            if volatility_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                stop_multiplier = 3.0 # Wider stop in high volatility
            elif volatility_risk == RiskLevel.LOW:
                stop_multiplier = 1.5 # Tighter stop in low volatility
            else:
                stop_multiplier = 2.0 # Standard stop

            stop_loss_distance = current_data.ATR_14 * stop_multiplier
        else:
            # Fallback to percentage-based stop adjusted for regime
            if volatility_risk in [RiskLevel.VERY_HIGH, RiskLevel.HIGH]:
                stop_loss_distance = current_price * 0.03 # 3% stop
            elif volatility_risk == RiskLevel.LOW:
                stop_loss_distance = current_price * 0.01
            else:
                stop_loss_distance = current_price * 0.02

        if signal == Signal.BUY:
            stop_loss = current_price - stop_loss_distance
        elif signal == Signal.SELL:
            stop_loss = current_price + stop_loss_distance
        else:
            stop_loss = 0

        # Target based on regime outlook and recommended strategy
        if recommended_strategy == "MEAN_REVERSION":
            # Target mean reversion level
            recent_prices = [data.price.close_price for data in company_data_list[-20:] if data.price.open_price > 0]
            if len(recent_prices) >= 10:
                mean_price = sum(recent_prices) / len(recent_prices)
                if signal == Signal.BUY:
                    target = mean_price
                elif signal == Signal.SELL:
                    target = mean_price
                else:
                    target = 0
            else:
                target = current_price + (stop_loss_distance * 2) # 2:1 rr
        elif recommended_strategy == "TREND_FOLLOWING":
            # Target extended trend move
            if signal == Signal.BUY:
                target = current_price + (stop_loss_distance * 3) # 3:1 rr
            elif signal == Signal.SELL:
                target = current_price - (stop_loss_distance * 3)
            else:
                target = 0
        else:
            # Standard rr target
            if signal == Signal.BUY:
                target = current_price + (stop_loss_distance * 2.5)
            elif signal == Signal.SELL:
                target = current_price - (stop_loss_distance * 2.5)
            else:
                target = 0

        # 9 RR calculation
        if signal != Signal.HOLD and stop_loss_distance > 0:
            rr_ratio = abs(target - current_price) / stop_loss_distance
        else:
            rr_ratio = 0

        # Minimum rr requirement based on regime
        min_rr = 1.5 if volatility_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH] else 2.0
        if rr_ratio < min_rr and signal != Signal.HOLD:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 10. Setup scoring
        # Weight factors: regime transition (30%, signal strength (25%), market state (20%),
        # rr (15%), strategy confidence (10%)
        score = (
            composite_score * 0.3 +
            (signal_strength * 20) * 0.25 + # Scale to 0-100
            (trend_confidence * 0.3 + 70 * 0.7) * 0.2 + # Blend with base 70
            min(100,  rr_ratio * 20) * 0.15 + # Scale RR to 0-100
            strategy_confidence * 0.1
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'REGIME_SHIFT',
            'direction': direction,
            'signal': signal,
            'current_price': current_price,
            'position_size_factor': position_sizing_factor,
            'stop_loss': stop_loss,
            'target': target,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
            'regime_analysis': {
                'volatility)change': vol_change,
                'volatility_outlook': vol_outlook,
                'volatility_transition_prob': vol_transition_prob,
                'trend_change': trend_change,
                'trend_type': trend_type,
                'trend_confidence': trend_confidence,
                'liquidity_change': liquidity_change,
                'liquidity_condition': liquidity_condition,
                'market_impact': market_impact,
                'regime_outlook': regime_outlook,
                'composite_score': composite_score,
            },
            'market_state': {
                'current_trend': current_trend.name if hasattr(current_trend, 'name') else str(current_trend),
                'volatility_regime': volatility_regime,
                'volatility_risk': volatility_risk.name if hasattr(volatility_risk, 'name') else str(volatility_risk),
                'momentum_regime': momentum_regime.name if hasattr(momentum_regime, 'name') else str(momentum_regime),
            },
            'strategy_recommendation': {
                'recommended_strategy': recommended_strategy,
                'strategy_confidence': strategy_confidence,
                'adjustment_reason': adjustment_reason,
            },
            'signal_components': {
                'buy_signal': buy_signals,
                'sell_signal': sell_signals,
                'transition_signal': transition_signal
            }
        }

    def _calculate_regime_risk_factor(self, volatility_risk, liquidity_condition, trend_confidence):
        """
        Calculate risk adjustment factor based on regime conditions
        :param volatility_risk:
        :param liquidity_condition:
        :param trend_confidence:
        :return:
        """
        # Volatility risk factor (0.5-1.5)
        if volatility_risk in [RiskLevel.VERY_HIGH, RiskLevel.HIGH]:
            vol_factor = 0.6
        elif volatility_risk == RiskLevel.MEDIUM:
            vol_factor = 0.8
        elif volatility_risk == RiskLevel.LOW:
            vol_factor = 1.0
        else:
            vol_factor = 1.2 # Very low risk

        # Liquidity factor (0.7-1.3)
        if liquidity_condition == "HIGH_INSTITUTIONAL":
            liquidity_factor = 1.2
        elif liquidity_condition == "LOW_RETAIL":
            liquidity_factor = 0.8
        elif liquidity_condition == "SPIKE":
            liquidity_factor = 0.9
        else:
            liquidity_factor = 1.0 # Moderate

        # trend confidence factor (0.8-1.2)
        trend_factor = 0.8 + (trend_confidence / 100) * 0.4 # Scale 0.8-1.2

        # Combine factors
        regime_risk_factor = vol_factor * liquidity_factor * trend_factor

        return max(0.3, min(1.5, regime_risk_factor)) # Clamp between 0.3 and 1.5

    def _create_volatility_data(self, company_data_list):
        """
        Create mock volatility data from price data
        :param company_data_list:
        :return:
        """
        # Simplified implementation - in practice, use actual volatility calculation
        class MockVolatilityData:
            def __init__(self, volatility_value):
                self.volatility_value = volatility_value

        volatility_data = []
        for data in company_data_list:
            if hasattr(data, 'ATR_14') and data.ATR_14 is not None:
                volatility_data.append(MockVolatilityData(data.ATR_14))
            else:
                # Fallback to price-based volatility proxy
                volatility_data.append(MockVolatilityData(1.0)) # Default value

        return volatility_data

    def _create_trade_data(self, company_data_list):
        """
        Create mock trade data from volume data
        :param company_data_list:
        :return:
        """
        # Simplified implementation - in practice, use actual trade data
        class MockTradeData:
            def __init__(self, price, size):
                self.price = price
                self.size = size
                self.timestamp = None # Not used in this strategy

        trade_data = []
        for data in company_data_list:
            if (hasattr(data.price, 'close_price') and data.price.close_price > 0 and
            hasattr(data, 'volume') and data.volume is not None):
                # Create multiple mock trade per bar
                avg_trade_size = max(1, data.volume // 10) # Assume 10 trades per bar
                for _ in range(10):
                    trade_data.append(MockTradeData(price=data.price.close_price, size=avg_trade_size))

        return trade_data

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        regime_analysis = setup_result['regime_analysis']
        market_state = setup_result['market_state']
        strategy_rec = setup_result['strategy_recommendation']
        components = setup_result['signal_components']

        details = f"""
REGIME SHIFT SETUP - {setup_result['symbol']}
======================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Current Price: {setup_result['current_price']}
Position size factor: {setup_result['position_size_factor']}
Stop loss: {setup_result['stop_loss']}
Target: {setup_result['target']}
Risk/Reward: {setup_result['risk_level']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})

Regime Analysis:
- Volatility Change: {regime_analysis['volatility_change']}
- Volatility Outlook: {regime_analysis['volatility_outlook']}
- Volatility Transition Prob: {regime_analysis['volatility_transition_prob']}
- Trend Change: {regime_analysis['trend_change']}
- Trend Type: {regime_analysis['trend_type']}
- Trend Confidence: {regime_analysis['trend_confidence']}
- Liquidity Change: {regime_analysis['liquidity_change']}
- Liquidity Condition: {regime_analysis['liquidity_condition']}
- Market Impact: {regime_analysis['market_impact']}
- Regime Outlook: {regime_analysis['regime_outlook']}
- Composite Score: {regime_analysis['composite_score']}

Market State:
- Current Trend: {market_state['current_trend']}
- Volatility Regime: {market_state['volatility_regime']}
- Volatility Risk: {market_state['volatility_risk']}
- Momentum Regime: {market_state['momentum_regime']}

Strategy Recommendation:
- Recommended Strategy: {strategy_rec['recommended_strategy']}
- Strategy Confidence: {strategy_rec['strategy_confidence']}
- Adjustment reason: {strategy_rec['adjustment_reason']}

Signal Components:
- Buy Signal: {components['buy_signal']}
- Sell Signal: {components['sell_signal']}
- Transition Signal: {components['transition_signal']}

Key Filters Passed:
- Volatility Regime Analysis
- Trend Regime Identification
- Liquidity Regime Assessment
- Multi-Factor Transition Signals
- Adaptive Strategy Selection
- Regime-Based Risk Management
"""
        return details.strip()

# Helper function to use the setup
def regime_shift_setup(company_data, volatility_data_list=None, trade_data_list=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param volatility_data_list:
    :param trade_data_list:
    :return:
    """
    setup = RegimeShiftSetup()
    return setup.check_setup(company_data, volatility_data_list, trade_data_list)
