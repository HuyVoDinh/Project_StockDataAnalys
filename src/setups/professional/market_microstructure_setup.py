from src.filters.microstructure.market_microstructure_filter import MarketMicrostructureFilter
from src.filters.orderflow.order_flow_filter import OrderFlowFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class MarketMicrostructureSetup:
    def __init__(self):
        self.microstructure_filter = MarketMicrostructureFilter()
        self.orderflow_filter = OrderFlowFilter()
        self.risk_filter = RiskFilter()
        self.volatility_filter = AdvancedVolatilityFilter()

    def check_setup(self, company: CompanyData, trade_data_list=None, order_book_data_list=None, quote_data_list=None):
        """
        Professional Market Microstructure setup
        This Setup exploits short-term market structure inefficiencies

        Key components:
        1. Order book dynamics and liquidity analysis
        2. Order flow imbalance detection
        3. Market microstructure pattern recognition
        4. High-frequency informed trading signals
        :param company_data:
        :param trade_data_list:
        :param order_book_data_list:
        :param quote_data_list:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 10:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # Need high-frequency data for microstructure analysis
        if not trade_data_list or not order_book_data_list:
            return None

        # 1. Order book imbalance analysis
        if order_book_data_list and len(order_book_data_list) > 0:
            current_order_book = order_book_data_list[-1]
            if (hasattr(current_order_book, 'bids') and hasattr(current_order_book, 'asks') and
            current_order_book.bids and current_order_book.asks):
                # Calculate toltal bid and ask volume
                total_bid_volume = sum(volume for _, volume in current_order_book.bids[:10]) # Top 10 levels
                total_ask_volume = sum(volume for _, volume in current_order_book.asks[:10]) # Top 10 levels

                order_book_imbalance = self.microstructure_filter.calculate_order_book_imbalance((total_bid_volume, total_ask_volume))
            else:
                order_book_imbalance = 0
        else:
            order_book_imbalance = 0

        # 2. Order flow analysis
        cucumlative_delta, delta_ratio, market_bisa = self.orderflow_filter.detect_cumulative_delta(trade_data_list, periods=50)

        # 3. Liquidity sweep detection
        liquidity_sweeps, sweep_intensity, sweep_direction = self.microstructure_filter.detect_liquidity_sweeps(trade_data_list, order_book_data_list, periods=30)

        # 4. Momentum ignition detection
        volume_data_list = [data for data in company_data_list if hasattr(data, 'volume') and data.volume is not None]
        momentum_ignition, ignition_strength, ignition_direction = self.microstructure_filter.detect_momentum_ignition(company_data_list, volume_data_list, periods=20)

        # 5. Spread dynamics analysis
        bid_ask_data_list = []
        if order_book_data_list:
            for ob in order_book_data_list[-20:]: # Last 20 order books
                if hasattr(ob, 'bids') and hasattr(ob, 'asks') and ob.bids and ob.asks:
                    bid_price = ob.bids[0][0] # Best bid
                    ask_price = ob.asks[0][0] # Best ask
                    # Create mock bid_ask data object
                    class MockBidAsk:
                        def __init__(self, bid, ask):
                            self.bid = bid
                            self.ask = ask
                    bid_ask_data_list.append(MockBidAsk(bid_price, ask_price))

        spread_quality, liquidity_condition, spread_signal = self.microstructure_filter.analyze_spread_dynamics(bid_ask_data_list, periods=20)

        # 6. Institutional activity detection
        institutional_activity, activity_score, directional_bias = self.orderflow_filter.detect_institutional_activity(trade_data_list, volume_threshold_multiplier=3)

        # 7. Entry signal generation
        signal = Signal.HOLD
        direction = "NEUTRAL"

        # Combine multiple microstructure signals
        buy_signals = 0
        sell_signals = 0

        # Order book imbalance signal
        if order_book_imbalance > 0.3: # Strong buying pressure
            buy_signals += 1
        elif order_book_imbalance < -0.3: # Strong selling pressure
            sell_signals += 1

        # Order flow delta signal
        if delta_ratio > 0.2: # Strong buying pressure
            buy_signals += 1
        elif delta_ratio < -0.2: # Strong selling pressure
            sell_signals += 1

        # Liquidity sweep signal
        if liquidity_sweeps and sweep_intensity > 50:
            if sweep_direction == "BULLISH":
                buy_signals += 1
            elif sweep_direction == "BEARISH":
                sell_signals += 1

        # Momentum ignition signal
        if momentum_ignition and ignition_strength > 60:
            if ignition_direction == "UP":
                buy_signals += 1
            elif ignition_direction == "DOWN":
                sell_signals += 1

        # Spread signal
        if spread_signal == Signal.BUY:
            buy_signals += 1
        elif spread_signal == Signal.SELL:
            sell_signals += 1

        # Institutional activity signal
        if institutional_activity and activity_score > 70:
            if directional_bias == "BULLISH":
                buy_signals += 1
            elif directional_bias == "BEARISH":
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
        # Position sizing based on signal strength and market quality
        signal_strength = max(buy_signals, sell_signals)
        market_quality_score = self._calculate_market_quality(spread_quality, liquidity_condition, activity_score)

        position_sizing_factor = min(1.0, (signal_strength / 5) * (market_quality_score / 100))

        # Stop loss based on recent volatility
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            stop_loss_distance = 2 * current_data.ATR_14 # 2x ATR stop
        else:
            # Fallback to percentage-based stop
            stop_loss_distance = current_price *0.01 # 1% stop for short-term trading

        if signal == Signal.BUY:
            stop_loss = current_price - stop_loss_distance
        elif signal == Signal.SELL:
            stop_loss = current_price + stop_loss_distance
        else:
            stop_loss = 0

        # Target based on microstructur patterns
        if signal == Signal.BUY:
            target = current_price + (stop_loss_distance * 2) # 2:1 Risk/reward
        elif signal == Signal.SELL:
            target = current_price - (stop_loss_distance * 2) # 2:1 Risk/reward
        else:
            target = 0

        # 9 Risk/Reward calculation
        if signal != Signal.HOLD and stop_loss_distance > 0:
            rr_ratio = 2.0 # Fixed 2:1 for microstructure strategies
        else:
            rr_ratio = 0

        # 10. Setup scoring
        # Weight factors: signal strength (30%), market quality (25%), microstructure factors (25%),
        # Risk/reward (10%), institutional activity (10%)
        score = (
        (signal_strength * 20) * 0.30 + # Scale to 0-100
            market_quality_score * 0.25 +
        ((abs(order_book_imbalance) + abs(delta_ratio)) * 50) * 0.25 + # Scale to 0-100
        (rr_ratio * 25) * 0.10 + # Scale to 0-100 (2:1 = 50)
            activity_score * 0.10
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'MARKET_MICROSTRUCTURE',
            'direction': direction,
            'signal': signal,
            'current_price': current_price,
            'position_size_factor': position_sizing_factor,
            'stop_loss': stop_loss,
            'target': target,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 80 else 'MEDIUM' if score > 65 else 'LOW',
            'signal_components' : {
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'order_book_imbalance': order_book_imbalance,
                'delta_ratio': delta_ratio,
                'liquidity_sweeps': liquidity_sweeps,
                'sweep_intensity': sweep_intensity,
                'momentum_ignition': momentum_ignition,
                'ignition_strength': ignition_strength,
                'spread_quality': spread_quality,
                'institutional_activity': institutional_activity,
                'activity_score': activity_score,
            },
            'market_condition': {
                'spread_quality': spread_quality,
                'liquidity_condition': liquidity_condition.name if hasattr(liquidity_condition, 'name') else str(liquidity_condition),
                'market_bias': market_bisa,
                'directional_bias': directional_bias
            }
        }

    def _calculate_market_quality(self, spread_quality, liquidity_condition, activity_score):
        """
        Calculate overall market quality score for trading
        :param spread_quality:
        :param liquidity_condition:
        :param activity_score:
        :return:
        """
        # Score spread quality (0-100)
        if spread_quality == "EXCELLENT":
            spread_score = 100
        elif spread_quality == "GOOD":
            spread_score = 70
        else:
            spread_score = 30

        # Score liquidity condition (0-100)
        if liquidity_condition == "Good":
            liquidity_score = 100
        elif liquidity_condition == "Weak":
            liquidity_score = 50
        else:
            liquidity_score = 20

        # Combine scores with weights
        market_quality = (spread_score * 0.4) + (liquidity_score * 0.4) + (activity_score * 0.2)

        return min(100, market_quality)

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
MARKET MICROSTRUCTURE SETUP - {setup_result['symbol']}
======================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Current Price: {setup_result['current_price']}
Position Size factor: {setup_result['position_size_factor']}
Stop Loss: {setup_result['stop_loss']}
Target: {setup_result['target']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})

Signal Components:
- Buy Signal: {components['buy_signals']}
- Sell Signal: {components['sell_signals']}
- Order Book Imbalance: {components['order_book_imbalance']}
- Delta Ratio: {components['delta_ratio']}
- Liquidity Sweeps: {components['liquidity_sweeps']}
- Sweep Intensity: {components['sweep_intensity']}
- Momentum Ignition: {components['momentum_ignition']}
- Ignition Strength: {components['ignition_strength']}
- Institutional Activity: {components['institutional_activity']}
- Activity Score: {components['activity_score']}

Market Condition:
- Spread Quality: {market_condition['spread_quality']}
- Liquidity Condition: {market_condition['liquidity_condition']}
- Market Bias: {market_condition['market_bias']}
- Directional Bias: {market_condition['directional_bias']}

Key Filters Passed:
- Order Book Analysis
- Order Flow Imbalance
- Liquidity Sweep Detection
- Momentum Ignition
- Spread Dynamics
- Institutional Activity
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def market_microstructure_strategy(company_data, trade_data_list=None, order_book_data_list=None, quote_data_list=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param trade_data_list:
    :param order_book_data_list:
    :param quote_data_list:
    :return:
    """
    setup = MarketMicrostructureSetup()
    return setup.check_setup(company_data, trade_data_list, order_book_data_list, quote_data_list)