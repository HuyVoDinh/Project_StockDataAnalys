from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.filters.volume.volume_profile_filter import VolumeProfileFilter
from src.filters.support_resistance_filter import SupportResistanceFilter
from src.filters.risk.risk_filter import RiskFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class VolatilityBreakoutSetup:
    def __init__(self):
        self.volatility_filter = AdvancedVolatilityFilter()
        self.volume_filter = VolumeProfileFilter()
        self.sr_filter = SupportResistanceFilter()
        self.risk_filter = RiskFilter()

    def check_setup(self, company: CompanyData):
        """
        Professional Volatility Breakout Setup
        This setup looks for stocks in volatility contraction phases that are about to breakout

        Key components:
        1. Volatility contraction patter
        2. Volume confirmation
        3. Support/resistance levels
        4. Risk management
        :param company:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 30:
            return None

        company_data_list = company.company_data

        # 1. Check for volatility contraction phase
        contraction_phase, expansion_phase, breakout_potential = self.volatility_filter.volatility_contraction_expension(company_data_list, peropds=30)

        if not contraction_phase or not breakout_potential:
            return None

        # 2. Confirm with volume analysis
        volume_trend, institutional_activity, volume_confidence = self.volume_filter.volume_price_analysis(company_data_list, periods=20)

        # Need to see increasing volume as a confirmation
        if volume_trend != Trend.Up and not institutional_activity:
            return None

        # 3. Check support/resistance levels for breakout
        current_data = company_data_list[-1]
        support_levels = self.sr_filter.identify_support_levels(company_data_list, periods=20)
        resistance_levels = self.sr_filter.identify_resistance_level(company_data_list, periods=20)

        current_price = current_data.price.close_price

        # Look for breakoutopportunities
        breakout_signals = []

        # Resistance breakout
        for resistance in resistance_levels:
            if (current_price > resistance and company_data_list[-2].price.close_price <= resistance and
            abs(current_price - resistance) / resistance < 0.03): # Within 3% of resistance
                breakout_signals.append(("RESISTANCE", resistance))

        # Support breakout (upward)
        for support in support_levels:
            if (current_price > support and company_data_list[-2].price.close_price <= support and
            abs(current_price - support) / support < 0.03): # Within 3% of support
                breakout_signals.append(("SUPPORT", support))

        if not breakout_signals:
            return None

        # 4. Confirm breakout with volatility
        breakout_confirmed, direction, quality = self.volatility_filter.volatility_breakout_confirmation(company_data_list, current_data)

        if not breakout_confirmed or quality < 70:
            return None

        # 5. Risk management check
        if support_levels:
            closest_support = max([level for level in support_levels if level < current_price], default=None)
            if closest_support:
                stop_loss = closest_support * 0.98 # 2% below support
                entry_price = current_price
                target_price = current_price * 1.05 # 5% target

                # Check risk/reward ratio
                rr_ratio = (target_price - entry_price) / (entry_price - stop_loss) if (entry_price - stop_loss) > 0 else 0

                if rr_ratio < 1.5: # Minimum 1.5:1 risk/reward
                    return None

                # Check stop loss size
                stop_loss_pct = (entry_price - stop_loss) / entry_price * 100
                if stop_loss_pct > 4: # Maximum 4% stop loss
                    return None

                # Calculate position score
                score = (quality * 0.4) + (volume_confidence * 0.3) + (rr_ratio * 10 * 0.3)

                return {
                    'symbol': company.symbol,
                    'setup_type': 'VOLATILITY_BREAKOUT',
                    'direction': 'LONG',
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'target_price': target_price,
                    'risk_reward': rr_ratio,
                    'score': min(100, score),
                    'confidence': 'HIGH' if score > 80 else 'MEDIUM' if score > 60 else 'LOW',
                    'breakout_level': breakout_signals[0][1] if breakout_signals else None,
                    'breakout_type': breakout_signals[0][0] if breakout_signals else None,
                }

        return None

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        details = f"""
VOLATILITY BREAKOUT SETUP - {setup_result['symbol']}
===================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Entry Price: {setup_result['entry_price']}
Stop Loss: {setup_result['stop_loss']}
Target Price: {setup_result['target_price']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} Score: {setup_result['score']}
Breakout Level: {setup_result['breakout_level']}
Breakout Type: {setup_result['breakout_type']}

Key Filters Passed:
- Volatility Contraction Phase
- Volume Confirmation
- Breakout Confirmation
- Risk Management
"""

        return details.strip()

# Helper function to use the setup
def volatility_breakout_setup(company_data):
    """
    Function to be called by the trading system
    :param company_data:
    :return:
    """
    setup = VolatilityBreakoutSetup()
    return setup.get_setup_details(setup)