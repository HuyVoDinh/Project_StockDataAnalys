from src.filters.cointegration.cointegration_filter import CointegrationFilter
from src.filters.correlation.correlation_filter import CorrelationFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.momentum.momentum_filter import MomentumFilter
from src.enums.trend import Trend
from src.enums.signal import   Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class PairsTradingSetup:
    def __init__(self):
        self.correlation_filter = CorrelationFilter()
        self.risk_filter = RiskFilter()
        self.momentum_filter = MomentumFilter()
        self.cointegration_filter = CointegrationFilter()

    def check_setup(self, company: CompanyData, paired_asset_data_list=None):
        """
        Professional Pairs Trading Setup
        This setup identifies mean-reverting pairs for statistical arbitrage

        Key components:
        1. Pair selection based on correlation and cointegration
        2. Spread analysis and z-score calculation
        3. Entry/exit signals based on spread deviations
        4. Risk management
        :param company:
        :param paired_asset_data_list:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 60:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # Need paired asset for analysis
        if not paired_asset_data_list or len(paired_asset_data_list) < 60:
            return None

        # 1. Correlation analysis
        company_prices = [data.price.close_price for data in company_data_list[-60:]]
        paired_prices = [data.price.close_price for data in paired_asset_data_list[-60:]]

        if len(company_prices) != len(paired_prices):
            return None

        correlation = self.correlation_filter.calculate_correlation(company_prices, paired_prices)

        # Need high positive correlation for pairs trading
        if correlation < 0.8:
            return None

        # 2. Cointegration test
        cointegrated, hedge_ratio, p_value = self.cointegration_filter.johansen_cointegration_test(company_prices, paired_prices)

        # Need cointegration for mean-reverting relationship
        if not cointegrated:
            return None

        # 3. Spread analysis
        spread = self._calculate_spread(company_prices, paired_prices, hedge_ratio)
        spread_mean = sum(spread) / len(spread)
        spread_std = (sum((s - spread_mean) ** 2 for s in spread) / len(spread)) ** 0.5

        if spread_std == 0:
            return None

        # Current spread z-score
        current_spread = spread[-1]
        z_score = (current_spread - spread_mean) / spread_std

        # 4. Entry signals based on z-score
        signal = Signal.HOLD
        direction = "NEUTRAL"

        # Long spread (buy company, sell paired asset) when z-score < -2
        if z_score < -2:
            signal = Signal.BUY
            direction = "LONG_SPREAD"
        # Short spread (sell company , buy paried asset) when z_score > 2
        elif z_score > 2:
            signal = Signal.SELL
            direction = "SHORT_SPREAD"

        # Exit signals when z-score reverts to mean (between -0.5 and 0.5)
        exit_signal = False
        if -0.5 <= z_score <= 0.5:
            exit_signal = True

        # 5. Momentum confirmation
        price_momentum = self.momentum_filter.price_momentum(company_data_list, periods=10)
        paired_momentum = self.momentum_filter.price_momentum(paired_asset_data_list, periods=10)

        # Momentum should support the spread movement
        momentum_confirmed = True
        if signal == Signal.BUY and (price_momentum not in [Trend.Up, Trend.Strong_Up] or
        paired_momentum not in [Trend.Down, Trend.Strong_Down]):
            momentum_confirmed = False
        elif signal == Signal.SELL and (price_momentum not in [Trend.Down, Trend.Strong_Down] or
        paired_momentum not in [Trend.Up, Trend.Strong_Up]):
            momentum_confirmed = False

        if not momentum_confirmed and signal != Signal.HOLD:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 6. Risk management
        # Position sizing based on spread volatility
        position_sizing_factor = min(1.0, 0.1 / spread_std) # Inverse of spread volatility

        # Stop loss based on spreasd extremes
        spread_min = min(spread)
        spread_max = max(spread)
        stop_loss_distance = (spread_max - spread_min) * 0.3 # 30% of spread range

        if signal == Signal.BUY:
            stop_loss = spread_mean - stop_loss_distance
        elif signal == Signal.SELL:
            stop_loss = spread_mean + stop_loss_distance
        else:
            stop_loss = 0

        # Target based on mean reversion
        if signal == Signal.BUY:
            target = spread_mean # revert to mean
        elif signal == Signal.SELL:
            target = spread_mean # Revert to mean

        else:
            target = 0

        # 7. RR calculation for spread trade
        if signal != Signal.HOLD and spread_std > 0:
            rr_ratio = abs(target - current_spread) / abs(stop_loss - current_spread) if abs(stop_loss - current_spread) > 0 else 0
        else:
            rr_ratio = 0

        # Need minimum 1.5:1 risk/reward
        if rr_ratio < 1.5 and signal != Signal.HOLD:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 8. Setup scoring
        # Weight factors: correlation (25%), cointegration (25%), z-score (20%), momentum (15%), rr(15%)
        score = (
            correlation * 100 * 0.25 +
            (1 - p_value) * 100 * 0.25 + # Lower p-value = better cointegration
            min(100, abs(z_score) * 25) * 0.2 + # Scale z-score to 0-100
            (70 if momentum_confirmed else 30) + 0.15 +
            min(100, rr_ratio * 20) * 0.15 # Scale RR ratio to 0-100
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'PARIS_TRADING',
            'direction': direction,
            'signal': signal,
            'paired_asset': paired_asset_data_list[0].symbol if hasattr(paired_asset_data_list[0], 'symbol') else 'UNKNOWN',
            'hedge_ratio': hedge_ratio,
            'correlation': correlation,
            'cointegration_p_value': p_value,
            'current_spread': current_spread,
            'spread_mean': spread_mean,
            'spread_std': spread_std,
            'z_score': z_score,
            'position_size_factor': position_sizing_factor,
            'stop_loss': stop_loss,
            'target': target,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
            'exit_signal': exit_signal,
            'momentum_confirmed': momentum_confirmed
        }

    def _calculate_spread(self, asset1_prices, asset2_prices, hedge_ratio):
        """
        Calculate the spread between two assets
        :param asset1_prices: Prices of first asset
        :param asset2_prices: Prices of second asset
        :param hedge_ratio: Hedge ratio from cointegration
        :return: Spread values
        """
        if len(asset1_prices) != len(asset2_prices):
            return []

        spread = [price1 - (hedge_ratio * price2) for price1, price2 in zip(asset1_prices, asset2_prices)]
        return spread

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found."

        details = f"""
PAIRS TRADING SETUP - {setup_result['symbol']}
=========================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Paired Asset: {setup_result['paired_asset']}
Hedge Ratio: {setup_result['hedge_ratio']}
Correlation: {setup_result['correlation']}
Cointegration: {setup_result['cointegration_p_value']}
Current Spread: {setup_result['current_spread']}
Spread Mean: {setup_result['spread_mean']}
Spread Std: {setup_result['spread_std']}
Z-Score: {setup_result['z_score']}
Position Size: {setup_result['position_size_factor']}
Stop Loss: {setup_result['stop_loss']}
Target: {setup_result['target']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})
Exit Signal: {setup_result['exit_signal']}
Momentum Confirmed: {setup_result['momentum_confirmed']}

Key filters Passed:
- High Correlation:
- Cointegration Test:
- Spread Analysis
- Momentum Confirmation
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def pairs_trading_setup(company_data, paired_asset_data_list=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param paired_asset_data_list:
    :return:
    """
    setup = PairsTradingSetup()
    return setup.check_setup(company_data, paired_asset_data_list)


