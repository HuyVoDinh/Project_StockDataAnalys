from src.filters.pattern.chart_pattern_filter import ChartPatternFilter
from src.filters.pattern.harmonic_pattern_filter import HarmonicPatternFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData
import numpy as np

class MLPatternRecognitionSetup:
    def __init__(self):
        self.chart_filter = ChartPatternFilter()
        self.harmonic_filter = HarmonicPatternFilter()
        self.risk_filter = RiskFilter()
        self.volatility_filter = AdvancedVolatilityFilter()

        # Pattern recognition weights (would be trained in practice)
        self.pattern_weight = {
            'head_and_shoulders': 0.15,
            'double_top_bottom': 0.12,
            'triangle': 0.10,
            'flag': 0.08,
            'gartley': 0.1,
            'butterfly': 0.09,
            'bat': 0.08,
            'crab': 0.07,
            'technical_confirmation': 0.21,
        }

    def check_setup(self, company: CompanyData):
        """
        Professional Machine Learning Pattern Recognition Setup
        This setup uses ensemble pattern recognition with machine learning techniques

        Key component:
        1. Multi-pattern recognition with confidence scoring
        2. Pattern confluence and clustering analysis
        3. Machine learning-based pattern validation
        4. Adaptive pattern recognition weights
        5. Ensemble signal generation
        :param company:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 25:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]
        current_price = current_data.price.close_price

        # 1. Classical chart pattern recognition
        chart_patterns = self.chart_filter.pattern_analysis(company_data_list, periods=35)

        # 2. Harmonic pattern recognition
        harmonic_patterns = self.harmonic_filter.find_harmonic_patterns(chart_patterns, periods=50)

        # 3. Pattern confluence analysis
        confluence_score, confluence_details = self._analyze_pattern_confluence(chart_patterns, harmonic_patterns, company_data_list)

        # 4. Pattern clustering analysis
        cluster_score, cluster_details = self._analyze_pattern_clustering(chart_patterns, harmonic_patterns, company_data_list)

        # 5. Technical indicator confirmation
        technical_confirmation, tech_score = self._technical_pattern_confirmation(company_data_list, chart_patterns, harmonic_patterns)

        # 6. Pattern quality assesment
        pattern_quality_score = self._assess_pattern_quality(chart_patterns, harmonic_patterns)

        # 7. Machine learning ensemble signal
        ml_signal, ml_confidence, ml_details = self._ml_ensemble_pattern_recongnition(chart_patterns, harmonic_patterns,
                                                                                      technical_confirmation, confluence_score,
                                                                                      cluster_score, pattern_quality_score)

        # 8. Adaptive pattern weights (simplified learning)
        self._update_pattern_weigts(confluence_details, cluster_details, tech_score, ml_details)

        # 9. Risk-adjusted entry signal
        signal = Signal.HOLD
        direction = "NEUTRAL"

        # Combine all pattern signals
        buy_signals = 0
        sell_signal = 0

        # Chart pattern signals
        for pattern_name, pattern_data in chart_patterns.items():
            if pattern_data.get('signal') == Signal.BUY:
                buy_signals += 1
            elif pattern_data.get('signal') == Signal.SELL:
                sell_signal += 1

        # Harmonic pattern signals
        for pattern_name, pattern_data in harmonic_patterns.items():
            if pattern_data.get('signal') == Signal.BUY:
                buy_signals += 1
            elif pattern_data.get('signal') == Signal.SELL:
                sell_signal += 1

        # ML ensemble signal
        if ml_signal == Signal.BUY:
            buy_signals += 2 # Weight ML signal more heavily
        elif ml_signal == Signal.SELL:
            sell_signal += 2

        # Technical confirmation
        if technical_confirmation == Signal.BUY:
            buy_signals += 1
        elif technical_confirmation == Signal.SELL:
            sell_signal += 1

        # Generate final signal
        signal_threshold = 3 # Need at least 3 confirming signals

        if buy_signals >= signal_threshold and buy_signals > sell_signal and ml_confidence > 0.6:
            signal = Signal.BUY
            direction = "LONG"
        elif sell_signal >= signal_threshold and sell_signal > buy_signals and ml_confidence > 0.6:
            signal = Signal.SELL
            direction = "SHORT"
        else:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 10. Risk management based on pattern analysis
        # Position sizing based on pattern quality and ML confidence
        pattern_strength = max(buy_signals, sell_signal)
        quality_factor = (confluence_score * 0.4 + cluster_score * 0.3 + pattern_quality_score * 0.3) / 100
        confidence_factor = ml_confidence

        position_sizing_factor = min(1.0, (pattern_strength / 6) * quality_factor * confidence_factor)

        # Adjust for volatility regime
        volatility_regime, volatility_trend, volatility_risk = self.volatility_filter.volatility_regime_analysis(company_data_list, periods=20)

        if volatility_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            position_sizing_factor *= 0.7 # Reduce size in high volatility
        elif volatility_risk == RiskLevel.LOW:
            position_sizing_factor *= 1.2 # Increase size in low volatility

        # Stop loss based on pattern targets and support/resistance
        stop_loss_distance = self._calculate_pattern_stop_loss(chart_patterns, harmonic_patterns, current_price, current_data)

        if signal == Signal.BUY:
            stop_loss = current_price - stop_loss_distance
        elif signal == Signal.SELL:
            stop_loss = current_price + stop_loss_distance
        else:
            stop_loss = 0

        # Target based on pattern projections
        target_price = self._calculate_pattern_target(chart_patterns, harmonic_patterns, current_price, signal)

        # 11. Risk/Reward calculation
        if signal != Signal.HOLD and stop_loss_distance > 0:
            rr_ratio = abs(target_price - current_price) / stop_loss_distance
        else:
            rr_ratio = 0

        # Need minimum 2:1 risk?reward for pattern strategies
        if rr_ratio < 2.0 and signal != Signal.HOLD:
            signal = Signal.HOLD
            direction = "NEUTRAL"

        # 12. Setup scoring
        # Weight factors: pattern confluence (25%), clustering (20%), quality (15%)
        # ML confidence (20%), risk/reward (10%), technical confirmation (10%)
        score = (
            confluence_score * 0.25 +
            cluster_score * 0.20 +
            pattern_quality_score * 0.15 +
            ml_confidence * 100 * 0.20 + # Scale to 0-100
            min(100, rr_ratio * 20) * 0.10 + # Scale RR to 0-100
            tech_score * 0.10
        )

        return {
            'symbol': company.symbol,
            'setup_type': 'ML_PATTERN_RECOGNITION',
            'direction': direction,
            'signal': signal,
            'current_price': current_price,
            'position_size_factor': position_sizing_factor,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
            'pattern_analysis': {
                'chart_patterns_count': len(chart_patterns),
                'harmonic_patterns_count': len(harmonic_patterns),
                'confluence_score': confluence_score,
                'cluster_score': cluster_score,
                'pattern_quality_score': pattern_quality_score,
                'ml_confidence': ml_confidence,
                'technical_confirmation': technical_confirmation.name if hasattr(technical_confirmation, 'name') else str(technical_confirmation),
            },
            'pattern_details': {
                'chart_patterns': list(chart_patterns.keys()) if chart_patterns else [],
                'harmonic_patterns': list(harmonic_patterns.keys()) if harmonic_patterns else [],
                'confluence_details': confluence_details,
                'cluster_details': cluster_details,
                'ml_details': ml_details,
            },
            'signal_components': {
                'buy_signals': buy_signals,
                'sell_signal': sell_signal,
                'pattern_strength': pattern_strength,
            }
        }

    def _analysze_pattern_confluence(self, chart_patterns, harmonic_patterns, company_data_list):
        """
        Analyze confluence between different pattern types
        :param chart_patterns:
        :param harmonic_patterns:
        :param company_data_list:
        :return:
        """
        if not chart_patterns and not harmonic_patterns:
            return 0, {}

        # Count patterns
        total_patterns = len(chart_patterns) + len(harmonic_patterns)

        # Check for directional agreement
        chart_signals = [pattern.get('signal') for pattern in chart_patterns.values() if pattern.get('signal')]
        harmonic_signals = [pattern.get('signal') for pattern in harmonic_patterns.values() if pattern.get('signal')]

        all_signals = chart_signals + harmonic_signals
        buy_signals = all_signals.count(Signal.BUY)
        sell_signals = all_signals.count(Signal.SELL)

        # Calculate agreement ratio
        if len(all_signals) > 0:
            agreement = max(buy_signals, sell_signals) / len(all_signals)
        else:
            agreement = 0.5

        # Calculate average confidence
        chart_confidences = [pattern.get('confidence', 50) for pattern in chart_patterns.values()]
        harmonic_confidences = [pattern.get('confidence', 50) for pattern in harmonic_patterns.values()]

        all_confidences = chart_confidences + harmonic_confidences
        if all_confidences:
            avg_confidence = sum(all_confidences) / len(all_confidences)
        else:
            avg_confidence = 50

        # Confluence score (0-100)
        confluence_score = min(100,
                               (total_patterns * 10) * 0.4 + # Pattern count component
                               (agreement * 100) * 0.4 + # Agreement component
                               (avg_confidence / 100 * 100) * 0.2 # Confidence component
        )

        details = {
            'total_patterns': total_patterns,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'agreement': agreement,
            'avg_confidence': avg_confidence,
        }

        return confluence_score, details

    def _analyze_pattern_clustering(self, chart_patterns, harmonic_patterns, current_price):
        """
        Analyze clustering of pattern targets and support/resistance levels
        :param chart_patterns:
        :param harmonic_patterns:
        :param current_price:
        :return:
        """
        # Extract target prices
        target_prices = []

        # Chart pattern targets
        for pattern in chart_patterns.values():
            if 'target_price' in pattern and pattern['target_price'] > 0:
                target_prices.append(pattern['target_price'])

        # Harmonic pattern targets
        for pattern in harmonic_patterns.values():
            if 'target_price' in pattern and pattern['target_price'] > 0:
                target_prices.append(pattern['target_price'])

        if len(target_prices) < 2:
            return 30, {'cluster_count': 0, 'price_range': 0, 'concentration': 0} # Low score for insufficient data

        # Calculate price range
        price_range = max(target_prices) - min(target_prices)
        if price_range == 0:
            return 50, {'cluster_count': 1, 'price_range': 0, 'concentration': 1}

        # Identify clusters (prices within 2% of each other)
        clusters = []
        used_prices = set()

        for i, price1 in enumerate(target_prices):
            if i in used_prices:
                continue

            cluster = [price1]
            for j, price2 in enumerate(target_prices):
                if j in used_prices or i == j:
                    continue

                # Check if prices are within 2% of each other
                if abs(price1 - price2) / ((price1 + price2) / 2) < 0.02:
                    clusters.append(price2)
                    used_prices.add(j)

            cluster.append(cluster)
            used_prices.add(i)

        # Calculate clustering metrics
        cluster_count = len(clusters)
        max_cluster_size = max(len(cluster) for cluster in clusters) if clusters else 0

        # Concentration measure (largest cluster vs total patterns)
        concentration = max_cluster_size / len(target_prices) if target_prices else 0

        # Cluster score (0-100)
        cluster_score = min(100,
                            (cluster_count * 15) * 0.3 + # Number of clusters
                            (max_cluster_size * 10) * 0.4 + #Largest cluster size
                            (concentration * 100) * 0.3 # Concentration
                            )

        details = {
            'cluster_count': cluster_count,
            'max_cluster_size': max_cluster_size,
            'price_range': price_range,
            'concentration': concentration,
        }

        return cluster_score, details

    def _technical_pattern_confirmation(self, company_data_list, chart_patterns, harmonic_patterns):
        """
        Use technical indicators to confirm pattern validity
        :param company_data_list:
        :param chart_patterns:
        :param harmonic_patterns:
        :return:
        """
        if len(company_data_list) < 14:
            return Signal.HOLD, 50

        current_data = company_data_list[-1]

        # RSI confirmation
        rsi_confirmation = 0
        if hasattr(current_data, 'RSI_14') and current_data.RSI_14 is not None:
            if current_data.RSI_14 < 30: # Over sold
                rsi_confirmation = 1
            elif current_data.RSI_14 > 70: # Overbought
                rsi_confirmation = -1

        # MACD confirmation
        macd_confirmation = 0
        if (hasattr(current_data, 'MACD') and current_data.MACD is not None and
        hasattr(current_data.MACD, 'MACD') and hasattr(current_data.MACD, 'signal')):
            macd_hist = current_data.MACD.MACD - current_data.MACD.signal
            if macd_hist > 0:
                macd_confirmation = 1
            elif macd_hist < 0:
                macd_confirmation = -1

        # Volume confirmation
        volume_confirmation = 0
        if len(company_data_list) >= 20:
            recent_volumes = [data.volume for data in company_data_list[-10:] if data.volume is not None]
            earlier_volumes = [data.volume for data in company_data_list[-20:-10] if data.volume is not None]

            if recent_volumes and earlier_volumes:
                avg_recent = sum(recent_volumes) / len(recent_volumes)
                avg_earlier = sum(earlier_volumes) / len(earlier_volumes)

                if avg_recent > avg_earlier * 1.2: # 20% volume increase
                    volume_confirmation = 1
                elif avg_recent < avg_earlier * 0.8: # 20% volume descrease
                    volume_confirmation = -1

        # Combine technical signals
        tech_score = rsi_confirmation + macd_confirmation + volume_confirmation

        if tech_score >= 2:
            signal = Signal.BUY
        elif tech_score <= -2:
            signal = Signal.SELL
        else:
            signal = Signal.HOLD

        # Technical confirmation score (0-100)
        confirmation_score = min(100, max(0, 50 + tech_score * 15)) # Scale -3 to 3 to 0-100

        return signal, confirmation_score

    def _assess_pattern_quality(self, chart_patterns, harmonic_patterns):
        """
        Assess overal quality of detected patterns
        :param chart_patterns:
        :param harmonic_patterns:
        :return:
        """
        all_patterns = list(chart_patterns.values()) + list(harmonic_patterns.values())

        if not all_patterns:
            return 30 # Low quality score for no patterns

        # Calculate average confidence
        confidences = [pattern.get('confidence', 50) for pattern in all_patterns]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 50

        # Calculate pattern diversity (more diverse = better)
        pattern_types = set()
        for pattern in chart_patterns.keys():
            pattern_types.add('chart_' + pattern.split('_')[0] if '_' in pattern else 'chart_' + pattern)
        for pattern in harmonic_patterns.keys():
            pattern_types.add('harmonic_' + pattern.split('_')[0] if '_' in pattern else 'harmonic_' + pattern)

        diversity_score = min(100, len(pattern_types) * 20) # Up to 5 difference types

        # Quality score (0-100)
        quality_score = (avg_confidence * 0.7) + (diversity_score * 0.3)
        return quality_score

    def _ml_ensemble_pattern_recognition(self, chart_patterns, harmonic_patterns,
                                         technical_confirmation, confluence_score,
                                         cluster_score, pattern_quality_score):
        """
        Machine learning ensemble for pattern recognition (simplified)
        :param chart_patterns:
        :param harmonic_patterns:
        :param technical_confirmation:
        :param confirmation_score:
        :param cluster_score:
        :param pattern_quality_score:
        :return:
        """
        # Feature vector for ML model
        features = [
            len(chart_patterns),            # Chart pattern count
            len(harmonic_patterns),         # Harmonic pattern count
            confluence_score / 100,          # Normalized confluence
            cluster_score / 100,            # Normalized clustering
            pattern_quality_score / 100,    # Normalized quality
            1 if technical_confirmation == Signal.BUY else 0, # Tech buy signal
            1 if technical_confirmation == Signal.SELL else 0, # Tech sell signal
        ]

        # Simplified ML model (in practice, this would be a trained model)
        # Weighted sum approach
        weights = [0.15, 0.15, 0.2, 0.2, 0.2, 0.05, 0.05] # Feature weights

        # Calculate weighted score
        weighted_sum = sum(f * w for f, w in zip(features, weights))

        # Apply activation function (sigmod-like)
        ml_confidence = 1 / (1 + np.exp(-5 * (weighted_sum - 0.5))) # Scaled sigmoid

        # Generate signal based on confidence
        if ml_confidence > 0.6:
            signal = Signal.BUY
        elif ml_confidence < 0.4:
            signal = Signal.SELL
        else:
            signal = Signal.HOLD

        details = {
            'features': features,
            'weights': weights,
            'weighted_sum': weighted_sum,
        }

        return signal, ml_confidence, details

    def _update_pattern_weights(self, confluence_details, cluster_details, tech_score, ml_details):
        """
        Adaptive weight updating based on pattern performance (simplified)
        :param confluence_details:
        :param cluster_details:
        :param tech_score:
        :param ml_details:
        :return:
        """
        # In practice, this would use actual trade results to update weights
        # For now, just show how it would work
        # Example: If confluence is high but actual performance is low, reduce confluence weight
        # This is a placeholder for actual ML weight updating

        pass # Weight updating would happen here in a real implementation

    def _calculate_pattern_stop_loss(self, chart_patterns, harmonic_patterns, current_data, current_price):
        """
        Calculate stop loss based on pattern support/resistance levels
        :param chart_patterns:
        :param harmonic_patterns:
        :param current_data:
        :param current_price:
        :return:
        """
        # Extract stop loss levels from patterns
        stop_levels = []

        # Chart pattern stop losses
        for pattern in chart_patterns.values():
            if 'stop_loss' in pattern and pattern['stop_loss'] > 0:
                stop_levels.append(pattern['stop_loss'])

        # Harmonic pattern stop losses
        for pattern in harmonic_patterns.values():
            if 'stop_loss' in pattern and pattern['stop_loss'] > 0:
                stop_levels.append(pattern['stop_loss'])

        # Calculate average stop level
        if stop_levels:
            avg_stop = sum(stop_levels) / len(stop_levels)
            stop_distance = abs(current_price - avg_stop)
        else:
            stop_distance = 0

        # Fallback to ATR-based stop if no pattern stops
        if stop_distance == 0 and hasattr(current_data, ' ATR_14') and current_data.ATR_14 is not None:
            stop_distance = current_data.ATR_14 * 2 # 2x ATR stop
        elif stop_distance == 0:
            stop_distance = current_price * 0.02 # 2% default stop

        return max(stop_distance, current_price * 0.01) # Minimum 1% stop

    def _calculate_pattern_target(self, chart_patterns, harmonic_patterns, current_price, signal):
        """
        Calculate target price based on pattern projections
        :param chart_patterns:
        :param harmonic_patterns:
        :param current_price:
        :param signal:
        :return:
        """
        # Extract target prices form patterns
        targets = []

        # Chart pattern targets
        for pattern in chart_patterns.values():
            if 'target_price' in pattern and pattern['target_price'] > 0:
                targets.append(pattern['target_price'])

        # Harmonic pattern targets
        for pattern in harmonic_patterns.values():
            if 'target_price' in pattern and pattern['target_price'] > 0:
                targets.append(pattern['target_price'])

        # Calculate average target
        if targets:
            avg_target = sum(targets) / len(targets)
        else:
            # Fallback to fixed risk/reward ratio
            stop_distance = current_price * 0.02 # 2% stop
            if signal == Signal.BUY:
                avg_target = current_price + (stop_distance * 3) # 3:1 RR
            elif signal == Signal.SELL:
                avg_target = current_price - (stop_distance * 3)
            else:
                avg_target = current_price

        return avg_target

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        pattern_analysis = setup_result['pattern_analysis']
        pattern_details = setup_result['pattern_details']
        components = pattern_analysis['signal_components']

        details = f"""
ML PATTERN RECOGNITION SETUP - {setup_result['symbol']}
======================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Signal: {setup_result['signal']}
Current Price: {setup_result['current_price']}
Position Size factor: {setup_result['position_size_factor']}
Stop Loss: {setup_result['stop_loss']}
Target: {setup_result['target']}
RisK/Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})

Pattern Analysis:
- Chart Patterns Count: {pattern_analysis['chart_patterns_count']}
- HarmonicPatterns Count: {pattern_analysis['harmonic_patterns_count']}
- Confluence Score: {pattern_analysis['confluence_score']}
- Cluster Score: {pattern_analysis['cluster_score']}
- Pattern Quality Score: {pattern_analysis['pattern_quality_score']}
- ML Confidence: {pattern_analysis['ml_confidence']}
- Technical Confirmation: {pattern_analysis['technical_confirmation']}

Pattern Details:
- Chart Patterns: {', '.join(pattern_details['chart_patterns'][:5]) if pattern_details['chart_patterns'] else 'None'}
- Harmonic Patterns: {' '.join(pattern_details['harmonic_patterns']) if pattern_details['harmonic_patterns'] else 'None'}

Signal Components:
- Buy Signals: {components['buy_signals']}
- Sell Signals: {components['sell_signals']}
- Pattern Strength: {components['pattern_strength']}

Key Filters Passed:
- Multi-Pattern Recognition
- Pattern Confluence Analysis
- Pattern Clustering Analysis
- Techinical Confirmation
- ML Ensemble Recognition
- Adaptive Weight Updating
- Risk Management:
"""
        return details.strip()

# Helper function to use the setup
def ml_pattern_recognition_setup(company_data):
    """
    Function to be called by the trading system
    :param company_data:
    :return:
    """
    setup = MLPatternRecognitionSetup()
    return setup.check_setup(company_data)