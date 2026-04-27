from src.enums.trend import Trend
from src.enums.signal import Signal

class MomentumRotationFilter:
    def __init__(self):
        pass

    def calculate_relative_momentum(self, stock_data_list, benchmark_data_list, periods=20):
        """
        Calculate relative momentum of stocks vs benchmark
        Professional traders use this to identify outperforming assets
        :param stock_data_list: List of stock data
        :param benchmark_data_list: List of benchmark data
        :param periods: Number of periods to analyze
        :return: Tuple of (relative_momentum, outperformance, momentum_rank)
        """
        if len(stock_data_list) < periods or len(benchmark_data_list) < periods:
            return Trend.Sideway, 0, 0

        # Calculate stock returns
        stock_prices = [data.price.close_price for data in stock_data_list[-periods:]]
        if len(stock_prices) >= 2 and stock_prices[0] > 0:
            stock_return = (stock_prices[-1] - stock_prices[0]) / stock_prices[0]
        else:
            stock_prices = 0

        # Calculate benchmark returns
        benchmark_prices = [data.price.close_price for data in benchmark_data_list[-periods:]]
        if len(benchmark_prices) >= 2 and benchmark_prices[0] > 0:
            benchmark_return = (benchmark_prices[-1] - benchmark_prices[0]) / benchmark_prices[0]
        else:
            benchmark_return = 0

        # Calculate relative momentum (outperformance)
        relative_momentum = stock_return - benchmark_return

        # Classify momentum
        if relative_momentum > 0.05: # Outperforming by 5%
            momentum_trend = Trend.Strong_Up
        elif relative_momentum > 0.02: # Outperforming by 2%
            momentum_trend = Trend.Up
        elif relative_momentum < -0.05: # Underperforming by 5%
            momentum_trend = Trend.Strong_Down
        elif relative_momentum < -0.02: # Underperforming by 2%
            momentum_trend = Trend.Down
        else:
            momentum_trend = Trend.Sideway

        # Calculate momentum rank (0 - 100)
        momentum_rank = min(100, max(0, 50 + (relative_momentum * 1000)))
        return momentum_trend, relative_momentum, momentum_rank

    def momentum_acceleration(self, price_data_list, periods=10):
        """
        Calculate momentum acceleration to identify stocks with increasing momentum
        Professional traders look for accelerating momentum as a strong signal
        :param price_data_list: List of price data
        :param periods: Number of periods to analyze
        :return: Tuple of (acceleration, acceleration_trend, quality)
        """
        if len(price_data_list) < periods * 2:
            return 0, Trend.Sideway, 0

        # Calculate returns for first half
        first_half = price_data_list[-periods*2:-periods]
        first_prices = [data.price.close_price for data in first_half]
        if len(first_prices) >= 2 and first_prices[0] > 0:
            first_return = (first_prices[-1] - first_prices[0]) / first_prices[0]
        else:
            first_return = 0

        # Calculate returns for second half
        second_half = price_data_list[-periods:]
        second_prices = [data.price.close_price for data in second_half]
        if len(second_prices) >= 2 and second_prices[0] > 0:
            second_return = (second_prices[-1] - second_prices[0]) / second_prices[0]
        else:
            second_return = 0

        # Calculate acceleration
        acceleration = second_return - first_return

        # Classify acceleration
        if acceleration > 0.03: # Accelerating by 3%
            acceleration_trend = Trend.Strong_Up
        elif acceleration > 0.01: # Accelerating by 1%
            acceleration_trend = Trend.Up
        elif acceleration < -0.03: # Decelerating by 3%
            acceleration_trend = Trend.Strong_Down
        elif acceleration < -0.01: # Decelerating by 3%
            acceleration_trend = Trend.Down
        else:
            acceleration_trend = Trend.Sideway

        # Quality score based on consistency
        quality = min(100, abs(acceleration) * 1000)
        return acceleration, acceleration_trend, quality

    def momentum_divergence(self, price_data_list, volume_data_list, periods=15):
        """
        Identify momentum divergence between price and volume
        Professional traders use this to spot potential reversals
        :param price_data_list: List of price data
        :param volume_data_list: List of volume data
        :param periods: Number of periods to analyze
        :return: Tuple of (divergence_type, strength, signal)
        """
        if len(price_data_list) < periods or len(volume_data_list) < periods:
            return "NONE", 0, Signal.HOLD

        # Calculate price momentum
        price_prices = [data.price.close_price for data in price_data_list[-periods:]]
        if len(price_prices) >= 2 and price_prices[0] > 0:
            price_momentum = (price_prices[-1] - price_prices[0]) / price_prices[0]
        else:
            price_momentum = 0

        # Calculate volume momentum
        volume_values = [data.volume for data in volume_data_list[-periods:] if data.volume is not None]
        if len(volume_values) >= 2 and volume_values[0] > 0:
            volume_momentum = (volume_values[-1] - volume_values[0]) / volume_values[0]
        else:
            volume_momentum = 0

        # Identify divergence
        if price_momentum > 0.02 and volume_momentum < -0.05:
            # Bullish divergence: price making higher highs, volume making lower lows
            divergence_type = "BULLISH"
            strength = min(100, (price_momentum - volume_momentum) * 100)
            signal = Signal.BUY
        elif price_momentum < -0.02 and volume_momentum > 0.05:
            # Bearish divergence: price making lower lows, volume making higher highs
            divergence_type = "BEARISH"
            strength = min(100, (volume_momentum - price_momentum) * 100)
            signal = Signal.BUY
        else:
            divergence_type = "NONE"
            strength = 0
            signal = Signal.HOLD

        return divergence_type, strength, signal

    def momentum_sustainability(self, momentum_data_list, periods=25):
        """
        Analyze momentum sustainability to identify durable trends
        Professional traders prefer sustainable momentum over short bursts
        :param momentum_data_list: List of momentum data
        :param periods:Number of periods to analyze
        :return: Tuple of (sustainability, trend_quality, duration)
        """
        if len(momentum_data_list) < periods:
            return 0, 0, 0

        # Calculate consistency of momentum direction
        positive_periods = 0
        negative_periods = 0
        total_momentum = 0

        for i in range(1, len(momentum_data_list[-periods:])):
            current = momentum_data_list[i]
            previous = momentum_data_list[i-1]

            if hasattr(current, 'price') and hasattr(previous, 'price'):
                if current.price.close_price > previous.price.close_price:
                    positive_periods += 1
                elif current.price.close_price < previous.price.close_price:
                    negative_periods += 1
                total_momentum += (current.price.close_price - previous.price.close_price) / previous.price.close_price


        # Calculate sustainability ratio
        total_periods = positive_periods + negative_periods
        if total_periods > 0:
            if total_momentum > 0:
                sustainability = positive_periods / total_periods
            else:
                sustainability = negative_periods / total_periods
        else:
            sustainability = 0

        # Trend quality based on consistency
        trend_quality = min(100, sustainability * 100)

        # Duration of consistent momentum
        if total_momentum > 0:
            duration = positive_periods
        else:
            duration = negative_periods

        return sustainability, trend_quality, duration

    def cross_asset_momentum(self, asset_returns_dict, current_asset, lookback_period=30):
        """
        Compare momentum across different assets to identify relative strength
        Professional traders use cross-asset analysis for better stock selection
        :param asset_returns_dict: Dictionary of asset returns {asset_name: [returns]}
        :param current_asset: Current asset name
        :param lookback_period: Lookback period for comparison
        :return: Tuple of (relative_rank, percentile, outperformance)
        """
        if current_asset not in asset_returns_dict:
            return 0, 0, 0

        current_returns = asset_returns_dict[current_asset][-lookback_period:]
        if len(current_returns) == 0:
            return 0, 0, 0

        current_performance = sum(current_returns) / len(current_returns) if current_returns else 0

        # Compare with other assets
        performances = []
        for asset, returns in asset_returns_dict.items():
            if len(returns) >= lookback_period:
                perf = sum(returns[-lookback_period:]) / lookback_period
                performances.append((asset,perf))

        # Sort by performance
        performances.sort(key=lambda x: x[1], reverse=True)

        # Find current asset rank
        current_rank = 0
        for i, (asset, perf) in enumerate(performances):
            if asset == current_asset:
                current_rank = i + 1
                break

        # Calculate percentile
        total_assets = len(performances)
        if total_assets > 0:
            percentile = (total_assets - current_rank + 1) / total_assets * 100
        else:
            percentile = 0

        # Calculate average outperformance
        if performances:
            avg_performance = sum([perf for _, perf in performances]) / len(performances)
            outperformance = current_performance - avg_performance
        else:
            outperformance = 0

        return current_rank, percentile, outperformance