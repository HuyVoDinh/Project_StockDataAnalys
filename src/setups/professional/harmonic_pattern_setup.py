from src.filters.pattern.harmonic_pattern_filter import HarmonicPatternFilter
from src.filters.pattern.chart_pattern_filter import ChartPatternFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class HarmonicPatternSetup(HarmonicPatternFilter):
    def __next__(self):
        self.harmonic_filter = HarmonicPatternFilter()
        self.chart_filter = ChartPatternFilter()
        self.risk_filter = RiskFilter()
        self.volatility_filter = AdvancedVolatilityFilter()

    def check_setup(self, company: CompanyData):
        """
        Professional Harmonic Pattern setup
        This setup identifies high-probability harmonic pattern setups

        Key components:
        1. Harmonic pattern detection
        2. Pattern convergene analysis
        3. Confluence with chart patterns
        4. Risk management
        :param company:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 50:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # 1 Find harmonic patterns
        harmonic_patterns = self.harmonic_filter.find_harmonic_patterns(company_data_list, periods=50)

        # Need at least one harmonic pattern
        if not harmonic_patterns:
            return None
        # 2. Analyze harmonic convergence
        convergence_score, best_setup, risk_level = self.harmonic_filter.harmonic_convergence_analysis(company_data_list, periods=50)

        # Need significant convergence
        if convergence_score < 60:
            return None

        # 3. Check for confluence with chart patterns
        chart_patterns = self.chart_filter.pattern_analysis(company_data_list, periods=30)

        # Confluence score based on agreement between harmonic and char patterns
        confluence_score = self._calculate_pattern_confluence(harmonic_patterns, chart_patterns, best_setup)

        # 4. Volatility analysis for pattern completion
        volatility_regime, volatility_trend, volatility_risk = self.volatility_filter.volatility_regime_analysis(company_data_list, periods=20)

        # in high volatility, harmonic patterns may fail more often
        if volatility_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            # Need higher confluence score in high volatility
            if confluence_score < 70:
                return None

        # 5. Risk management
        # Get the primary harmonic pattern for setup details
        primary_pattern = best_setup.get('primary_pattern') if best_setup else None
        if not primary_pattern:
            # Fallback to highest confidence pattern
            primary_pattern = self._get_highest_confidence_pattern(harmonic_patterns)

        if not primary_pattern:
            return None

        # Extract pattern detials
        entry_price = current_price
        target_price = primary_pattern.get('target_price', current_price * 1.05)
        stop_loss = primary_pattern.get('stop_loss', current_price * 0.97)

        # Adjust stop loss based on volatility
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            # Use ATR for stop loss if available
            atr_stop = current_price - (2 * current_data.ATR_14) if best_setup['signal'] == Signal.BUY else current_price + (2 * current_data.ATR_14)
            # Use the more conservative (wider) stop
            if best_setup['signal'] == Signal.BUY:
                stop_loss = max(stop_loss, atr_stop)
            else:
                stop_loss = min(stop_loss, atr_stop)

        # 6. Risk/Reward caclculation
        rr_ratio = abs(target_price - entry_price) / abs(entry_price - stop_loss) if abs(entry_price - stop_loss) > 0 else 0

        # Need minimum 2:1 risk/reward for harmonic patterns
        if rr_ratio < 2.0:
            return None

        # 7. Position sizing based on pattern quality
        # Higher confidence patterns get larget position sizes
        avg_confidence = best_setup.get('avg_confidence', 50)
        position_sizing_factor = min(1.0, avg_confidence / 100) # Scale 0-100 to 0-1.0

        # Adjust for volatility
        if volatility_risk == RiskLevel.HIGH:
            position_sizing_factor *= 0.7
        elif volatility_risk == RiskLevel.VERY_HIGH:
            position_sizing_factor *= 0.5

        # 8. Setup scoring
        # Weight factors: convergence (30%), confluence(25%), confidence(20%)
        # Risk/reward(15%), volatility adjustment (10%)
        score = (
            convergence_score * 0.3 +
            confluence_score * 0.25 +
            avg_confidence * 0.2 +
            min(100, rr_ratio * 15) + 0.15 + # Scale RR ratio to 0-100
            (100 - volatility_risk.value * 25) * 0.1 # Map RiskLevel to 0-100
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'HARMONIC_PATTERN',
            'direction': best_setup['setup_type'],
            'signal': best_setup['signal'],
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_reward': rr_ratio,
            'position_sizing_factor': position_sizing_factor,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
            'convergence_score': convergence_score,
            'confluence_score': confluence_score,
            'pattern_count': best_setup.get('pattern_count', 0),
            'avg_confidence': avg_confidence,
            'volatility_risk': volatility_risk.name if hasattr(volatility_risk, 'name') else str(volatility_risk),
            'primary_pattern': {
                'type': primary_pattern.get('type', 'UNKNOWN'),
                'confidence': primary_pattern.get('confidence', 0),
            }
        }

    def _calculate_pattern_confluence(self, harmonic_patterns, chart_patterns, best_setup):
        """
        Calculate confluence score between harmonic and chart patterns
        :param harmonic_patterns:
        :param chart_patterns:
        :param best_setup:
        :return:
        """

        if not harmonic_patterns and not chart_patterns:
            return 0

        # Base confluence on number of patterns found
        harmonic_count = len(harmonic_patterns)
        chart_count = len(chart_patterns)

        # Check for directional agreement
        harmonic_signals = [pattern['signal'] for pattern in harmonic_patterns.values()]
        chart_signals = [pattern['signal'] for pattern in chart_patterns.values()]

        # Count agreement
        agreement_count = 0
        total_signals = len(harmonic_patterns) + len(chart_patterns)

        if total_signals > 0:
            if best_setup['signal'] == Signal.BUY:
                agreement_count = (harmonic_signals.count(Signal.BUY) + chart_signals.count(Signal.BUY))
            elif best_setup['signal'] == Signal.SELL:
                agreement_count = (harmonic_signals.count(Signal.SELL)) + chart_signals.count(Signal.SELL)

            agreement_ratio = agreement_count / total_signals
        else:
            agreement_ratio = 0.5 #Neutral

        # Confluence score (0-100)
        confluence_score = min(100,
                               (harmonic_count * 10 + chart_count * 5) * 0.5 + # Pattern count component
                               agreement_ratio * 50 # Agreement component
        )
        return confluence_score

    def _get_highest_confidence_pattern(self, harmonic_patterns):
        """
        Get the harmonic pattern with the highest confidence
        :param harmonic_patterns:
        :return:
        """
        if not harmonic_patterns:
            return None

        best_pattern = None
        highest_confidence = 0

        for pattern in harmonic_patterns.values():
            confidence = pattern.get('confidence', 0)
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_pattern = pattern

        return best_pattern

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        details = f"""
HARMONIC PATTERN SETUP - {setup_result['symbol']}
===============================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Entry Price: {setup_result['entry_price']:.2f}
Stop Loss: {setup_result['stop_loss']:.2f}
Target Price: {setup_result['target_price']:.2f}
Risk Reward: {setup_result['risk_reward']:.2f}
Position Size Factor: {setup_result['position_sizing_factor']:.2f}
Confidence: {setup_result['avg_confidence']:.2f}
Convergence Score: {setup_result['confluence_score']:.2f}
Confluence Score: {setup_result['confluence_score']:.2f}
Pattern Count: {setup_result['pattern_count']}
Average Confidence: {setup_result['avg_confidence']:.2f}
Volatility Risk: {setup_result['volatility_risk']}
Primary Pattern: {setup_result['primary_pattern']['type']} (Confidence: {setup_result['primary_pattern']['confidence']:})

Key Filters Passed:
- Harmonic Pattern Detection
- Pattern Convergence Analysis
- Char Pattern Confluence
Risk Management:
"""
        return details.strip()

# Helper function to use the setup
def harmonic_pattern_setup(company_data):
    """
    Function to be called by the trading system
    :return:
    """
    setup = HarmonicPatternSetup()
    return setup.check_setup(company_data)