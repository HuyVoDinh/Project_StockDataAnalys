from src.filters.momentum.momentum_filter import MomentumFilter
from src.filters.momentum.momentum_rotation_filter import MomentumRotationFilter
from src.filters.correlation.correlation_filter import CorrelationFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.market_trend_filter import MarketTrendFilter
from src.filters.market_regime.market_regime_filter import MarketRegimeFilter
from src.enums.trend import Trend, MarketState
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class RelativeStrengthSetup:
    def __init__(self):
        self.momentum_filter = MomentumRotationFilter()
        self.correlation_filter = CorrelationFilter()
        self.risk_filter = RiskFilter()
        self.market_regime_filter = MarketRegimeFilter()

    def check_setup(self, company: CompanyData, benchmark_data_list=None, sector_data_list=None,
                    peer_group_data_dict=None, market_data_list=None):
        """
        Professional Relative Strength Setup
        This strategy identifies stocks outperforming their benchmarks, sectors, and peers
        :param company:
        :param benchmark_data_list:
        :param sector_data_list:
        :param peer_group_data_dict:
        :param market_data_list:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 30:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # Need benchmark data for relative strength analysis
        if not benchmark_data_list:
            return None

        # 1. Calculate relative momentum vs benchmark
        benchmark_momentum, relative_performance, momentum_rank = self.momentum_filter.calculate_relative_momentum(
            company_data_list, benchmark_data_list, periods=30
        )

        # Need to be outperforming benchmark
        if benchmark_momentum not in [Trend.Up, Trend.Strong_Up]:
            return None

        # 2. Calculate relative strength vs sector (if provided)
        if sector_data_list and len(sector_data_list) >= 30:
            sector_momentum, sector_realtive, sector_rank = self.momentum_filter.calculate_relative_momentum(
                company_data_list, sector_data_list, periods=30
            )
        else:
            sector_momentum = Trend.Up
            sector_relative = 0.02
            sector_rank = 75

        # 3. Calculate relative strength vs peers (if provided)
        peer_strength_score = 80 # Default score
        if peer_group_data_dict:
            peer_strength_score = self._analyze_peer_group_strength(company_data_list, peer_group_data_dict)
            if peer_strength_score < 60: # Need to be in top 40% of peer
                return None

        # 4. Correlation analysis with benchmark
        if len(benchmark_data_list) >= 30:
            # Extract prices for correlation calculation
            company_prices = [data.price.close_price for data in company_data_list[-30:] if data.price.close_price > 0]
            benchmark_prices = [data.price.close_price for data in benchmark_data_list[-30:] if data.price.close_price > 0]

            if len(company_prices) >= 20 and len(benchmark_prices) >= 20:
                correlation = self.correlation_filter.calculate_correlation(company_prices, benchmark_prices)
                # Want positive but not perfect correlation (diversification benefit)
                if correlation < 0.2 or correlation > 0.9:
                    return None
            else:
                correlation = 0.5 # Default assumption
        else:
            correlation = 0.5

        # 5. Market regime compatibility
        if market_data_list:
            market_regime, volatility_regime, _ = self.market_regime_filter.market_regime_classification(market_data_list, {}, periods=30)
        else:
            market_regime = MarketState.MID_TREND
            volatility_regime = Trend.Good

        # 6. Risk management
        current_price = current_data.price.close_price
        stop_loss = self._calculate_stop_loss(current_data, company_data_list, sector_data_list, peer_group_data_dict)
        target_price = current_price * 1.15 # 15% target for strong relative performers

        # Check risk/reward
        rr_ratio = (target_price - current_price) / (current_price - stop_loss) if (current_price - stop_loss) > 0 else 0
        if rr_ratio < 2.0: # Need at least 2:1 rr
            return None

        # Calculate position score
        # Weight factors: benchmark outperformance (30%), sector outperformance (25%), peer strength (25%), rr (20%)
        score = (momentum_rank * 0.3) + (sector_rank * 0.25) + (peer_strength_score * 0.25) + (rr_ratio * 5 * 0.2)

        return {
            'symbol': company.symbol,
            'setup_type': 'RELATIVE_STRENGTH',
            'direction': 'LONG',
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
        }

    def _analyze_peer_group_strength(self, company_data_list, peer_group_data_dict):
        """Analyze relative strength against peer group."""
        if not peer_group_data_dict or len(company_data_list) < 20:
            return 80 # Default score

        # Calculate company momentum
        company_prices = [data.price.close_price for data in company_data_list[-20:] if data.price.close_price > 0]
        if len(company_prices) >= 2 and company_prices[0] > 0:
            company_momentum = (company_prices[-1] - company_prices[0]) / company_prices[0]
        else:
            company_momentum = 0

        # Calculate peer group momentums
        peer_momentums = []
        for peer_symbol, peer_data_list in peer_group_data_dict.items():
            if len(peer_data_list) > 20:
                peer_prices = [data.price.close_price for data in peer_data_list[-20:] if data.price.close_price > 0]
                if len(peer_prices) >= 2 and peer_prices[0] > 0:
                    peer_momentum = (peer_prices[-1] - peer_prices[0]) / peer_prices[0]
                    peer_momentums.append (peer_momentum)

        if not peer_momentums:
            return 80

        # Calculate percentile rank
        better_peers = sum(1 for pm in peer_momentum if company_momentum > pm)
        percentile_rank = (better_peers / len(peer_momentums)) * 100

        return percentile_rank

    def _calculate_stop_loss(self, current_data, company_data_list, sector_data_list=None):
        """
        Calculate appropriate stop loss for relative strength setup
        :param current_data:
        :param company_data_list:
        :param sector_data_list:
        :return:
        """
        current_price = current_data.price.close_price

        # Use multiple methods and take the most conservative (highest) stop loss

        # Method 1: ATR-based stop
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            atr_stop = current_price - (2.5 * current_data.ATR_14) # Wider stop for momentum plays
        else:
            atr_stop = current_price * 0.92 # 8% default stop

        # Method 2: Support level stop
        support_stop = current_price * 0.9 # 10% below current prices as default
        if company_data_list and len(company_data_list) >= 15:
            recent_lows = [data.price.low_price for data in company_data_list[-15:]]
            if recent_lows:
                support_level = min(recent_lows)
                support_stop = support_level * 0.98 # 2% below support

        # Method 3: Sector-based stop (if provided)
        sector_stop = atr_stop # Default to atr stop
        if sector_data_list and len(sector_data_list) >= 15:
            sector_lows = [data.price.low_price for data in sector_data_list[-15:]]
            if sector_lows:
                sector_support = min(sector_lows)
                sector_stop = max(sector_support * 0.95, current_price * 0.85) # At least 15% stop

        # Use the highest (most conservative) stop loss
        stop_loss = max(atr_stop, support_stop, sector_stop, current_price * 0.85) # Minimum 15% stop

        return stop_loss

    def get_setup_details(self, setup_result):
        """
        Get details about the setup
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        details = f"""
RELATIVE STRENGTH SETUP - {setup_result['symbol']}
========================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Entry Price: {setup_result['entry_price']}
Stop Loss: {setup_result['stop_loss']}
Target Price: {setup_result['target_price']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})
Benchmark Outperformance: {setup_result['benchmark_outperformance']}
Sector Outperformance: {setup_result['sector_outperformance']}
Peer Group Strength: {setup_result['peer_strength']}
Correlation with Benchmark: {setup_result['correlation']}
Market Regime: {setup_result['market_regime']}

Key filter Passed:
- Benchmark Relative Strength
- Sector Relative Strength
- Peer Group Analysis
- Correlation Analysis
- Risk Management
"""

        return details.strip()\

# Helper function to use the setup
def relatvie_strength_strategy(company_data, benchmark_data_list=None, sector_data_list=None, peer_group_data_dict=None, market_data_list=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param benchmark_data_list:
    :param sector_data_list:
    :param peer_group_data_dict:
    :param market_data_list:
    :return:
    """
    setup = RelativeStrengthSetup()
    return setup.check_setup(company_data, benchmark_data_list, sector_data_list, peer_group_data_dict, market_data_list)