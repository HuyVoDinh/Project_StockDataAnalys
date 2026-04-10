import pandas as pd
from datetime import datetime
import os

class Portfolio:
    def __init__(self, name, initial_cash = 1000000000):
        self.name = name
        self.cash = initial_cash
        self.position = {} #Symbol{'quantity': int, 'purchase_price': float}
        self.trade_history = [] # List of trades
        self.portfolio_file = f"Trading/{name}_portfolio.csv"
        self.history_file = f"Trading/{name}_history.csv"
        self.load_portfolio()

    def load_portfolio(self):
        """Load existing portfolio data if available"""
        if os.path.exists(self.portfolio_file):
            portfolio_data = pd.read_csv(self.portfolio_file)
            for _, row in portfolio_data.iterrows():
                self.position[row['symbol']] = {
                    'quantity': row['quantity'],
                    'purchase_price': row['purchase_price'],
                }

        if os.path.exists(self.history_file):
            history_data = pd.read_csv(self.history_file)
            for _, row in history_data.iterrows():
                self.trade_history.append({
                    'data': row['data'],
                    'symbol': row['symbol'],
                    'action': row['action'],
                    'price': row['price'],
                    'quantity': row['quantity'],
                    'cash_change': row['cash_change']
                })

            #Update cash balance based on trade history
            total_cash_change = sum(t['cash_change'] for t in self.trade_history)
            self.cash += total_cash_change + 1000000000 #Initial cash + net cash changes

    def save_portfolio(self):
        """Save current position"""
        portfolio_data = []
        for symbol, position in self.position.items():
            portfolio_data.append({
                'symbol': symbol,
                'quantity': position['quantity'],
                'purchase_price': position['purchase_price'],
            })

        df_portfolio = pd.DataFrame(portfolio_data)
        df_portfolio.to_csv(self.portfolio_file, index=False)

        # Save trade history
        df_history = pd.DataFrame(self.trade_history)
        df_history.to_csv(self.history_file, index=False)

    def buy(self, symbol, price, quantity):
        """Buy a stock"""
        cost = price * quantity
        if self.cash >= cost:
            self.cash -= cost
            if symbol in self.position:
                # Average down/up
                total_quantity = self.position[symbol]['quantity'] + quantity
                total_cost = (self.position[symbol]['quantity'] * self.position[symbol]['purchase_price']) + (price * quantity)
                avg_price = total_cost / total_quantity
                self.position[symbol]['quantity'] = total_quantity
                self.position[symbol]['purchase_price'] = avg_price
            else:
                self.position[symbol] = {
                    'quantity': quantity,
                    'purchase_price': price,
                }

            # Record trade
            self.trade_history.append({
                'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbol,
                'action': 'Buy',
                'price': price,
                'quantity': quantity,
                'cash_change': -cost,
            })

            self.save_portfolio()
            return True
        return False

    def sell(self, symbol, price, quantity=None):
        """Sell a stock"""
        if symbol in self.position:
            if quantity is None:
                quantity = self.position[symbol]['quantity']

            if self.position[symbol]['quantity'] >= quantity:
                proceeds = price * quantity
                self.cash += proceeds
                self.position[symbol]['quantity'] -= quantity

                if self.position[symbol]['quantity'] == 0:
                    del self.position[symbol]

                # Record trade
                self.trade_history.append({
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': symbol,
                    'action': 'Sell',
                    'price': price,
                    'quantity': quantity,
                    'cash_change': proceeds,
                })

                self.save_portfolio()
                return True
            return False

    def get_portfolio_value(self, current_prices):
        """Calculate total portfolio value"""
        value = self.cash
        for symbol, position in self.position.items():
            if symbol in current_prices:
                value += position['quantity'] * current_prices[symbol]
        return value

    def get_portfolio_report(self, current_prices):
        """Generate portfolio report"""
        report = f"Portfolio Report for {self.name}"
        report += "=" * 50 + "\n"
        report += f"Cash: {self.cash:,.0f} VND\\n"
        report += f"Total Value: {self.get_portfolio_value(current_prices):,.0f} VND\n"
        report += "\nPositions:\n"
        report += "-" * 30 + "\n"

        total_profit_loss = 0
        for symbol, position in self.position.items():
            current_price = current_prices.get(symbol, position['purchase_price'])
            market_value = position['quantity'] * current_price
            cost_basis = position['quantity'] * position['purchase_price']
            profit_loss = market_value - cost_basis
            total_profit_loss += profit_loss

            report += f"{symbol}: {position['quantity']} shares\n"
            report += f"  Purchase Price: {position['purchase_price']:,.0f} VND\n"
            report += f"  Market Value: {market_value:,.0f} VND\n"
            report += f"  P/L: {profit_loss:,.0f} VND\n\n"

        report += f"Unrealized P/L: {total_profit_loss:,.0f} VND\n"
        report += f"Realized P/L: {sum(t['cash_change'] for t in self.trade_history if t['action'] == 'SELL') - sum(abs(t['cash_change']) for t in self.trade_history if t['action'] == 'BUY'):,.0f} VND\n"
        
        return report

