from src.filters.volatility.advanced_volatility_filter import AdvancedVolatilityFilter
from src.filters.options.options_filter import OptionFilter
from src.filters.risk.risk_filter import RiskFilter
from src.filters.market_regime.market_regime_filter import MarketRegimeFilter
from src.enums.trend import Trend, MarketState
from src.enums.signal import Signal, Emplitude
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class VolatilityCrushSetup:
    def __init__(self):
        self.volatility_filter = AdvancedVolatilityFilter()
        self.risk_filter = RiskFilter()
        self.market_regime_filter = MarketRegimeFilter()

    def check_setup(self, company: CompanyData, options_data_list=None, earnings_date=None, market_data_list=None, sector_data_list=None):
        """
        Professional Volatility Crush Setup
        This setup capitalizes on the volatility decline after earnings announcements

        Key components:
        1. High implied volatility ahead of events
        2. Earnings or event timing
        3. Volatility crush identification
        4. Risk management
        :param company:
        :param options_data_list:
        :param earnings_date:
        :param market_data_list:
        :param sector_data_list:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 20:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # Need options data for volatility crush setup
        if not options_data_list:
            return None

        # 1. Check for high implied volatility
        iv_rank, iv_percentile = self._analyze_implied_volatility(options_data_list)
        if iv_rank < 50: # Need about median IV rank
            return None

        # 2. Check for upcoming events (earnings, etc)
        if not earnings_date:
            return None
        days_to_event = self._calculate_days_to_event(earnings_date)
        if days_to_event < 1 or days_to_event > 30: # Only consider 1-30 days out
            return None

        # 3. Analyze volatility regime
        volatility_regime, volatility_trend, risk_level = self.volatility_filter.volatility_regime_analysis(company_data_list, periods=20)

        # Want to see elevated realized volatility
        if volatility_regime not in [Emplitude.Good, Emplitude.Break, Emplitude.Bulltrap]:
            return None

        # 4. Check for volatility premium (IV > HV)
        historical_volatility = self._calculate_historical_volatility(company_data_list)
        volatility_premium = iv_percentile - (historical_volatility * 100) if historical_volatility else 0

        if volatility_premium < 10: # Need at least 10% premium
            return None

        # 5. Market regime compatibility
        if market_data_list and sector_data_list:
            market_regime, market_volatility, _ = self.market_regime_filter.market_regime_classification(market_data_list, {'sector': sector_data_list}, periods=30)
        else:
            market_regime = MarketState.MID_TREND
            market_volatility = Trend.Good

        # 6. Risk management for volatility crush
        current_price = current_data.price.close_price
        position_size = self._calculate_position_size(current_price, iv_rank, days_to_event)

        # For volatility crush, we're typically selling options (short premium)
        # So we want to define max loss scenarios
        max_loss = self._calculate_max_loss(current_price, options_data_list, position_size)

        # Calculate expected return (volatility crush potential)
        expected_return = self._estimate_volatility_crush(iv_rank, days_to_event)

        # Risk/reward for volatility selling
        if max_loss <= 0:
            return None

        rr_ratio = expected_return / (max_loss / position_size) if position_size else 0
        if rr_ratio < 1.5: # Need at least 1.5:1 risk/reward
            return None

        # Calculate position score
        score = (iv_rank * 0.4) + (volatility_premium * 0.3) + (rr_ratio * 10 * 0.3)

        return {
            'symbol': company.symbol,
            'setup_type': 'VOLATILITY_CRUSH',
            'direction': 'SHORT_VOLATILITY',
            'current_price': current_price,
            'position_size': position_size,
            'max_loss': max_loss,
            'expected_return': expected_return,
            'risk_reward': rr_ratio,
            'score': score,
            'confidence': 'HIGH' if score > 80 else 'MEDIUM' if score > 65 else 'LOW',
            'iv_rank': iv_rank,
            'iv_percentile': iv_percentile,
            'historical_volatility': historical_volatility,
            'volatility_premium': volatility_premium,
            'days_to_event': days_to_event,
            'earnings_date': earnings_date,
            'market_regime': market_regime.name if hasattr(market_regime, 'name') else str(market_regime)
        }

    def _analyze_implied_volatility(self, options_data_list):
        """
        Analyze implied volatility levels and rank
        :param options_data_list:
        :return:
        """
        if not options_data_list:
            return 0, 0

        # Extract current IV data
        current_options = options_data_list[-1] if options_data_list else None
        if not current_options or not hasattr(current_options, 'implied_volatility'):
            return 0, 0

        current_iv = current_options.implied_volatility
        if current_iv is None:
            return 0, 0

        # Calculate IV rank and percentile
        historical_ivs = []
        for options_data in options_data_list[-60:]: # Last 60 periods
            if hasattr(options_data, 'implied_volatility') and options_data.implied_volatility is not None:
                historical_ivs.append(options_data.implied_volatility)

        if len(historical_ivs) < 10:
            return 0, 0

        # IV rank = (Current IV - 52-week low) / (52-week high - 52-week low)
        iv_low = min(historical_ivs)
        iv_high = max(historical_ivs)

        if iv_high == iv_low:
            iv_rank = 50

        else:
            iv_rank = ((current_iv - iv_low) / (iv_high - iv_low)) * 100

        # IV percentile = % of time IV was bellow current level
        below_current = sum(1 for iv in historical_ivs if iv < current_iv)
        iv_percentile = (below_current / len(historical_ivs)) * 100 if historical_ivs else 0

        return iv_rank, iv_percentile

    def _calculate_days_to_event(self, event_date):
        """
        Calculate days remaining until event
        :param event_date:
        :return:
        """
        from datetime import datetime, date

        if isinstance(event_date, str):
            try:
                event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            except ValueError:
                return 0
        elif isinstance(event_date, datetime):
            event_date = event_date.date()
        elif not isinstance(event_date, date):
            return 0

        today = date.today()
        delta = event_date - today

        return delta.days

    def _calculate_historical_volatility(self, company_data_list):
        """
        Calculate historical volatility from price data
        :param company_data_list:
        :return:
        """
        if len(company_data_list) < 10:
            return 0

        # Extract prices
        prices = [data.price.close_price for data in company_data_list[-20:] if data.price.close_price > 0]

        if len(prices) < 5:
            return 0

        # Calculate returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] > 0]

        if len(returns) < 3:
            return 0

        # Calculate standard deviation (volatility)
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        volatility = variance ** 0.5

        # Annualize (assuming daily data)
        annualized_Volatility = volatility * (252 ** 0.5) # 252 trading days

        return annualized_Volatility

    def _calculate_position_size(self, current_price, iv_rank, days_to_event):
        """
        Calculate appropriate position size for volatility setup
        :param current_price:
        :param iv_rank:
        :param days_to_event:
        :return:
        """
        # Base position size inversely related to IV rank (higher IV = smaller positions)
        base_size = 100 # Base 100 contracts/shares
        iv_adjustment = max(0.1, 1 - (iv_rank / 100)) # Reduce size as IV increases

        # Time adjustment (shorter time = smaller positions due to gamma risk)
        time_adjustment = min(1.0, days_to_event / 30) # Scale 1-30 days to 0.03-1.0

        position_size = base_size * iv_adjustment * time_adjustment

        # Minimum position size
        position_size = max(10, position_size)

        return position_size

    def _calculate_max_loss(self, current_price, options_data_list, position_size):
        """
        Calculate maximum potential loss for the setup
        :param current_price:
        :param options_data_list:
        :param position_size:
        :return:
        """
        if not options_data_list or position_size <= 0:
            return 0

        current_options = options_data_list[-1] if options_data_list else None
        if not current_options:
            return position_size * current_price * 0.1 # Default 10% of position value

        # For short options strategies, max loss depends on strategy type
        # This is a simplified calculate -actual max loss depends on specific options structure
        if hasattr(current_options, 'option_type') and current_options.option_type:
            if 'straddle' in current_options.option_type.lower() or 'strangle' in current_options.option_type.lower():
                # Short straddles/stragles have unlimited loss potential
                # Use a risk-based estimate
                max_loss = position_size * current_price * 0.2 # 20% risk estimate
            elif 'credit_spread' in current_options.option_type.lower():
                # Credit spreads have defined max loss
                if hasattr(current_options, 'spread_width') and current_options.spread_width:
                    max_loss = position_size * current_options.spread_width
                else:
                    max_loss = position_size * current_price * 0.05 # 5% risk estimate
            else:
                # Default calculation
                max_loss = position_size * current_price * 0.1
        else:
            # Default calculation
            max_loss = position_size * current_price * 0.1

        return max_loss

    def _estimate_volatility_crush(self, iv_rank, days_to_event):
        """
        Estimate potential return from volatility crush
        :param iv_rank:
        :param days_to_event:
        :return:
        """
        # Higher IV rank typically means larger potential crush
        base_crush = iv_rank * 0.3 # 30% of IV rank as based crush

        # Time decay accelerates closer to expiration
        time_factor = max(0.5, min(2.0, 30 / days_to_event if days_to_event > 0 else 1))

        # Estimate expected return from volatility crush
        expected_return = base_crush * time_factor

        # Cap at reasonable levels
        expected_return = min(50, expected_return) # Max 50% expected return

        return expected_return

    def get_setup_details(self, setup_result):
        """
        Get detailed information about the setup for reporting
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        details = f"""
VOLATILITY CRUSH SETUP - {setup_result['symbol']}
==================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Current Price: {setup_result['current_price']}
Position Size: {setup_result['position_size']}
Max Loss: {setup_result['max_loss']}
Expected Return: {setup_result['expected_return']}
Risk Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})
IV Rank: {setup_result['iv_rank']}
IV Percentile: {setup_result['iv_percentile']}
Historical Volatility: {setup_result['historical_volatility']}
Volatility Premium: {setup_result['volatility_premium']}
Days to Event: {setup_result['days_to_event']}
Earnings Date: {setup_result['earnings_date']}
Market Regime: {setup_result['market_regime']}

Key Filters Passed:
- High Implied Volatility
- Event Timing
- Volatility Premium
- Risk Management
"""
        return details.strip()

# Helper function to use the setup
def volatility_crush_setup(company_data, options_data_list=None, earnings_date=None, market_data_list=None, sector_data_list=None):
    """
    Function to be called by the trading system

    :param company_data:
    :param options_data_list:
    :param earnings_date:
    :param market_data_list:
    :param sector_data_list:
    :return:
    """
    setup = VolatilityCrushSetup()
    return setup.check_setup(company_data, options_data_list, earnings_date, market_data_list, sector_data_list)