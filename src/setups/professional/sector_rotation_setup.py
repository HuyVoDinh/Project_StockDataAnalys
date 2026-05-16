from src.filters.momentum.momentum_rotation_filter import MomentumRotationFilter
from src.filters.market_regime.market_regime_filter import MarketRegimeFilter
from src.filters.risk.risk_filter import RiskFilter
from src.enums.trend import Trend, MarketState
from src.enums.signal import Signal
from src.enums.risk import RiskLevel
from src.models.company import CompanyData

class SectorRotationSetup:
    def __init__(self):
        self.momentum_filter = MomentumRotationFilter()
        self.market_regime_filter = MarketRegimeFilter()
        self.risk_filter = RiskFilter()

    def check_setup(self, company: CompanyData, sector_data_dict=None, market_data_list=None, economic_data=None):
        """
        Professional Sector Rotation Setup
        This setup identifies the best performing sectors and rotates into leading stocks

        Key components:
        1. Sector momentum analysis
        2. Cross-sector relative strength
        3. Economic cycle positioning
        4. Risk management
        :param company:
        :param sector_data_dict:
        :param market_data_list:
        :param economic_data:
        :return:
        """
        if not company or not company.company_data or len(company.company_data) < 20:
            return None

        company_data_list = company.company_data
        current_data = company_data_list[-1]

        # Need sector data for analysis
        if not sector_data_dict:
            return None

        # 1. Analyze sector momentum
        sector_momentum_analysis = self._analyze_sector_momentum(sector_data_dict, company.symbol)
        if not sector_momentum_analysis:
            return None

        leading_sector, sector_rank, sector_percentile, sector_outperformance = sector_momentum_analysis

        # 2. Check if sector is in favor
        sector_favorability = self._assess_sector_favorability(leading_sector, economic_data)
        if sector_favorability < 0.6: # Need at least 60% favorability
            return None

        # 3. Analyze stock relative strength within sector
        stock_strength = self._analyze_stock_strength(company_data_list, sector_data_dict.get(leading_sector, []))
        if stock_strength < 70: # Need to be in top 30% of sector
            return None

        # 4. Check market regime compatibility
        if market_data_list:
            market_regime, volatility_regime, _ = self.market_regime_filter.market_regime_classification(market_data_list, sector_data_dict, periods=30)
        else:
            market_regime = MarketState.MID_TREND
            volatility_regime = Trend.Good

        # 5. Risk management
        current_price = current_data.price.close_price
        stop_loss = self._calculate_stop_loss(current_data, sector_data_dict.get(leading_sector, []))
        target_price = current_price * 1.12 # 12% target foir sector rotation

        # Check risk.reward
        rr_ratio = (target_price - current_price) / (current_price - stop_loss) if (current_price - stop_loss) > 0 else 0
        if rr_ratio < 1.8: # Need at least 1.8:1 risk/reward
            return None

        # Calculate position score
        score = (sector_percentile * 0.3) + (stock_strength * 0.4) + (rr_ratio * 8 * 0.3)

        return {
            'symbol': company.symbol,
            'setup_type': 'SECTOR_ROTATION',
            'direction': 'LONG',
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_reward': rr_ratio,
            'score': min(100, score),
            'confidence': 'HIGH' if score > 85 else 'MEDIUM' if score > 70 else 'LOW',
            'leading_sector': leading_sector,
            'sector_rank': sector_rank,
            'sector_percentile': sector_percentile,
            'sector_outperformance': sector_outperformance,
            'stock_strength': stock_strength,
            'market_regime': market_regime.name if hasattr(market_regime,'name') else str(market_regime),
        }

    def _analyze_sector_momentum(self, sector_data_dict, stock_symbol):
        """
        Analyze momentum across sectors to identify leaders
        :param sector_data_dict:
        :param stock_symbol:
        :return:
        """
        if not sector_data_dict:
            return None

        # Find which sector this stock belongs to (simplified)
        # In real implementation, this would use sector classification data
        leading_sector = None
        best_momentum = -float('inf')
        sector_analysis = {}

        for sector_name, sector_data_list in sector_data_dict.items():
            if len(sector_data_list) >= 20:
                prices = [data.price.close_price for data in sector_data_list[-20:]]
                if len(prices) >= 2 and prices[0] > 0:
                    momentum = (prices[-1] - prices[0]) / prices[0]
                    sector_analysis[sector_name] = momentum
                    if momentum > best_momentum:
                        best_momentum = momentum
                        leading_sector = sector_name

        if not leading_sector:
            return None

        # Calcualte sector rank and percentile
        sector_returns = list(sector_analysis.value())
        sector_returns.sort(reverse=True)

        sector_rank = list(sector_analysis.keys()).index(leading_sector) + 1
        sector_percentile = (len(sector_analysis) - sector_rank + 1) / len(sector_analysis) * 100
        sector_outperformance = sector_analysis[leading_sector] - (sum(sector_returns) / len(sector_returns) if sector_returns else 0)

        return leading_sector, sector_rank, sector_percentile, sector_outperformance

    def _assess_sector_favorability(self, sector_name, economic_data=None):
        """
        Assess sector favorability based on economic cycle
        Professional trades rotate sectors based on economic conditions
        :param sector_name:
        :param economic_data:
        :return:
        """
        # Economic cycle mapping (simplified)
        sector_cycle_map = {
            'TECH': ['EARLY', 'MID'],
            'FINANCIAL': ['EARLY', 'MID'],
            'CONSUMER_CYCLICAL': ['MID', 'LATE'],
            'ENERGY': ['EARLY', 'LATE'],
            'HEALTHCARE': ['ALL'],
            'UTILITIES': ['MID', 'LATE'],
            'CONSUMER_DEFENSIVE': ['LATE'],
            'INDUSTRIALS': ['EARLY', 'MID'],
        }

        # Curreent economic cycle (simplified - would come from economic data)
        current_cycle = 'MID' # Default assumption

        if economic_data:
            # Analyze economic indicators to determine cycle
            pass # implementation would depend on economic data structure

        # Check if sector is favorable in current cycle
        favorable_cycles = sector_cycle_map.get(sector_name.upper(), ['ALL'])
        if 'ALL' in favorable_cycles or current_cycle in favorable_cycles:
            favorability = 0.8 # High favorability
        else:
            favorability = 0.4 # Low favorability

        return favorability

    def _analyze_stock_strength(self, company_data_list, sector_data_dict):
        """
        Analyze stock strength relative to sector
        :param company_data_list:
        :param sector_data_dict:
        :return:
        """
        if len(company_data_list) < 20 or len(sector_data_dict) < 20:
            return 50 # Neutral

        # Calculate stock momentum
        stock_prices = [data.price.close_price for data in company_data_list[-20:]]
        if len(stock_prices) >= 2 and stock_prices[0] > 0:
            stock_momentum = (stock_prices[-1] - stock_prices[0]) / stock_prices[0]
        else:
            stock_momentum = 0

        # Calculate sector momentum
        sector_prices = [data.price.close_price for data in sector_data_dict[-20:]]
        if len(sector_prices) >= 2 and sector_prices[0] > 0:
            sector_momentum = (sector_prices[-1] - sector_prices[0]) / sector_prices[0]
        else:
            sector_momentum = 0


        # Calculate relative strength
        relative_strength = stock_momentum - sector_momentum

        # Convert to 0-100 score
        strength_score = min(100, max(0, 50 + (relative_strength * 500)))

        return strength_score

    def _calculate_stop_loss(self, current_data, sector_data_list):
        """
        Calculate appropriate stop loss level
        :param current_data:
        :param sector_data_list:
        :return:
        """
        current_price = current_data.price.close_price

        # Use Atr for stop loss calculation
        if current_data.ATR_14 and current_data.ATR_14 > 0:
            atr_stop = current_price - (2.0 * current_data.ATR_14)
        else:
            atr_stop = current_price * 0.95 # 5% default stop

        # Also consider support levels
        if sector_data_list and(sector_data_list) >= 10:
            recent_lows = [data.price.low_price for data in sector_data_list[-10:]]
            support_level = min(recent_lows) if recent_lows else current_price
            support_stop = support_level * 0.98 # 2% below
        else:
            support_stop = current_price * 0.95

        # Use more conservative (higher) stop loss
        stop_loss = max(atr_stop, support_stop, current_price * 0.92) # Minimum 8% stop

        return stop_loss

    def get_setup_details(self, setup_result):
        """
        Get detailed setup information
        :param setup_result:
        :return:
        """
        if not setup_result:
            return "No valid setup found"

        details = f"""
SECTOR ROTATION SETUP - {setup_result['symbol']}
======================================
Setup Type: {setup_result['setup_type']}
Direction: {setup_result['direction']}
Entry Price: {setup_result['entry_price']}
Stop loss: {setup_result['stop_loss']}
Target Price: {setup_result['target_price']}
Risk/Reward: {setup_result['risk_reward']}
Confidence: {setup_result['confidence']} (Score: {setup_result['score']})
Leading Sector: {setup_result['leading_sector']}
Sector Rank: {setup_result['sector_rank']}
Sector Percentile: {setup_result['sector_percentile']}
Sector Strength: {setup_result['sector_strength']}

Key Filters Passed
- Sector Momentum Analysis
- Sector Favorability
- Relative Stock Strength
- Risk Management
"""
        return details.strip()

# Helper fucntion to use the setup
def sector_rotation_setup(company_data, sector_data_dict=None, market_data_list=None, economic_data=None):
    """
    Function to be called by the trading system
    :param company_data:
    :param sector_data_dict:
    :param market_data_list:
    :param economic_data:
    :return:
    """
    setup = SectorRotationSetup()
    return setup.check_setup(company_data, sector_data_dict=sector_data_dict,market_data_list=market_data_list, economic_data=economic_data)