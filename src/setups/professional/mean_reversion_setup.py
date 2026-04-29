from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.filters.momentum.momentum_filter import MomentumFilter
from src.filters.support_resistance_filter import SupportResistanceFilter
from src.filters.risk.risk_filter import RiskFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class MeanReversionSetup:
    def __init__(self):
        self.volatility_filter = AdvancedVolatilityFilter()
        self.momentum_filter = MomentumFilter()
        self.sr_filter = SupportResistanceFilter()
        self.risk_filter = RiskFilter()

    def check_setup(self, company: CompanyData):
        """
        Professional Mean Reversion Setup
        This strategy looks for stocks that have moved too far in one direction and are likely to revert

        Key components:
        1. Overbought/Oversold conditions
        2. Volatility analysis
        3. Support/Resistance levels
        4. Risk management
        :param company:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 20:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # 1. Check for mean reversion signals using volatility filter
        mean_reversion_signal, strength, confidence = self.volatility_filter.volatility_mean_reversion(company_data_list, periods=20)

        if mean_reversion_signal == Trend.Sideway or confidence < 60:
            return None

        # 2. Confirm with RSI
        rsi_signal = self.momentum_filter.rsi_momentum(current_data, overbought=70, oversold=30)

        # Check if RSI confirms the mean reversion signal
        if mean_reversion_signal == Trend.Down and rsi_signal != Signal.SELL:
            return None
        elif mean_reversion_signal == Trend.Up and rsi_signal != Signal.BUY:
            return None

        # 3. Check support/resistance for reversion levels
        support_levels = self.sr_filter.identify_support_levels(company_data_list, periods=20)
        resistance_levels = self.sr_filter.identify_resistance_level(company_data_list, periods=20)

        current_price = current_data.price.close_price

        # 4. Risk management and setup details
        if mean_reversion_signal == Trend.Down: # Overbought - looking to short (or avoid going long)
            # Find resistance level to short toward
            if resistance_levels:
                closest_resistance = min([level for level in resistance_levels if level > current_price], default=None)
                if closest_resistance:
                    entry_price = current_price
                    stop_loss = closest_resistance * 1.02 # 2% above resistance
                    target_price = current_price * 0.95 # 5% down target

                    # Check risk/reward ratio
                    rr_ratio = (entry_price - target_price) / (stop_loss - entry_price) if (stop_loss - entry_price) > 0 else 0

                    if rr_ratio < 1.5: # Minimum 1.5:1 risk/reward
                        return None

                    # Check if move is significant enough
                    move_pct = (entry_price - target_price) / entry_price * 100
                    if move_pct < 2: # Minimum 2% expected move
                        return None

                    # Calculate position score
                    score = (confidence * 0.4) + (strength * 0.3) + (rr_ratio * 10 + 0.3)

                    return {
                        'symbol': company.symbol,
                        'setup_type': 'MEAN_REVERSION_SHORT',
                        'direction': 'SHORT',
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'target_price': target_price,
                        'risk_reward': rr_ratio,
                        'score': min(100, score),
                        'confidence': 'HIGH' if score > 80 else 'MEDIUM' if score > 60 else 'LOW',
                        'resistance_level': closest_resistance,
                        'reversion_strength': strength
                    }
        elif mean_reversion_signal == Trend.Up: # Oversold - looking to go long
            # Find support level to buy toward
            if support_levels:
                closest_support = max([level for level in support_levels if level < current_price], default=None)
                if closest_support:
                    entry_price = current_price
                    stop_loss = closest_support * 0.98 # 2% below support
                    target_price = current_price * 1.05 # 5% up target

                    # Check risk/reward ratop
                    rr_ratio = (target_price - entry_price) / (entry_price - stop_loss) if (entry_price - stop_loss) > 0 else 0

                    if rr_ratio < 1.5: # Minimum 1.5:1 risk/reward
                        return None

                    # Check if move is significant enoug
                    move_pct = (target_price - entry_price) / entry_price * 100
                    if move_pct < 2: # Minimum 2% expected move
                        return None

                    # Calculate position score
                    score = (confidence * 0.4) + (strength * 0.3) + (rr_ratio * 10 + 0.3)

                    return {
                        'symbol':company.symbol,
                        'setup_type': 'MEAN_REVERSION_LONG',
                        'direction': 'LONG',
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'target_price': target_price,
                        'risk_reward': rr_ratio,
                        'score': min(100, score),
                        'confidence': 'HIGH' if score > 80 else 'MEDIUM' if score > 60 else 'LOW',
                        'support_level': closest_support,
                        'reversion_strength': strength
                    }
        return None

    def get_setup_details(self, setup_results):
        """
        Get detailed information about the setup for reporting
        :param setup_results:
        :return:
        """
        if not setup_results:
            return "No valid setup found"

        setup_type = "MEAN REVERSION (SHORT)" if "SHORT" in setup_results['setup_type'] else "MEAN REVERSION (LONG)"

        details = f"""
{setup_type} SETUP - {setup_results['symbol']}
===============================================
Setup Type: {setup_results['setup_type']}
Direction: {setup_results['direction']}
Entry Price: {setup_results['entry_price']}
Stop Loss: {setup_results['stop_loss']}
Target Price: {setup_results['target_price']}
Risk Reward: {setup_results['risk_reward']}
Confidence: {setup_results['confidence']} (Score: {setup_results['score']})
Reversion Strength: {setup_results['reversion_strength']}

Key Filters Passed:
- Mean Reversion Signal
- RSI Confirmation
- Support/Resistance
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def mean_reversion_setup(company_data):
    """
    Function to be called by the trading system
    :param company_data:
    :return:
    """
    setup = MeanReversionSetup()
    return setup.check_setup(company_data)
