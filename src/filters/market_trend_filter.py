from src.enums.trend import Trend, MarketState, Momentum

class MarketTrendFilter:
    def __init__(self):
        pass

    def check_market_trend(self, market_index_data_list, periods=20):
        """
        Examine the overall market trend.
        :param market_index_data_list:
        :param periods:
        :return:
        """
        if len(market_index_data_list) < periods:
            return Trend.Sideway

        recent_data = market_index_data_list[-periods:]
        prices = [data.price.close_price for data in recent_data]

        # Calculate the market's MA20.
        ma20 = sum(prices) / len(prices)

        # Compare the current price with the MA20.
        current_price = prices[-1]

        if current_price > ma20 * 1.05: # The price is at least 5% higher than the MA20.
            return Trend.Up
        elif current_price < ma20 * 0.95: # The price is at least 5% lower than the MA20.
            return Trend.Down
        else:
            return Trend.Sideway

    def check_market_momentum (self, market_index_data_list, periods=10):
        """
        examine market dynamics
        :param market_index_data_list:
        :param periods:
        :return:
        """
        if len(market_index_data_list) < periods:
            return Momentum.Out

        recent_data = market_index_data_list[-periods:]
        prices = [data.price.close_price for data in recent_data]

        # Calculate the percentage change in price.
        price_change = (prices[-1] - prices[0]) / prices[0] * 100

        if price_change > 2: # Up more than 2% in the daily period
            return Momentum.In
        elif price_change < -2: # Down more than 2% in the daily period
            return Momentum.Out
        else:
            return Momentum.Out

    def check_market_volatility(self, market_index_data_list, periods=10):
        """
        Check market fluctuations.
        :param market_index_data_list:
        :param periods:
        :return:
        """
        if len(market_index_data_list) < periods:
            return Trend.Weak

        recent_data = market_index_data_list[-periods:]
        prices = [data.price.close_price for data in recent_data]

        # Calculate the standard deviation of the transaction value.
        avg_price = sum(prices) / len(prices)
        variance = sum((price - avg_price) ** 2 for price in prices) / len(prices)
        std_dev = variance ** 0.5

        # Calculate the percentage of variation.
        volatility_pct = (std_dev / avg_price) * 100

        if volatility_pct > 2:
            return Trend.Fomo
        elif volatility_pct < 0.5:
            return Trend.Weak
        else:
            return Trend.Good

    def check_market_state(selfself, market_index_data_list, periods=30):
        """
        Check the market status (early, middle, and late in the trend).
        :param market_index_data_list:
        :param periods:
        :return:
        """
        if len(market_index_data_list) < periods:
            return MarketState.EARLY_TREND

        recent_data = market_index_data_list[-periods:]
        prices = [data.price.close_price for data in recent_data]

        ma10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else prices[-1]
        ma30 = sum(prices) / len(prices)

        current_price = prices[-1]

        if ma10 > ma30:
            if current_price > ma10 * 1.05:
                return MarketState.LATE_TREND
            elif current_price > ma10:
                return MarketState.MID_TREND
            else:
                return MarketState.EARLY_TREND
        else:
            return MarketState.EARLY_TREND

    def check_sector_rotation(self, sector_data_dict, market_trend):
        """
        Industry rotation inspection
        :param sector_data_dict:
        :param market_trend:
        :return:
        """
        sector_strength = {}

        for sector, data_list in sector_data_dict.items():
            if len(data_list) < 5:
                continue

            recent_data = data_list[-5:]
            prices = [data.price.close_price for data in recent_data]

            # Calculate the percentage change over 5 days.
            price_change = (prices[-1] - prices[0]) / prices[0] * 100

            # Compare with market trends.
            if market_trend == Trend.Up:
                if price_change > 3: # The sector is growing faster than the market.
                    sector_strength[sector] = Trend.Good
                elif price_change < 0: # Sector declines as the market rises.
                    sector_strength[sector] = Trend.Weak
            elif market_trend == Trend.Down:
                if price_change > 0: # Sectors rise when the market falls.
                    sector_strength[sector] = Trend.Good
                elif price_change < -3: #The sector declined more sharply than the market.
                    sector_strength[sector] = Trend.Weak
            else: # Sideways
                if abs(price_change) > 2: # There have been significant fluctuations.
                    sector_strength[sector] = Trend.Good if price_change > 0 else Trend.Weak
                else:
                    sector_strength[sector] = Trend.Sideway

        return sector_strength

    def check_market_breadth(self, stock_data_list, market_trend):
        """
        Check the market breadth (number of stocks rising/falling).
        :param stock_data_list:
        :param market_trend:
        :return:
        """
        if not stock_data_list:
            return 0

        advancing = 0
        declining = 0
        unchanged = 0

        for stock_data in stock_data_list:
            if len(stock_data.company_data) < 2:
                continue

            current_price = stock_data.company_data[-1].price.close_price
            previous_price = stock_data.company_data[-2].price.close_price

            if current_price > previous_price:
                advancing += 1
            elif current_price < previous_price:
                declining += 1
            else:
                unchanged += 1

            total = advancing + declining + unchanged
            if total == 0: return 0

            advance_decline_radio = advancing / total if total > 0 else 0
            return advance_decline_radio