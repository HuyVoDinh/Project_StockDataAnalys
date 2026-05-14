from src.filters.orderflow.order_flow_filter import OrderFlowFilter
from src.filters.microstructure.market_microstructure_filter import MarketMicrostructureFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import Company, CompanyData


class OrderFlowSetup:
    def __init__(self):
        self.orderflow_filter = OrderFlowFilter()
        self.microstructure_filter = MarketMicrostructureFilter()
        self.risk_filter = RiskFilter()
        self.volatility_filter = AdvancedVolatilityFilter()

    def check_setup(self, company: CompanyData, trade_data_list=None, order_book_data_list=None):
        """
        Professional Order Flow Strategy
        This strategy identifies institutional activity and smart money flow

        Key components
        1. Volume-weighted price analysis
        2. Cumulative delta and order flow imbalance
        3. Footprint chart pattern recognition
        4. Liquidity void and key level identification
        5. Institutional activity detection
        :param company:
        :param trade_data_list:
        :param order_book_data_list:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 15:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # Need high-frequency data for order flow analysis
        if not trade_data_list:
            return None

        # 1. Volume-weighted average price analysis
        vwap, price_deviation, flow_direction = self.orderflow_filter.calculate_volume_weighted_price(trade_data_list, periods=200)

        # 2. Cumulative delta analysis
        cumulative_delta, delta_ratio, market_bias = self.orderflow_filter.detect_cumulative_delta(trade_data_list, periods=200)

        # 3. Order flow imbalance
        imbalance_ratio, buying_pressure, selling_pressure = self.orderflow_filter.order_flow_imbalance(trade_data_list, time_window=60)

        # 4. Institutional activity detection
        institutional_activity, activity_score, directional_bias = self.orderflow_filter.detect_institutional_activity(trade_data_list, volume_threshold_multiplier=15)

        # 5. Liquidity void detection (of order book data available)
        if order_book_data_list and len(order_book_data_list) > 0:
            void_levels, void_intensity, breakout_potential = self.orderflow_filter.detect_liquidity_voids(order_book_data_list, price_leves=15)
        else:
            void_levels, void_intensity, breakout_potential = [], 0, "LOW"

        # 6. Footprint chart analysis
        key_levels, volume_profile, market_structure = self.orderflow_filter.analyze_footprint_charts(trade_data_list, price_levels=8)

        # 7. Entry signal generation based on order flow
        signal = Signal.HOLD
        direction = "NEUTRAL"

        # Combine order flow signals
        buy_signals = 0
        sell_signals = 0

        # VWAP signal
        if flow_direction == "ABOVE_VWAP" and price_deviation > 0.015: # 1.5 above VWAP
            buy_signals += 1
        elif flow_direction == "BELOW_VWAP" and price_deviation < -0.015: # 1.5% below VWAP
            sell_signals += 1

        # delta signal
        if delta_ratio > 0.15: # 15% buying pressure
            buy_signals += 1
        elif delta_ratio < -0.15:
            sell_signals += 1

        # Order flow imbalance signal
        if imbalance_ratio > 0.2: # Strong buying imbalance
            buy_signals += 1
        elif imbalance_ratio < -0.2:
            sell_signals += 1

        # Institutional activity signal
        if institutional_activity and activity_score > 65:
            if directional_bias == "BULLISH":
                buy_signals += 1
            elif directional_bias == "BEARISH":
                sell_signals += 1

        # Liquidity void signal
        if breakout_potential == "HIGH" and void_intensity > 50:
            # Determine direction based on void location
            bid_voids = [level for level in void_levels if level[0] == "BID"]
            ask_voids = [level for level in void_levels if level[0] == "ASK"]

            if ask_voids and not bid_voids: # More resistance voids
                buy_signals += 1
            elif bid_voids and not ask_voids: # More support voids
                sell_signals += 1

        # Market structure signal
        if market_structure == "BULLISH_STACKING":
            buy_signals += 1
        elif market_structure == "BEARISH_STACKING":
            sell_signals += 1

        # Generate final signal
        if buy_signals >= 3 and buy_signals > sell_signals:
            signal = Signal.BUY
            direction = "LONG"
        elif sell_signals >= 3 and sell_signals > buy_signals:
            signal = Signal.SELL
            direction = "SHORT"
        else:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 8. Risk management
        # Position sizing based on order flow strength and institutional activity
        signal_strength = max(buy_signals, sell_signals)
        order_flow_quality = self._calculate_order_flow_quality(delta_ratio, imbalance_ratio, activity_score)

        position_sizing_factor = min(1.0, (signal_strength / 5)  * (order_flow_quality / 100))

        # Adjust for market structure
        if market_structure == "CONSOLIDATION":
            position_sizing_factor *= 0.8 # Reduce in consolidation
        elif market_structure in ["BULLISH_STACKING", "BEARISH_STACKING"]:
            position_sizing_factor *= 1.2 # Increse in trending structure

        # Stop loss based on order book levels and recent volatility
        if order_book_data_list and len(order_book_data_list) > 0:
            current_order_book = order_book_data_list[-1]
            if (hasattr(current_order_book, 'bids') and hasattr(current_order_book, 'asks') and current_order_book.bids and current_order_book.asks):
                # Use beat bid/ask for tight stop
                best_bid = current_order_book.bids[0][0]
                best_ask = current_order_book.asks[0][0]
                order_book_stop = min(current_price - best_bid, best_ask - current_price)
            else:
                order_book_stop = current_price * 0.005 # 0.5% default
        else:
            order_book_stop = current_price * 0.005

        # Combine with ATR if available
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            atr_stop = current_data.ATR_14
            stop_loss_distance = max(order_book_stop, atr_stop * 0.5) # Blend stops
        else:
            stop_loss_distance = order_book_stop

        if signal == Signal.BUY:
            stop_loss = current_price - stop_loss_distance
        elif signal == Signal.SELL:
            stop_loss = current_price + stop_loss_distance
        else:
            stop_loss = 0

        # Target based on order flow patterns and key levels
        if key_levels:
            # Find nearest key level in direction of trade
            if signal == Signal.BUY:
                target_levels = [level for level in key_levels if level > current_price]
                if target_levels:
                    target = min(target_levels) # Nearest resistance
                else:
                    target = current_price + (stop_loss_distance * 3) # 3:1 rr
            elif signal == Signal.SELL:
                target_levels = [level for level in key_levels if level < current_price]
                if target_levels:
                    target = max(target_levels)  # Nearest support
                else:
                    target = current_price - (stop_loss_distance * 3)
        else:
            # Use fixed rr ratio
            if signal == Signal.BUY:
                target = current_price + (stop_loss_distance * 3)
            elif signal == Signal.SELL:
                target = current_price - (stop_loss_distance * 3)
            else:
                target = 0

        # 9. RR calculation
        if signal != Signal.HOLD and stop_loss_distance > 0:
            rr_ratio = abs(target - current_price) / stop_loss_distance
        else:
            rr_ratio = 0

        # Need minimum 2:1 rr for order flow setup
        if rr_ratio < 2.0 and signal != Signal.HOLD:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 10. Setup scoring
        # Weight factors: signal strength (25%), order flow quality (25%), institutional activity (20%), rr(15%), market structure (15%)
        score = (
        (signal_strength * 20) * 0.15 + # Scale to 0-100
            order_flow_quality * 0.25 +
            activity_score * 0.2 +
            min (100, rr_ratio * 15) * 0.15 + # Scale RR to 0-100
        (70 if market_structure in ["BULLISH_STACKING", "BEARISH_STACKING"] else
         50 if market_structure == "CONSOLIDATION" else 30) * 0.15
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'ORDER_FLOW',
            'direction': direction,
            'signal': signal,
            'current_price': current_price,
            'position_size_factor': position_sizing_factor,
            'stop_loss': stop_loss,
            'target': target,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
            'signal_components': {
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'vwap': vwap,
                'price_deviation': price_deviation,
                'flow_direction': flow_direction,
                'cumulative_delta': cumulative_delta,
                'delta_ratio': delta_ratio,
                'imbalance_ratio': imbalance_ratio,
                'institutional_activity': institutional_activity,
                'activity_score': activity_score,
                'directional_bias': directional_bias,
                'void_intensity': void_intensity,
                'breakout_potential': breakout_potential,
            },
            'market_condition': {
                'market_bias': market_bias,
                'market_structure': market_structure,
                'key_levels_count': len(key_levels),
                'volume_profile_nodes': len(volume_profile) if volume_profile else 0
            }
        }

    def _calculate_order_flow_quality(self, delta_ratio, imbalance_ratio, activity_score):
        """
        Calculate overall order flow quality score
        :param delta_ratio:
        :param imbalance_ratio:
        :param activity_score:
        :return:
        """
        # Score delta ratio (0-100)
        delta_score = min(100, abs(delta_ratio) * 500) # Scale to 0-100

        # Score imbalance ratio (0-100)
        imbalance_score = min(100, abs(imbalance_ratio) * 250) # Scale to 0-100

        # Combine scores with weights
        order_flow_quality = (delta_score * 0.35) + (imbalance_score * 0.35) + (activity_score * 0.3)

        return min(100, order_flow_quality)

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        components = setup_result['signal_components']
        market_condition = setup_result['market_condition']

        details = f"""
ORDER FLOW SETUP - {setup_result['symbol']}
==================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Current Price: {setup_result['current_price']}
Position size factor: {setup_result['position_size_factor']}
Stop loss: {setup_result['stop_loss']}
Target: {setup_result['target']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})

Signal Components:
- Buy signals: {components['buy_signals']}
- Sell signals: {components['sell_signals']}
- VWAP: {components['vwap']}
- Price deviation: {components['price_deviation']}
- Flow Direction: {components['flow_direction']}
- Cumulative Delta: {components['cumulative_delta']}
- Delta Ratio: {components['delta_ratio']}
- Imbalance Ratio: {components['imbalance_ratio']}
- Institutional Activity: {components['institutional_activity']}
- Activity Score: {components['activity_score']}
- Directional Bias: {components['directional_bias']}
- Void Intensity: {components['void_intensity']}
- Breakout Potential: {components['breakout_potential']}

Market Condition:
- Market Bias: {market_condition['market_bias']}
- Market Structure: {market_condition['market_structure']}
- Key Levels Count: {components['key_levels_count']}
- Volume Profile Nodes: {components['volume_profile_nodes']}

Key Filters Passed:
- Volume-Weighted Price Analysis
- Cumulative Delta Analysis
- Order Flow Imbalance
- Institutional Activity Detection
- Liquidity Void Analysis
- Footprint Chart Analysis
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def order_flow_setup(company_data, trade_data_list=None, order_book_data_list=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param trade_data_list:
    :param order_book_data_list:
    :return:
    """
    setup = OrderFlowSetup()
    return setup.check_setup(company_data, trade_data_list, order_book_data_list)