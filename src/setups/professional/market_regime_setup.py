from pydantic.v1 import NoneStr

from src.filters.market_regime.market_regime_filter import MarketRegimeFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.filters.volume.volume_profile_filter import VolumeProfileFilter
from src.filters.momentum.momentum_filter import MomentumFilter
from src.filters.risk.risk_filter import RiskFilter
from src.enums.trend import Trend, MarketState
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class MarketRegimeSetup:
    def __init__(self):
        self.market_regime_filter = MarketRegimeFilter()
        self.volatility_filter = AdvancedVolatilityFilter()
        self.volume_filter = VolumeProfileFilter()
        self.momentum_filter = MomentumFilter()
        self.risk_filter = RiskFilter()

    def check_setup(self, company: CompanyData, market_data_list=None, sector_data_dict=None):
        """
        Professional Market Regime Adaptive Setup
        This setup adapts to different market conditions and applies appropriate filters

        Key components:
        1. Market regim classification
        2. Regime-specific filters
        3. Adaptive position size
        4. Risk management
        :param company:
        :param market_data_list:
        :param sector_data_dict:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 30:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # 1. Determine market regime if market data is provided
        if market_data_list and sector_data_dict:
            market_regime, volatility_regime, sector_rotation = self.market_regime_filter.market_regime_classification(
                market_data_list, sector_data_dict, periods=50)
        else:
            # Default to neutral regime if no market data
            market_regime = MarketState.EARLY_TREND
            volatility_regime = Trend.Sideway
            sector_rotation = {}

        # 2. Get regime adaptation setup
        risk_regime = volatility_regime # Simplified mapping
        strategy_type, position_sizing, risk_management = self.market_regime_filter.regime_adaptation_strategy(
            market_regime, volatility_regime, risk_regime)

        # 3. Apply regime-specific filters
        regime_filters_passes = self._apply_regime_filters(company_data_list, market_regime, volatility_regime)
        if not regime_filters_passes:
            return None

        # 4. Check momentum (always important)
        price_momentum = self.momentum_filter.price_momentum(company_data_list, periods=10)
        rsi_momentum = self.momentum_filter.rsi_momentum(current_data, overbought=75, oversold=25) # Stricter levels

        # 5. Check volume confirmation
        volume_trend, institutional_activity, volume_confidence = self.volume_filter.volume_profile_analysis(company_data_list, periods=20)

        # 6. Apply strategy-specific logic based on regime
        setup_result = None
        if strategy_type == "TREND_FOLLOWING":
            setup_result = self._trend_following_setup(company, company_data_list, price_momentum,
                                                       volume_trend, institutional_activity, volume_confidence)
        elif strategy_type == "BREAKOUT":
            setup_result = self._breakout_setup(company, company_data_list, price_momentum, rsi_momentum,
                                                volume_trend, institutional_activity, volume_confidence)
        elif strategy_type == "DEFENSIVE":
            setup_result = self._defensive_setup(company, company_data_list, price_momentum, rsi_momentum,
                                                 volume_trend,volume_confidence)
        else: # MIXED or default
            setup_result = self._mixed_regime_setup(company, company_data_list, price_momentum, rsi_momentum,
                                                    volume_trend, institutional_activity,volume_confidence)

        if setup_result:
            # Add regime information to setup
            setup_result["market_regime"] = market_regime.name if hasattr(market_regime, 'name') else str(market_regime)
            setup_result["strategy_type"] = strategy_type
            setup_result["position_sizing"] = position_sizing
            setup_result["risk_management"] = risk_management

            # Adjust position sizing based on regime
            setup_result = self._adjust_for_regime(setup_result, position_sizing, risk_management)

        return setup_result

    def _apply_regime_filters(self, company_data_list, market_regime, volatility_regime):
        """
        Apply filters specific to the current market regime
        :param company_data_list:
        :param market_regime:
        :param volatility_regime:
        :return:
        """
        # Get volatility analysis
        volatility_regime_result, volatility_trend, risk_level = self.volatility_filter.volatility_regime_analysis(company_data_list, periods=20)

        # In high volatility regimes, be more selective
        if volatility_regime in [Trend.Fomo, Trend.Good] and risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            # Need stronger confirmation signals
            volume_trend, institutional_activity, volume_confidence = self.volume_filter.volume_profile_analysis(company_data_list, periods=20)

            # Need high confidence volume and clear trend
            if volume_confidence < 70 or not institutional_activity:
                return False
        # In low volatility regimes, look for breakouts
        elif volatility_regime == Trend.Weak:
            # Need contraction patterns
            contraction_phase, expansion_phase, breakout_potential = self.volatility_filter.volatility_contraction_expansion(company_data_list, periods=30)

            if not contraction_phase:
                return False

        return True

    def _trend_following_setup(self, company, company_data_list, price_momentum, volume_trend, institutional_activity, volume_confidence):
        """
        Setup logic for trend following regime
        :param company:
        :param company_data_list:
        :param price_momentum:
        :param volume_trend:
        :param institutional_activity:
        :param volume_confidence:
        :return:
        """
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # Need strong momentum and volume confirmation
        if price_momentum not in [Trend.Up, Trend.Strong_Up] or volume_trend != Trend.Up:
            return None

        if not institutional_activity or volume_confidence < 70:
            return None

        # Entry should be on pullback to moving average
        ma20 = current_data.moving_average_20.ma_price if current_data.moving_average_20.ma_price else current_price
        ma50 = current_data.moving_average_50.ma_price if current_data.moving_average_50.ma_price else current_price

        # Price should be above MAs and within 3% of MA220 for entry
        if (current_price > ma20 and current_price > ma50 and abs(current_price - ma20) / ma20 < 0.03):
            # Risk management
            stop_loss = ma20 * 0.97 # 3% below 20-day MA
            target_price = current_price * 1.10 # 10% target

            rr_ratio = (target_price - current_price) / (current_price - stop_loss) if (current_price > stop_loss) > 0 else 0

            if rr_ratio < 2.0: # Minimum 2:1 risk/reward
                return None

            score = (volume_confidence * 0.4) + (70 * 0.3) + (rr_ratio * 10 * 0.3) # 70 for momentum

            return {
                'symbol': company.symbol,
                'setup_type': 'TREND_FOLLOWING',
                'direction': 'LONG',
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'target_price': target_price,
                'risk_reward': rr_ratio,
                'score': min(100, score),
                'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW'
            }

        return NoneStr

    def _breakout_setup(self, company, company_data_list, price_momentum, rsi_momentum,
                        volume_trend, institutional_activity, volume_confidence):
        """
        Setup logic for breakout regime.
        :param company:
        :param company_data_list:
        :param price_momentum:
        :param rsi_momentum:
        :param volume_trend:
        :param institutional_activity:
        :param volume_confidence:
        :return:
        """
        current_data = company_data_list[-1]

        # Check for breakout confirmation
        breakout_confirmed, direction, quality = self.volatility_filter.volatility_breakout_confirmation(company_data_list, current_data)

        if not breakout_confirmed or quality < 60 or direction != Trend.Up:
            return None

        # Need volume confirmation for breakouts
        if volume_trend != Trend.Up or not institutional_activity:
            return None

        current_price = current_data.price.close_price
        entry_price = current_price
        stop_loss = current_price * 0.96 # 4% stop loss
        target_price = current_price * 1.08 # 8% target

        rr_ratio = (target_price - entry_price) / (entry_price - stop_loss) if (entry_price - stop_loss) > 0 else 0

        if rr_ratio < 1.5:
            return None

        score = (quality * 0.4) + (volume_confidence * 0.3) + (rr_ratio * 10 * 0.3)

        return {
            'symbol': company.symbol,
            'setup_type': 'BREAKOUT',
            'direction': 'LONG',
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW'
        }

    def _defensive_setup(self, company, company_data_list, price_momentum, rsi_momentum,
                         volume_trend, volume_confidence):
        """
        Setup logic for defensive regime.
        :param company:
        :param company_data_list:
        :param price_momentum:
        :param rsi_momentum:
        :param volume_trend:
        :param volume_confidence:
        :return:
        """
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # In defensive regime, look for high quality setups with strong risk management
        if price_momentum in [Trend.Down, Trend.Strong_Down]:
            return None # Avoid downtrending stocks

        # Look for oversold conditions with positive momentum recovery
        if rsi_momentum == Signal.BUY: # RSI indication oversold recovery
            # Need support confirmation
            # TODO: Need verify support level

            # Simplified support check
            stop_loss = current_price * 0.95 # 5% stop loss (defensive)
            target_price = current_price * 1.04 # 4% target (conservative)

            rr_ratio = (target_price - current_price) / (current_price - stop_loss) if (current_price - stop_loss) > 0 else 0

            if rr_ratio < 2.0: # Need strong rr in defensive mode
                return None

            score = (volume_confidence * 0.3) + (60 * 0.4) + (rr_ratio * 10 * 0.3) # 60 for momentum

            return {
                'symbol': company.symbol,
                'setup_type': 'DEFENSIVE',
                'direction': 'LONG',
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'target_price': target_price,
                'risk_reward': rr_ratio,
                'score': min(100, score),
                'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW'
            }

        return None

    def _mixed_regime_setup(self, company, company_data_list, price_momentum, rsi_momentum,
                            volume_trend, institutional_activity, volume_confidence):
        """
        Setup logic for mixed regime.
        :param company:
        :param company_data_list:
        :param price_momentum:
        :param rsi_momentum:
        :param volume_trend:
        :param institutional_activity:
        :param volume_confidence:
        :return:
        """
        # Apply balanced criteria
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # Need at least neutral momentum
        if price_momentum == Trend.Strong_Down:
            return None

        # Volume confirmation helpful but not required
        volume_ok = volume_trend in [Trend.Up, Trend.Sideway] or institutional_activity

        if volume_ok:
            stop_loss = current_price * 0.96 # 4% stop loss
            target_price = current_price * 1.06 # 6% target

            rr_ratio = (target_price - current_price) / (current_price - stop_loss) if (current_price - stop_loss) > 0 else 0

            if rr_ratio < 1.5:
                return None

            # Score based on available factors
            momentume_score = 70 if price_momentum in [Trend.Up, Trend.Good] else 50 if price_momentum == Trend.Sideway else 30
            volume_score = volume_confidence if volume_confidence else 50

            score = (momentume_score * 0.4) + (volume_score * 0,3) + (rr_ratio * 0.3)

            return {
                'symbol': company.symbol,
                'setup_type': 'MIXED_REGIME',
                'direction': 'LONG',
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'target_price': target_price,
                'risk_reward': rr_ratio,
                'score': min(100, score),
                'confidence': 'HIGH' if score > 80 else 'MEDIUM' if score > 60 else 'LOW'
            }
        return None

    def _adjust_for_regime(self, setup_result, position_sizing, risk_management):
        """
        Adjust setup parameters based on regime recommendations
        :param setup_result:
        :param position_sizing:
        :param risk_management:
        :return:
        """
        if not setup_result:
            return setup_result

        # Adjust position sizing
        if position_sizing == "CONSERVATIVE":
            # Reduce target by 20%
            setup_result['target_price'] = setup_result['entry_price'] + (
            (setup_result['target_price'] - setup_result['entry_price']) * 0.8
            )
        elif position_sizing == "AGGRESSIVE":
            # Increase target by 20%
            setup_result['target_price'] = setup_result['entry_price'] + (
            (setup_result['target_price'] - setup_result['entry_price']) * 1.2
            )

        # Adjust risk management
        if risk_management == "STRICT":
            # Tighten stop loss by 20%
            setup_result['stop_loss'] = setup_result['entry_price'] - (
            (setup_result['entry_price'] - setup_result['stop_loss']) * 0.8
            )
        elif risk_management == "FLEXIBLE":
            setup_result['stop_loss'] = setup_result['entry_price'] - (
            (setup_result['entry_price'] - setup_result['stop_loss']) * 1.2
            )

        # REcalculate risk/reward
        entry_price = setup_result['entry_price']
        stop_loss = setup_result['stop_loss']
        target_price = setup_result['target_price']

        if (entry_price - stop_loss) > 0:
            rr_ratio = (target_price - entry_price) / (entry_price - stop_loss)
            setup_result['risk_reward'] = rr_ratio

        return setup_result

    def get_setup_details(self, setup_results):
        """
        Get detailed information about the setup for reporting
        :param setup_results:
        :return:
        """
        if not setup_results:
            return "No valid setup found"

        details = f"""
MARKET REGIME STRATEGY SETUP - {setup_results['symbol']}
=====================================
Setup Type: {setup_results['setup_type']}
Marget Regime: {setup_results.get('market_regime', 'UNKNOWN')}
Direction: {setup_results['direction']}
Entry Price: {setup_results['entry_price']}
Stop Loss: {setup_results['stop_loss']}
Target Price: {setup_results['target_price']}
Risk/Reward: {setup_results['risk_reward']}
Confidence: {setup_results['confidence']} (Score: {setup_results['score']})
Position Sizing: {setup_results.get('position_sizing', 'MODERATE')}
Risk Management: {setup_results.get('risk_management', 'BALANCED')}

Key Filters Passed:
- Market Regime Analysis
- Regime-Specific Filters
- Momentum Confirmation
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def market_regime_strategy(company_data, market_data_list=None, sector_data_dict=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param market_data_list:
    :param sector_data_dict:
    :return:
    """
    setup = MarketRegimeSetup()
    return setup.check_setup(company_data, market_data_list, sector_data_dict)