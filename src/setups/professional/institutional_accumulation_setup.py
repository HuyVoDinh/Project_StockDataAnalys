from src.filters.volume.volume_profile_filter import VolumeProfileFilter
from src.filters.momentum.momentum_filter import MomentumFilter
from src.filters.support_resistance_filter import SupportResistanceFilter
from src.filters.risk.risk_filter import RiskFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class InstitutionalAccumulationSetup:
    def __init__(self):
        self.volume_filter = VolumeProfileFilter()
        self.momentum_filter = MomentumFilter()
        self.sr_filter = SupportResistanceFilter()
        self.risk_filter = RiskFilter()

    def check_setup(self, company: CompanyData):
        """
        Professional Institutional Accumulation Setup
        This strategy looks for stocks where institutions are accumulation shares

        Key components:
        1. Institutional volume activity
        2. Accumulation/Distribution analysis
        3. Momentum confirmation
        4. Support levels
        5. Risk Management
        :param company:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 25:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # 1. Check for institutional activity
        volume_trend, institutional_activity, volume_confidence = self.volume_filter.volume_profile_analysis(company_data_list, periods=25)

        if not institutional_activity or volume_confidence < 60:
            return None

        # 2. Check accumulation/distribution
        accumulation_signal, distribution_signal, ad_strength = self.volume_filter.volume_accumulation_distribution(company_data_list,periods=30)

        # wanna see accumulation, not distribution
        if not accumulation_signal or distribution_signal:
            return None

        # 3. Check institutional flow
        institutional_flow, flow_strength, flow_quality = self.volume_filter.institutional_flow_analysis(company_data_list, periods=25)

        if institutional_flow != Trend.Up or flow_strength < 50:
            return None
        # 4. Confirm with momentum
        price_momentum = self.momentum_filter.price_momentum(company_data_list, periods=10)

        # Wanna see positive momentum or consolidation before breakout
        if price_momentum not in [Trend.Up, Trend.Good, Trend.Sideway]:
            return None

        # 5. Check for support levels (accumulation happens at support)
        support_levels = self.sr_filter.identify_support_levels(company_data_list, periods=20)

        current_price = current_data.price.close_price
        if support_levels:
            # Check if price is near support (within 2%)
            closest_support = max([level for level in support_levels if level < current_price], default=None)
            if closest_support and abs(current_price - closest_support) / closest_support < 0.02:
                # Price is near support - good for accumulation setup

                # 6. Risk management check
                stop_loss = closest_support * 0.97 # 3% below support
                entry_price = current_price
                target_price = current_price * 1.08 # 8% target (institutional moves)

                # Check rist/reward ratio
                rr_ratio = (target_price - entry_price) / (entry_price - stop_loss) if (entry_price - stop_loss) > 0 else 0.0

                if rr_ratio < 2.0: # Minimum 2:1 risk/reward for institutional setups
                    return None

                # Check stop loss size
                stop_loss_pct = (entry_price - stop_loss) / entry_price * 100
                if stop_loss_pct > 5: # Maximum 5% stop loss
                    return None

                # Calculate position score
                score = (volume_confidence * 0.3) + (ad_strength * 0.2) + (flow_quality * 0.2) + (rr_ratio * 10 * 0.3)
                return {
                    'symbol': company.symbol,
                    'setup_type': 'INSTITUTIONAL_ACCUMULATION',
                    'direction': 'LONG',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'target_price': target_price,
                    'risk_reward': rr_ratio,
                    'score': min(100, score),
                    'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
                    'support_level': support_levels,
                    'accumulation_strength': ad_strength
                }

        return None

    def get_setup_details(self, setup_result):
        """Get detailed information about the setup for reporting"""
        if not setup_result:
            return "No valid setup found"

        details = f"""
INSTITUTIONAL ACCUMULATION SETUP - {setup_result['symbol']}
============================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Entry Price: {setup_result['entry_price']}
Stop Loss: {setup_result['stop_loss']}
Target Price: {setup_result['target_price']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})
Support Levels: {setup_result['support_levels']}
Accumulation Strength: {setup_result['accumulation_strength']}

Key Filters Passed: 
- Institutional Activity
- Accumulation Signal
- Institutional Flow
- Support Proximity
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def institutional_accumulation_setup(company_data):
    """
    Function to be called by the trading system
    """
    setup = InstitutionalAccumulationSetup()
    return setup.check_setup(company_data)
    return setup.check_setup(company_data)

