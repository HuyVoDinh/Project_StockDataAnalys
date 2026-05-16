from src.filters.multi_timeframe.multi_timeframe_filter import MultiTimeframeFilter
from src.filters.momentum.momentum_filter import MomentumFilter
from src.filters.support_resistance_filter import  SupportResistanceFilter
from src.filters.risk.risk_filter import RiskFilter
from src.enums.trend import Trend, MarketState
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class MultiTimeframeSetup:
    def __init__(self):
        self.mt_filter = MultiTimeframeFilter()
        self.momentum_filter = MomentumFilter()
        self.sr_filter = SupportResistanceFilter()
        self.risk_filter = RiskFilter()

    def check_setup(self, company: CompanyData, multi_timeframe_data_dict=None):
        """
        Professional Multi-Timeframe Setup
        This setup combine analysis across multiple timeframes for higher probability setups

        Key components:
        1. Multi-timeframe trend confirmation
        2. Multi-timeframe momentum alignment
        3. Multi-timeframe support resistance confluence
        4. Risk management across timeframs
        :param self:
        :param company:
        :param multi_timeframe_data_dict:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 20:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # Need multi-timeframe data for analysis
        if not multi_timeframe_data_dict:
            return None

        # 1. Multi-timeframe trend analysis
        timeframe_confirmation, dominant_trend, timeframe_alignment = self.mt_filter.timeframe_confirmation(
            multi_timeframe_data_dict, timeframes=['daily', 'weekly', 'monthly']
        )

        # Need at least moderate confirmation across timeframes
        if timeframe_confirmation in ["NO_CONFIRMATION", "WEAK_BULLISH", "WEAK_BEARISH"]:
            return None

        # 2. Multi-timeframe momentum analysis
        momentum_regime, momentum_consistency, momentum_quality = self.mt_filter.momentum_multiframe(
            multi_timeframe_data_dict.get('momentum', {}), timeframes=['daily', 'weekly', 'monthly']
        )

        # Need consistent momentum across timeframes
        if momentum_consistency < 60: # Less than 60% consistency
            return None

        # 3. Multi-timeframe moving average alignment
        ma_alignment_score, ma_alignment_quality, ma_direction = self.mt_filter.moving_average_alignment(
            multi_timeframe_data_dict.get('moving_averages', {}), timeframes=['daily', 'weekly', 'monthly']
        )

        # Need high quality alignment
        if ma_alignment_quality not in ["HIGH", "MODERATE"]:
            return None

        # 4. Multi-timeframe support/resistance confluence
        sr_confluence_score, key_levels, timeframe_importance = self.mt_filter.support_resistance_multiframe(
            multi_timeframe_data_dict.get('support_resistance', {}), timeframes=['daily', 'weekly', 'monthly']
        )

        # Need significant confluence
        if sr_confluence_score < 50:
            return None

        # 5. Multi-timeframe volatility analysis
        volatility_regime, regime_consistency, risk_assessment = self.mt_filter.volatility_regime_multiframe(
            multi_timeframe_data_dict.get('volatility', {}), timeframes=['daily', 'weekly', 'monthly']
        )

        # 6. Current timeframe analysis
        current_price = current_data.price.close_price

        # Check if price is near key support/resistance levels
        near_support = False
        near_resistance = False
        support_level = 0
        resistance_level = 0

        if key_levels:
            for level in key_levels:
                if abs(current_price - level) / current_price < 0.01: # Within 1% of level
                    if level < current_price:
                        near_support = True
                        support_level = level
                    else:
                        near_resistance = True
                        resistance_level = level

        # 7. Risk management based on multi-timeframe analysis
        # Determine position size based on timeframe importance
        total_timeframe_importance = sum(timeframe_importance.values())
        if total_timeframe_importance > 0:
            position_sizing_factor = timeframe_importance.get('daily', 0) / total_timeframe_importance
        else:
            position_sizing_factor = 0.5 # Default 50%

        # Adjust for volatility regime
        if volatility_regime == "HIGH":
            position_sizing_factor *= 0.7 # Reduce position size in high volatility
        elif volatility_regime == "LOW":
            position_sizing_factor *= 1.3 # Increase position size in low volatility

        # 8. Entry and exit levels
        if timeframe_confirmation in ["STRONG_BULLISH", "MODERATE_BULLISH"]:
            # Bullish setup
            entry_price = current_price
            if near_support and support_level > 0:
                stop_loss = support_level * 0.99 # 1% below support
            else:
                stop_loss = current_price * 0.97 # 3% default stop

            if near_resistance and resistance_level > 0:
                target_price = resistance_level * 1.01 # 1% above resistance
            else:
                # Use momentume projection
                momentum_target = current_price * (1 + (momentum_quality / 1000))
                target_price = max(current_price * 1.05, momentum_target) # Minimum 5% target

        elif timeframe_confirmation in ["STRONG_BEARISH", "MODERATE_BEARISH"]:
            # Bullish setup
            entry_price = current_price
            if near_resistance and resistance_level > 0:
                stop_loss = resistance_level * 1.01  # 1% above resistance
            else:
                stop_loss = current_price * 1.03  # 3% default stop

            if near_support and support_level > 0:
                target_price = support_level * 0.99  # 1% below support
            else:
                # Use momentume projection
                momentum_target = current_price * (1 - (momentum_quality / 1000))
                target_price = min(current_price * 1.05, momentum_target)  # Minimum 5% targe
        else:
            return None

        # 9. Risk/Reward calculation
        rr_ratio = abs(target_price - entry_price) / abs(entry_price - stop_loss) if abs(entry_price - stop_loss) > 0 else 0

        # Need minimum 1.5:! rr
        if rr_ratio < 1.5:
            return None

        # 10. Setup scoring
        # Weight factors: trend confirmation (30%), momentum (25%), MA alignment (20%)
        # SR confluence (15%), rr(15%)
        score = (
        (70 if timeframe_confirmation in ["STRONG_BULLISH", "STRONG_BEARISH"] else 50) * 0.3 +
        momentum_quality * 0.25 +
        ma_alignment_score * 0.2 +
        sr_confluence_score * 0.15 +
        min(100, rr_ratio * 20) * 0.1 # Scale RR ratio to 0-100
        )

        # Determine direction based on timeframe confirmation
        if timeframe_confirmation in ["STRONG_BULLISH", "MODERATE_BULLISH"]:
            direction = "LONG"
            signal = Signal.BUY
        elif timeframe_confirmation in ["STRONG_BEARISH", "MODERATE_BEARISH"]:
            direction = "SHORT"
            signal = Signal.SELL
        else:
            direction = "NEUTRAL"
            signal = Signal.HOLD

        return {
                'symbol': company.symbol,
                'setup_type': 'MULTI_TIMEFRAME',
                'direction': direction,
                'signal': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target_price': target_price,
                'risk_reward': rr_ratio,
                'position_size_factor': position_sizing_factor,
                'score': min(100, score),
                'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
                'timeframe_confirmation': timeframe_confirmation,
                'dominant_trend': dominant_trend.name if hasattr(dominant_trend, 'name') else str(dominant_trend),
                'momentum_consistency': momentum_consistency,
                'ma_alignment_quality': ma_alignment_quality,
                'sr_confluence_score': sr_confluence_score,
                'volatility_regime': volatility_regime,
                'risk_assessment': risk_assessment
        }

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        details = f"""
MULTI-TIMEFRAME SETUP - {setup_result['symbol']}
=====================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Entry Price: {setup_result['entry_price']}
Stop Loss: {setup_result['stop_loss']}
Target Price: {setup_result['target_price']}
Risk Reward: {setup_result['risk_reward']}
Position Size Factor: {setup_result['position_size_factor']}
Confidence: {setup_result['confidence']} Score: {setup_result['score']}
Timeframe Confirmation: {setup_result['timeframe_confirmation']}
Dominant Trend: {setup_result['dominant_trend']}
Momentum Consistency: {setup_result['momentum_consistency']}
MA Alignment Quality: {setup_result['ma_alignment_quality']}
S/R Confluence Score: {setup_result['sr_confluence_score']}
Volatility Regime: {setup_result['volatility_regime']}
Risk Assessment: {setup_result['risk_assessment']}

Key Filters Passed:
- Multi-Timeframe Trend Confirmation
- Multi-Timeframe Momentum Alignment
- Moving Average Alignment
- Support/Resistance Confluence
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def multi_timeframe_setup(company, multi_timeframe_data_dict=None):
    """
    Function to be called by the trading system
    :param company: 
    :param multi_timeframe_data_dict: 
    :return: 
    """
    setup = MultiTimeframeSetup()
    return setup.check_setup(company, multi_timeframe_data_dict)




