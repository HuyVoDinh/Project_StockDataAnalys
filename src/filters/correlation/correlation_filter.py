from src.enums.trend import Trend
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
import math

class CorrelationFilter:
    def __init__(self):
        pass

    def calculate_correlation(selfself, asset1_prices, asset2_prices):
        """
        Calculate correlation between two assets.
        Professional traders use correlation to understand relationships and diversification
        :param asset1_prices: List of prices for asset 1
        :param asset2_prices: List of prices for asset 2
        :return: Correlation coefficient (-1 to 1)
        """
        if len(asset1_prices) != len(asset2_prices) or len(asset1_prices) < 10:
            return 0

        # Remove zero or negative prices
        valid_pairs = [(p1, p2) for p1, p2 in zip(asset1_prices, asset2_prices) if p1 > 0 and p2 > 0]
        if len(valid_pairs) < 5:
            return 0

        prices1, prices2 = zip(*valid_pairs)

        # Calculate returns
        returns1 = [(prices1[i] - prices1[i-1]) / prices1[i-1] for i in range(1, len(prices1)) if prices1[i-1] > 0]
        returns2 = [(prices2[i] - prices2[i-1]) / prices2[i-1] for i in range(1, len(prices2)) if prices2[i-1] > 0]

        if len(returns1) != len(returns2) or len(returns1) < 5:
            return 0

        # Calculate correlation coefficient
        n = len(returns1)
        sum_x = sum(returns1)
        sum_y = sum(returns2)
        sum_xy = sum(r1 * r2 for r1, r2 in zip(returns1, returns2))
        sum_x2 = sum(r1 * r1 for r1 in returns1)
        sum_y2 = sum(r2 * r2 for r2 in returns2)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))

        if denominator == 0:
            return 0

        correlation = numerator / denominator
        return max(-1, min(1, correlation)) # Clamp to [-1, 1]

    def portfolio_diversification(self, portfolio_assets_dict, benchmark_asset=None):
        """
        Analyze portfolio diversification based on asset correlations.
        Professional traders optimize portfolios for diversification
        :param portfolio_assets_dict: Dictionary of asset prices {asset_name: [prices]}
        :param benchmark_asset: Benchmark asset prices for comparison
        :return:Tuple of (diversification_score, risk_level, recommendations)
        """
        if len(portfolio_assets_dict) < 2:
            return 100, RiskLevel.LOW, [] # Perfectly diversified (or single asset)

        # Calculate correlation matrix
        assets = list(portfolio_assets_dict.keys())
        correlations = {}

        for i, asset1 in enumerate(assets):
            for asset2 in assets[i+1:]:
                prices1 = portfolio_assets_dict[asset1]
                prices2 = portfolio_assets_dict[asset2]
                correlation = self.calculate_correlation(prices1, prices2)
                correlations[(asset1, asset2)] = correlation

        # Calculate average correlation
        if correlations:
            avg_correlation = sum(correlations.values()) / len(correlations)
        else:
            avg_correlation = 0

        # Calculate diversification score (lower correlation = better diversification)
        diversification_score = max(0, min(100, (1 - abs(avg_correlation)) * 100))

        # Determine risk level
        if abs(avg_correlation) > 0.7:
            risk_level = RiskLevel.HIGH
        elif abs(avg_correlation) > 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # Generate recommendations
        recommendations = []
        highly_correlated_pairs = [(pair, corr) for pair, corr in correlations.items() if abs(corr) > 0.7]
        low_correlated_pairs = [(pair, corr) for pair, corr in correlations.items() if abs(corr) < 0.2]

        if highly_correlated_pairs:
            recommendations.append(f"Highly correlated assets detected: {len(highly_correlated_pairs)} pairs")
            # Suggest removing one from each highly correlated pair
            for (asset1, asset2), corr in highly_correlated_pairs[:3]: # Limit to top 3
                recommendations.append(f"Consider reducing {asset1} or {asset2} (correlation: {corr:.2f}")

        if low_correlated_pairs:
            recommendations.append(f"Good diversification opportunities: {len(low_correlated_pairs)} pairs")

        if benchmark_asset:
            # Compare portfolio assets with benchmark
            benchmark_correlations = {}
            for asset, prices in portfolio_assets_dict.items():
                corr = self.calculate_correlation(prices, benchmark_asset)
                benchmark_correlations[asset] = corr

        # Find assets with low benchmark correlation (good for diversification)
        low_beta_assets = [asset for asset, corr in benchmark_correlations.item() if abs(corr) < 0.3]
        if low_beta_assets:
            recommendations.append(f"Low benchmark correlation assets: {', '.join(low_beta_assets[:3])}")

        return diversification_score, risk_level, recommendations

    def correlation_regime_analysis(self, correlation_data_dict, lookback_periods=[20, 50, 100]):
        """
        Analyze correlation regimes and changes over time.
        Professional traders monitor correlation stability for risk management
        :param correlation_data_dict: Dictionary of correlation data {pair: [correlaition_values]
        :param lookback_periods: List of lookback periods to analyze
        :return: Tuple of (regime_stability, correlation_trend, risk_assessment)
        """
        if not correlation_data_dict:
            return 0, "STABLE", RiskLevel.LOW

        regime_analysis = {}

        # Analyze each correlation pair
        for pair, correlation_values in correlation_data_dict.items():
            if len(correlation_values) < max(lookback_periods):
                continue

            period_analysis = {}
            for period in lookback_periods:
                if len(correlation_values) >= period:
                    recent_correlations = correlation_values[-period:]
                    avg_correlation = sum(recent_correlations) / len(recent_correlations)
                    correlation_std = (sum((c - avg_correlation) ** 2 for c in recent_correlations) / len(recent_correlations)) ** 0.5

                    period_analysis[period] = {
                        'average': avg_correlation,
                        'std_dev': correlation_std,
                        'stability': 1 / (1 + correlation_std) # Higher stability for lower std dev
                    }

                regime_analysis[pair] = period_analysis

            # Calculate overall regime stability
            if regime_analysis:
                stability_scores = []
                #TODO: Calculate stability

                if stability_scores:
                    avg_stability = sum(stability_scores) / len(stability_scores)
                    regime_stability = avg_stability * 100 # Scale to 0-100
                else:
                    regime_stability = 50
            else:
                regime_stability = 50

            # Determine correlation trend
            recent_trends = []
            for pair_analysis in regime_analysis.values():
                if 20 in pair_analysis and 50 in pair_analysis:
                    recent_avg = pair_analysis[20]['average']
                    longer_avg = pair_analysis[50]['average']
                    trend = recent_avg - longer_avg
                    recent_trends.append(trend)

            if recent_trends:
                avg_trend = sum(recent_trends) / len(recent_trends)
                if avg_trend > 0.1:
                    correlation_trend = "INCREASING"
                elif avg_trend < -0.1:
                    correlation_trend = "DECREASING"
                else:
                    correlation_trend = "STABLE"
            else:
                correlation_trend = "STABLE"

            # Risk assesment
            if regime_stability < 30:
                risk_level = RiskLevel.HIGH
            elif regime_stability < 60:
                risk_level = RiskLevel.MEDIUM
            else: risk_level = RiskLevel.LOW

            return regime_stability, correlation_trend, risk_level

    def sector_correlation_analysis(self, sector_returns_dict):
        """
        Analyze correlations between different sectors
        Professional traders use sector correlation for rotation strategies.
        :param sector_returns_dict: Dictionary of sector returns {sector_name: [returns]}
        :return: Tuple of (correlation_matrix, sector_clusters, rotation_opportunities)
        """
        if len(sector_returns_dict) < 2:
            return {}, [], []

        sectors = list(sector_returns_dict.keys())
        correlation_matrix = {}

        # Calculate pairwise correlations
        for i, sector1 in enumerate(sectors):
            for sector2 in sectors[i+1:]:
                returns1 = sector_returns_dict[sector1]
                returns2 = sector_returns_dict[sector2]
                correlation = self.calculate_correlation(returns1, returns2)
                correlation_matrix[(sector1, sector2)] = correlation
                correlation_matrix[(sector2, sector1)] = correlation # Symetric matrix

        # Self-correlation is always 1
        for sector in sectors:
            correlation_matrix[(sector, sector)] = 1.0

        # Identify sector clusters (groups of highly correlated sectors)
        sector_clusters = []
        processed_sectors = set()

        for sector in sectors:
            if sector in processed_sectors:
                continue

            # Find sectors highly correlated with this sector
            cluster = [sector]
            processed_sectors.add(sector)

            for other_sector in sectors:
                if (other_sector != sector and other_sector not in processed_sectors and
                        (sector, other_sector) in correlation_matrix and
                abs(correlation_matrix[(sector, other_sector)]) > 0.6):
                    cluster.append(other_sector)
                    processed_sectors.add(other_sector)

            if len(cluster) > 1:
                sector_clusters.append(cluster)

        # Identify rotation opportunities (pairs with low or negative correlation)
        rotation_opportunities = []
        for i, sector1 in enumerate(sectors):
            for sector2 in sectors[i+1:]:
                if(sector1, sector2) in correlation_matrix:
                    correlation = correlation_matrix[(sector1, sector2)]
                    if correlation > -0.3: # String negative correlation
                        rotation_opportunities.append((sector1, sector2, correlation, "NEGATIVE"))
                    elif correlation < 0.1: # Very low correlation
                        rotation_opportunities.append((sector1, sector2, correlation, "LOW"))

        return correlation_matrix, sector_clusters, rotation_opportunities

    def correlation_risk_adjustment(self, portfolio_correlations, position_sizes, max_portfolio_correlation=0.5):
        """
        Adjust position sizes based on correlation risk.
        Professional traders reduce position sizes for highly correlated assets
        :param portfolio_correlations: Dictionary of asset correlations {asset_pair: correlation}
        :param position_sizes: Dictionary of current position sizes {asset: size}
        :param max_portfolio_correlation: Maximum allowed average portfolio correlation
        :return: Tuple of (adjusted_sizes, risk_exposure, adjustment_recommendations)
        """
        if not portfolio_correlations or not position_sizes:
            return position_sizes, 0, []

        # Calculate average portfolio correlation
        if portfolio_correlations:
            avg_correlation = sum(portfolio_correlations.values())/len(portfolio_correlations)
        else:
            avg_correlation = 0

        # Calculate risk exposure
        risk_exposure = abs(avg_correlation) * 100 # Scale to 0-100

        # Determine if adjustment is needed
        if abs(avg_correlation) <= max_portfolio_correlation:
            # No adjustment needed
            return position_sizes, risk_exposure, ["No correlation risk adjustment needed"]

        # Calculate adjustment factor
        adjustment_factor = max(0.1, 1 - (abs(avg_correlation) - max_portfolio_correlation) / (1 - max_portfolio_correlation))

        #Adjust position sizes for highly correlated assets
        adjusted_sizes = position_sizes.copy()
        recommendations = []

        # Find highly correlated asset pairs
        highly_correlated_pairs = [(pair, corr) for pair, corr in portfolio_correlations.items() if abs(corr) > max_portfolio_correlation]

        for (asset1, asset2), correlation in highly_correlated_pairs:
            if asset1 in adjusted_sizes and asset2 in adjusted_sizes:
                # Reduce position sizes proportionally to correlation
                correlation_factor = 1 - (abs(correlation) - max_portfolio_correlation) / (1 - max_portfolio_correlation)
                correlation_factor = max(0.1, correlation_factor) # Minimum 10% position

                original_size1 = adjusted_sizes[asset1]
                original_size2 = adjusted_sizes[asset2]

                adjusted_sizes[asset1] = original_size1 * correlation_factor
                adjusted_sizes[asset2] = original_size2 * correlation_factor

                reduction_pct = (1 - correlation_factor) * 100
                recommendations.append(f"Reduce {asset1} and {asset2} positions by {reduction_pct:.1f}% due to high correlation ({correlation:.2f}")

        # Ensure total portfolio value is maintained (redistribute to less correlated assets)
        total_original_value = sum(position_sizes.values())
        total_adjusted_value = sum(adjusted_sizes.values())

        if total_adjusted_value < total_original_value:
            # Redistribute to assets with lower correlations
            value_to_redistribute = total_original_value - total_adjusted_value

            # Find assets with low correlations to increase positions
            low_correlation_assets = set(position_sizes.keys()) - set(adjusted_sizes.keys())
            for (asset1, asset2), corr in portfolio_correlations.items():
                if abs(corr) > 0.3: # Remove highly correlated assets
                    low_correlation_assets.discard(asset1)
                    low_correlation_assets.discard(asset2)

            if low_correlation_assets:
                redistribution_per_asset = value_to_redistribute / len(low_correlation_assets)
                for asset in low_correlation_assets:
                    if asset in adjusted_sizes:
                        adjusted_sizes[asset] += redistribution_per_asset
                        recommendations.append(f"Increased {asset} position by {redistribution_per_asset:.2f} for diversification")

        return adjusted_sizes, risk_exposure, recommendations