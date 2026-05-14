from src.filters.risk.risk_filter import RiskFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.filters.momentum.momentum_filter import MomentumFilter
from src.filters.trend.trend_filter import TrendFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData
import numpy as np
import random

class ReinforcementLearningSetup:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        self.risk_filter = RiskFilter()
        self.volatility_filter = AdvancedVolatilityFilter()
        self.momentum_filter = MomentumFilter()
        self.trend_filter = TrendFilter()
        # RL parameters
        self.learning_rate = learning_rate # Alpha
        self.discount_factor = discount_factor # Gamma
        self.epsilon = epsilon # Exploration rate

        # Q-table for state-action values (simplified)
        self.q_table = {}

        # State and action definitions
        self.states = [
            'VERY_LOW_VOLATILITY', 'LOW_VOLATILITY', 'MODERATE_VOLATILITY', 'HIGH_VOLATILITY', 'VERY_HIGH_VOLATILITY',
            'STRONG_UPTREND', 'UPTREND', 'NEUTRAL_TREND', 'DOWNTREND', 'STRONG_DOWNTREND',
            'VERY_BULLISH_MOMENTUM', 'BULLISH_MOMENTUM', 'NEUTRAL_MOMENTUM', 'BEARISH_MOMENTUM', 'VERY_BEARISH_MOMENTUM',
            'LOW_RISK', 'MODERATE_RISK', 'HIGH_RISK'
        ]

        self.actions = ['BUY', 'SELL', 'HOLD']

        # Initialize Q-table
        self._initialize_q_table()

    def _initialize_q_table(self):
        """
        Initialize Q-table with default values
        :return:
        """
        for state in self.states:
            self.q_table[state] = {}
            for action in self.actions:
                # Initialize with small random values
                self.q_table[state][action] = random.uniform(-0.1, 0.1)

    def check_setup(self, company: CompanyData, market_data_list=None, peer_data_dict=None):
        """
        Professional Reinforcement Learning Setup
        This setup uses reinforcement learning to optimize trading decisions

        Key components:
        1. State representation using market features
        2. Action selection using epsilon-greedy policy
        3. Reward calculation based on performance
        4. Q-learning update mechanism
        5. Adaptive position sizing
        :param company:
        :param market_data_list:
        :param peer_data_dict:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 20:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # 1. State representation
        current_state = self._get_current_state(company_data_list, market_data_list)

        # 2. Action selection (epsilon-greedy)
        action = self._select_action(current_state)

        # 3. convert action to signal
        signal = self._action_to_signal(action)
        direction = self._action_to_direction(action)

        # 4. Calculate reward (this would typically come from actual trading results)
        # For now, simulate reward based on recent performance
        reward = self._calculate_reward(company_data_list, signal)

        # 5. Q-learning update (in practice, this happens after observing next state)
        # For demonstration, show how the update would work
        next_state = self._predict_next_state(current_state, action, company_data_list)
        self._update_q_table(current_state, action, reward, next_state)

        # 6. Risk management
        # Position sizing based on state and Q-values
        position_sizing_factor = self._calculate_position_size(current_state, action)

        # Adjust for volati8lity regime
        volatility_regime, volatility_trend, volatility_risk = self.volatility_filter.volatility_regime_analysis(company_data_list, periods=20)

        if volatility_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            position_sizing_factor *= 0.6 # Reduce size in high volatility
        elif volatility_risk == RiskLevel.LOW:
            position_sizing_factor *= 1.3 # Increase size in low volatility

        # stop loss based on recent volatility and state
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            # Adjust stop distance based on volatility state
            if 'HIGH' in current_state or 'VERY_HIGH' in current_state:
                stop_multiplier = 3.0 # Wider stop in high volatility states
            else:
                stop_multiplier = 2.0 # Standard stop

            stop_loss_distance = current_price.ATR_14 * stop_multiplier
        else:
            # Fallback to percentage-based stop adjusted for state
            if 'HIGH' in current_state or 'VERY_HIGH' in current_state:
                stop_loss_distance = current_price * 0.03 # 3% stop
            else:
                stop_loss_distance = current_price * 0.02

        if signal == Signal.BUY:
            stop_loss = current_price - stop_loss_distance
        elif signal == Signal.SELL:
            stop_loss = current_price + stop_loss_distance
        else:
            stop_loss = 0

        # Target based on state and recent momentum
        target_price = self._calculate_target_price(current_price, signal, company_data_list, current_state)

        # 7. Risk/Reward calculation
        if signal != Signal.HOLD and stop_loss_distance > 0:
            rr_ratio = abs(target_price - current_price) / stop_loss_distance
        else:
            rr_ratio = 0

        # Need minimum 1.5:1 risk/reward
        if rr_ratio < 1.5 and signal != Signal.HOLD:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 8. Setup scoring
        # Score based on Q-value, reward, and risk-adjusted performance
        q_value = self.q_table.get(current_state, {}).get(action, 0)
        state_score = self._calculate_state_score(current_state)

        # Weight factors: Q-value(40%), reward(30%), state score (20%), risk/reward (10%)
        score = (
            max(0, min(100, (q_value + 1) * 50)) * 0.4 + # Scale Q-value to 0-100
            max(0, min(100, (reward + 1) * 50)) * 0.3 + # Sacle reward to 0-100
            state_score * 0.2 +
            min(100, rr_ratio * 20) * 0.1 # Scale RR to 0-100
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'REINFORCEMENT_LEARNING',
            'direction': direction,
            'signal': signal,
            'current_state': current_state,
            'position_size_factor': position_sizing_factor,
            'stop_loss': stop_loss,
            'target': target_price,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 80 else 'MEDIUM' if score > 65 else 'LOW',
            'rl_analysis': {
                'current_state': current_state,
                'selected_action': action,
                'q_value': q_value,
                'immediate_reward': reward,
                'exploration_rate': self.epsilon,
                'volatility_risk': volatility_risk.name if hasattr(volatility_risk, 'name') else str(volatility_risk),
            },
            'market_condition': {
                'volatility_regime': volatility_regime,
                'current_trend': self.trend_filter.price_momentum(company_data_list, periods=15).name,
                'momentum_regime': self.momentum_filter.momentum_regime(company_data_list, periods=15).name,
            }
        }
    def _get_current_state(self, company_data_list, market_data_list=None):
        """
        Convert market conditions to discrete state representation
        :param company_data_list:
        :param market_data_list:
        :return:
        """
        # Volatility state
        volatility_regime, volatility_trend, volattility_risk = self.volatility_filter.volatility_regime_analysis(
            company_data_list, periods=20)
        volatility_state = f"{volattility_risk.name if hasattr(volattility_risk, 'name') else str(volattility_risk)}_VOLATILITY"

        # Trend state
        current_trend = self.trend_filter.price_momentum(company_data_list, periods=15).name
        trend_state = f"{current_trend.name if hasattr(current_trend, 'name') else str(current_trend)}_TREND"

        # Momentum state
        momentum_regime = self.momentum_filter.momentum_regime(company_data_list, periods=15)
        momentum_state = f"{momentum_regime.name if hasattr(momentum_regime, 'name') else str(momentum_regime)}_MOMENTUM"

        # Risk state
        risk_level = self.risk_filter.assess_risk_level(company_data_list)
        risk_state = f"{risk_level.name if hasattr(risk_level, 'name') else str(risk_level)}_RISK"

        # Return the most relevant state for decision making
        # In practice, this could be a combination or the most critical factor
        if 'HIGH' in volatility_state or 'VERY_HIGH' in volatility_state:
            return volatility_state
        elif 'STRONG' in trend_state:
            return trend_state
        elif 'VERY' in momentum_state:
            return momentum_state
        else:
            return risk_state

    def _select_action(self, state):
        """
        Select action using epsilon-greedy policy
        :param state:
        :return:
        """
        # Exploration: random action
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Exploitation: best action based on Q-values
        q_values = self.q_table.get(state, {})
        if not q_values:
            return random.choice(self.actions)

        # Return action with highest Q-value
        return max(q_values, key=q_values.get)

    def _action_to_signal(self, action):
        """
        Convert RL action to trading signal
        :param action:
        :return:
        """
        if action == 'BUY':
            return 'LONG'
        elif action == 'SELL':
            return 'SHORT'
        else:
            return 'NEUTRAL'

    def _calculate_reward(self, company_data_list, signal):
        """
        Calculate reward based on recent performance (simplified)
        :param company_data_list:
        :param signal:
        :return:
        """
        if len(company_data_list) < 5 or signal == Signal.HOLD:
            return 0

        # Calcualte recent returns
        recent_prices = [data.price.close_price for data in company_data_list[-5:] if data.price.close_price > 0]
        if len(recent_prices) < 2:
            return 0

        recent_return = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]

        # Adjust reward based on signal
        if signal == Signal.BUY:
            reward = recent_return
        elif signal == Signal.SELL:
            reward = -recent_return
        else:
            reward = 0

        # Clamp reward to reasonable range
        return max(-1, min(1, reward))

    def _predict_next_state(self, current_state, action, company_data_list):
        """
        Predict next state based on current state and action (simplified)
        :param current_state:
        :param action:
        :param company_data_list:
        :return:
        """
        # In practice, this would use the actual next market state
        # For demonstration, this is a simple prediction

        # If taking action in a high-risk state, next state might be lower risk
        if 'HIGH' in current_state and action != 'HOLD':
            if 'VOLATILITY' in current_state:
                return 'MODERATE_VOLATILITY'
            elif 'RISK' in current_state:
                return 'MODERATE_RISK'

        # If we're holding in a low-risk state, it might stay low
        if 'LOW' in current_state and action == 'HOLD':
            return current_state

        # Default: next state is similar to current
        return current_state

    def _update_q_table(self, state, action, reward, next_state):
        """
        Update Q-table using Q-learning formula
        :param state:
        :param action:
        :param reward:
        :param next_state:
        :return:
        """
        # Get current Q-value
        current_q = self.q_table.get(state, {}).get(action, 0)

        # Get maximum Q-value for next state
        next_q_values = self.q_table.get(next_state, {})
        if next_q_values:
            max_next_q = max(next_q_values.values())
        else:
            max_next_q = 0

        # Q-learning update formula: Q(s,a) = Q(s,a) + q[r + ymaxQ(s',a') - Q(s,a)]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)

        # Update Q-table
        if state not in self.q_table:
            self.q_table[state] = {}
        self.q_table[state][action] = new_q

    def _calculate_position_size(self, state, action):
        """
        Calculate position size based on state and Q-values
        :param state:
        :param action:
        :return:
        """
        # Get Q-value for the selected action
        q_value = self.q_table.get(state, {}).get(action, 0)

        # Based position size based on Q-value confidence
        # Q-values are typically between -1 and 1, so we scale to 0-1
        base_size = max(0, min(1, (q_value + 1) / 2))

        # Adkist based pm state
        if 'VERY_HIGH' in state:
            # Reduce position size in very high risk states
            position_size = base_size * 0.5
        elif 'HIGH' in state:
            # Moderate position size in high risk states
            position_size = base_size * 0.7
        elif 'LOW' in state:
            # increase position size in low risk states
            position_size = base_size * 1.2
        else:
            position_size = base_size

        return min(1.0, position_size)

    def _calculate_target_price(self, current_price, signal, company_data_list, state):
        """
        Calculate target price based on state and recent momentum
        :param current_price:
        :param signal:
        :param company_data_list:
        :param state:
        :return:
        """
        if signal == Signal.HOLD:
            return current_price

        # Calculate recent momentum
        if len(company_data_list) >= 10:
            recent_prices = [data.price.close_price for data in company_data_list[-10:] if data.price.close_price > 0]
            if len(recent_prices) >= 2:
                momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            else:
                momentum = 0
        else:
            momentum = 0

        # Adjust momentum based on state
        if 'HIGH' in state or 'VERY_HIGH' in state:
            # Reduce target in high volatility states
            momentum *= 0.7
        elif 'LOW' in state:
            # Increase target in low volatility states
            momentum *- 1.3

        # Calculate target based on momentum and signal
        if signal == Signal.BUY:
            target = current_price * (1 + abs(momentum) * 2) # 2x momentum for target
        elif signal == Signal.SELL:
            target = current_price * (1 - abs(momentum) * 2)
        else:
            target = current_price

        return target

    def _calculate_state_score(self, state):
        """
        Calculate score for current state (0-100)
        :param state:
        :return:
        """
        # Score based on state favorability
        if 'VERY_LOW' in state or 'LOW' in state:
            return 90
        elif 'MODERATE' in state:
            return 70
        elif 'VERY_HIGH' in state:
            return 30
        else:
            return 60

    def get_setup_details(self, setup_results):
        """
        Get details information about the setup for reporting
        :param setup_results:
        :return:
        """
        if not setup_results:
            return "No valid setup found"

        rl_analysis = setup_results['rl_analysis']
        market_condition = setup_results['market_condition']

        details = f"""
REINFORCEMENT LEARNING SETUP - {setup_results['symbol']}
============================================
Setup Type: {setup_results['setup_type']}
Direction: {setup_results['direction']}
Signal: {setup_results['signal']}
Current Price: {setup_results['current_price']}
Position Size factor: {setup_results['position_size_factor']}
Stop Loss: {setup_results['stop_loss']}
Target Price: {setup_results['target']}
Risk/Reward: {setup_results['risk_reward']}
Confidence: {setup_results['confidence']} (Score: {setup_results['score']})

RL Analysis:
- Current State: {rl_analysis['current_state']}
- Selected Action: {rl_analysis['selected_action']}
- Q-Value: {rl_analysis['q_value']}
- Immediate Reward: {rl_analysis['immediate_reward']}
- Exploration Rate: {rl_analysis['exploration_rate']}
- Volatility Risk: {rl_analysis['volatility_risk']}

Market Condition:
- Volatility Regime: {market_condition['volatility_regime']}
- Current Trend: {market_condition['current_trend']}
- Momentum Regime: {market_condition['momentum_regime']}

Key Filters Passed:
- State Representation
- Action Selection (Epsilon-Greedy)
- Reward Calculation
- Q-Learning Update
- Adaptive Position Sizing
- Risk Management
"""
        return details.strip()

    def get_q_table_summary(self):
        """
        Get summary of current Q-table for analysis
        :return:
        """
        summary = "Q-TABLE SUMMARY\n==============\n"
        for state, actions in self.q_table.items():
            summary += f"\n{state}:\n"
            for action, q_value in actions.items():
                summary += f"\t{action}: {q_value}\n"

        return summary

# Helper function to use the setup
def reinforcement_learning_setup(company_data, market_data_list=None, peer_data_dict=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param market_data_list:
    :param peer_data_dict:
    :return:
    """
    setup = ReinforcementLearningSetup()
    return setup.check_setup(company_data, market_data_list, peer_data_dict)