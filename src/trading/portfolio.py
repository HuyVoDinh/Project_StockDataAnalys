import pandas as pd
from datetime import datetime
import os
import json

class Portfolio:
    def __init__(self, name, initial_cash = 1000000000):
        self.name = name
        self.cash = initial_cash
        self.position = {} #Symbol{'quantity': int, 'purchase_price': float}
        self.trade_history = [] # List of trades
        self.portfolio_file = f"Trading/{name}_portfolio.json"
        self.history_file = f"Trading/{name}_history.csv"
        self.load_portfolio()

    def load_portfolio(self):
        """Load portfolio from JSON file"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cash = data.get('cash', self.cash)
                    self.position = data.get('positions', {})
            except Exception as e:
                print(f"[Portfolio][load_portfolio] Error loading portfolio: {e}")
                # Initialize with default values if there's an error
                self.cash = 1000000000
                self.position = {}
        # If no portfoolio file exists, it will be created when save_portfolio

        # Load trade history from CSV file
        if os.path.exists(self.history_file):
            try:
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
            except Exception as e:
                print(f"[Portfolio][load_portfolio] Error loading history: {e}")
                # Initialize with empty history if there's an error
                self.trade_history = []

            #Update cash balance based on trade history
            total_cash_change = sum(t['cash_change'] for t in self.trade_history)
            self.cash += total_cash_change + 1000000000 #Initial cash + net cash changes

    def save_portfolio(self):
        """Save current position to JSON file"""
        os.makedirs(os.path.dirname(self.portfolio_file), exist_ok=True)
        try:
            data = {
                'cash': self.cash,
                'positions': self.position,
            }
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[Portfolio][save_portfolio] Error saving portfolio: {e}")

    def buy(self, symbol, price, quantity):
        """Buy a stock"""
        cost = price * quantity
        if self.cash >= cost:
            self.cash -= cost
            if symbol in self.position:
                # Average down/up
                total_quantity = self.position[symbol]['quantity'] + quantity
                total_cost = (self.position[symbol]['quantity'] * self.position[symbol]['purchase_price']) + (price * quantity)
                avg_price = total_cost / total_quantity if total_quantity > 0 else price
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
        report = f"Portfolio Report for {self.name}\n"
        report += "=" * 50 + "\n"
        report += f"Cash: {self.cash:,.0f} VND\n"
        report += f"Total Value: {self.get_portfolio_value(current_prices):,.0f} VND\n"
        report += f"Number of positions: {len(current_prices)}\n"
        report += "\nPositions:\n"
        report += "-" * 30 + "\n"

        total_profit_loss = 0
        for symbol, position in self.position.items():
            current_price = current_prices.get(symbol, position['purchase_price'])
            market_value = position['quantity'] * current_price
            cost_basis = position['quantity'] * position['purchase_price']
            profit_loss = market_value - cost_basis
            total_profit_loss += profit_loss

            # Calcualte the number of percentage of the profit
            if cost_basis > 0:
                profit_pct = (profit_loss / cost_basis) * 100
                report += f"(symbol): {position['quantity']} shares\n"
                report += f" Purchase Price: {position['purchase_price']:,.0f} VND\n"
                report += f" Current Price: {current_price:,.0f} VND\n"
                report += f" Market Value: {market_value:,.0f} VND\n"
                report += f" Profit Loss: {profit_loss:,.0f} VND ({profit_pct:.2f}%)\n\n"
            else:
                report += f"{symbol}: {position['quantity']} shares\n"
                report += f"  Purchase Price: {position['purchase_price']:,.0f} VND\n"
                report += f"  Market Value: {market_value:,.0f} VND\n"
                report += f"  P/L: {profit_loss:,.0f} VND\n\n"

        # Calculate realized profit
        realized_profit = sum(t['cash_change'] for t in self.trade_history if t['action'] == 'Sell')
        report += f"Unrealized P/L: {total_profit_loss:,.0f} VND\n"
        report += f"Realized P/L: {sum(t['cash_change'] for t in self.trade_history if t['action'] == 'SELL') - sum(abs(t['cash_change']) for t in self.trade_history if t['action'] == 'BUY'):,.0f} VND\n"
        report += f"Total P/L: {total_profit_loss + realized_profit:,.0f} VND\n"
        return report

