from src.filters.correlation.correlation_filter import CorrelationFilter
from src.filters.momentum.momentum_rotation_filter import MomentumRotationFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData
import numpy as np

class StatisticalArbitrageSetup:
    def __init__(self):
        self.correlation_filter = CorrelationFilter()
        self.momentum_filter = MomentumRotationFilter()
        self.risk_filter = RiskFilter()
        self.volatility_filter = AdvancedVolatilityFilter()

    def check_setup(self, company: CompanyData, market_data_list=None, sector_data_list=None, peer_group_data_dict=None):
        """
        Professional Statistical Arbitrage Setup
        This setup identifies mispriced assets relative to their peers/market

        Key components:
        1. Cross-sectional mean reversion
        2. Factor model analysis
        3. Momentum and volatility screening
        4. Risk management
        :param company:
        :param market_data_list:
        :param sector_data_list:
        :param peer_group_data_dict:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 30:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # Need market and peer data for statistical arbitrage
        if not market_data_list or not peer_group_data_dict:
            return None

        # 1. Calculate asset's z-score relative to peers (cross-sectional analysis)
        peer_returns = self._calculate_peer_returns(peer_group_data_dict, periods=30)
        company_return = self._calculate_asset_return(company_data_list, periods=30)

        if not peer_returns:
            return None

        # Calculate cross-sectional z-score
        peer_mean_return = sum(peer_returns) / len(peer_returns)
        peer_std_return = (sum((r - peer_mean_return) ** 2 for r in peer_returns) / len(peer_returns)) ** 0.5

        if peer_std_return == 0:
            return None

        cross_sectional_z_score = (company_return - peer_mean_return) / peer_std_return

        # 2. Factor model analysis (simplified Fama-French 3-factor model)
        market_return = self._calculate_asset_return(market_data_list, periods=30)
        smb_factor, hml_factor = self._calculate_factors(company_data_list, market_data_list, sector_data_list, periods=30)

        # Calculate alpha (excess return not explained by factors)
        alpha = company_return - (0.01 + 1.0 * market_return + 0.5 * smb_factor + 0.3 * hml_factor)

        # 3. Momentum analysis
        relative_momentum, outperformace, momentum_rank = self.momentum_filter.calculate_relative_momentum(company_data_list, market_data_list, periods=30)

        # 4. Volatility analysis
        volatility_regime, volatility_trend, volatility_risk = self.volatility_filter.volatility_regime_analysis(company_data_list, periods=20)

        # 5. Entry signals based on statistical mispricing
        signal = Signal.HOLD
        direction = "NEUTRAL"

        # Long undervalued assets (negative z-score, positive alpha)
        if cross_sectional_z_score < -.15 and alpha > 0.02: # 2% excess return threshold
            signal = Signal.BUY
            direction = "LONG"
        # Short overvalued assets (positive z-scorem negative alpha)
        elif cross_sectional_z_score > 1.5 and alpha < -0.02: # -2% excess return threshold
            signal = Signal.SELL
            direction = "SHORT"

        # 6. Risk management
        # Position sizing based on statistical significance
        position_sizing_factor = min(1.0, abs(cross_sectional_z_score) / 3.0) # Scale z-score to 0-1

        # Adjust for volatility regime
        if volatility_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            position_sizing_factor *= 0.6
        elif volatility_risk == RiskLevel.MEDIUM:
            position_sizing_factor *= 0.8

        # Stop loss based on historical volatility
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            stop_loss_distance = 3 * current_data.ATR_14 # 3x ATR stop
        else:
            # Fallback to percentage-based stop
            stop_loss_distance = current_price * 0.05 # 5% stop

        if signal == Signal.BUY:
            stop_loss = current_price - stop_loss_distance
        elif signal == Signal.SELL:
            stop_loss = current_price + stop_loss_distance
        else:
            stop_loss = 0

        # Target based on mean reversion expectation
        expected_reversion = peer_std_return * abs(cross_sectional_z_score)
        if signal == Signal.BUY:
            target = current_price * (1 + expected_reversion)
        elif signal == Signal.SELL:
            target = current_price * (1 - expected_reversion)
        else:
            target = 0

        # 7, Risk/Reward calculation
        if signal != Signal.HOLD and stop_loss_distance > 0:
            rr_ratio = abs(target - current_price) / stop_loss_distance
        else:
            rr_ratio = 0

        # Need minimum 2:1 risk/reward
        if rr_ratio < 2.0 and signal != Signal.HOLD:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 8. Setup scoring
        # Weight factors: z-score (25%), alpha (25%), momentum (20%), risk/reward (15%), volatility adjustment (15%)
        score = (
            min(100, abs(cross_sectional_z_score) * 30) * 0.25 +
            min(100, abs(alpha) * 2500) * 25 +
            momentum_rank * 0.2 +
            min(100, rr_ratio * 15) * 0.15 +
            (100 - volatility_risk.value * 25) * 0.15
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'STATISTICAL_ARBITRAGE',
            'direction': direction,
            'signal': signal,
            'current_price': current_price,
            'cross_sectional_z_score': cross_sectional_z_score,
            'alpha': alpha,
            'factor_exposures': {
                'market_beta': 1.0,
                'smb': smb_factor,
                'hml': hml_factor,
            },
            'relative_momentum': outperformace,
            'momentum_rank': momentum_rank,
            'volatility_risk': volatility_risk.name if hasattr(volatility_risk, 'name') else str(volatility_risk),
            'position_size_factor': position_sizing_factor,
            'stop_loss': stop_loss,
            'target': target,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
            'peer_group_stats': {
                'mean_return': peer_mean_return,
                'std_return': peer_std_return,
                'peer_count': len(peer_returns),
            }
        }

    def _calculate_peer_returns(self, peer_group_data_dict, periods=30):
        """
        Calculate returns for peer group assets
        :param peer_group_data_dict: Dictionary of peer asset data
        :param periods: Number of periods for return calculation
        :return: List of peer returns
        """
        peer_returns = []

        for symbol, data_list in peer_group_data_dict.items():
            if len(data_list) >= periods:
                prices = [data.price.close_price for data in data_list[-periods:] if data.price.close_price >0]
                if len(prices) >= 2 and prices[0] > 0:
                    return_val = (prices[-1] - prices[0]) / prices[0]
                    peer_returns.append(return_val)

        return peer_returns

    def _calculate_asset_return(self, data_list, periods=30):
        """
        Calculate return for a single asset
        :param data_list: List of asset data
        :param periods: Number of periods for return calculation
        :return: Asset return
        """
        if len(data_list) < periods:
            return 0
        prices = [data.price.close_price for data in data_list[-periods:] if data.price.close_price >0]
        if len(prices) < 2 or prices[0] <= 0:
            return 0

        return (prices[-1] - prices[0]) / prices[0]

    def _calculate_factor(self, company_data_list, market_data_list, sector_data_list=None, periods=30):
        """
        Calculate factor exposures (simplified)
        :param company_data_list: Company data
        :param market_data_list: Market data
        :param sector_data_list: Sector data
        :param periods: Number of periods
        :return: Tuple of (SMB factor, HML factor)
        """
        # SMB (Small Minus Big) -size factor
        # Simplified difference between small-cap and large-cap returns
        if sector_data_list and len(sector_data_list) >= periods:
            small_cap_return = self._calculate_asset_return(sector_data_list, periods)
        else:
            small_cap_return = 0

        market_return = self._calculate_asset_return(market_data_list, periods)
        smb_factor = small_cap_return - market_return

        # HML (High Minus Low) - value factor
        # Simplified: difference between high book-to-market and low book-to-market returns
        # In practice, this would use actual book-to-market ratios
        hml_factor = 0.01 # Simplified assumption

        return smb_factor, hml_factor

    def get_setup_details(self, setup_result):
        """
        Get detail information about the setup for reporting
        :param setup_result:
        :return:
        """

        details = f"""
STATISTICAL ARBITRAGE SETUP - {setup_result['symbol']}
=======================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Current Price: {setup_result['current_price']}
Cross-Sectional Z-Score: {setup_result['cross_sectional_z_score']}
Alpha: {setup_result['alpha']}
Relative Momentum: {setup_result['relative_momentum']}
Momentum Rank: {setup_result['momentum_rank']}
Volatility Risk: {setup_result['volatility_risk']}
Position Size: {setup_result['position_size_factor']}
Stop Loss: {setup_result['stop_loss']}
Target: {setup_result['target']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})

Factor Exposures:
- Market Beta: {setup_result['factor_exposures']['market_beta']}
- SMB: {setup_result['factor_exposures']['smb']}
- HML: {setup_result['factor_exposures']['hml']}

Peer Group Statistics:
- Mean Return: {setup_result['peer_group_stats']['mean_return']}
- Std Dev Return: {setup_result['peer_group_stats']['std_return']}
- Peer Count: {setup_result['peer_group_stats']['peer_count']}

Key Filters Passed
- Cross-Sectional Analysis
- Factor Model Analysis
- Momentum Screening
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def statistical_arbitrage_setup(company_data, market_data_list=None, sector_data_list=None, peer_group_data_list=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param market_data_list:
    :param sector_data_list:
    :param peer_group_data_list:
    :return:
    """
    setup = StatisticalArbitrageSetup()
    return setup.check_setup(company_data, market_data_list, sector_data_list, peer_group_data_list)