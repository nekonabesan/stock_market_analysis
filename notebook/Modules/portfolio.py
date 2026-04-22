import math
import collections
from .utility import Utility

class OwnedStock(object):
    def __init__(self):
        self.total_cost = 0
        self.total_count = 0
        self.current_count = 0
        self.average_cost = 0

    def append(self, count: int, cost: int) -> None:
        if self.total_count != self.current_count:
            self.total_count = self.current_count
            self.total_cost = self.current_count * self.average_cost
        self.total_cost += cost
        self.total_count += count
        self.current_count += count
        self.average_cost = math.ceil(self.total_cost / self.total_count)
    
    def remove(self, count: int) -> None:
        if self.current_count < count:
            raise ValueError("Can't remove", self.total_cost, count)
        self.current_count -= count

class Portfolio(object):
    def __init__(self, deposit: int):
        self.utility = Utility()
        self.deposit = deposit
        self.amount_of_investment = deposit
        self.total_profit = 0
        self.total_tax = 0
        self.total_fee = 0
        self.count_of_trades = 0
        self.count_of_wins = 0
        self.total_gains = 0
        self.total_losses = 0
        self.stocks = collections.defaultdict(OwnedStock)

    def add_deposit(self, deposit: int) -> None:
        self.deposit += deposit
        self.amount_of_investment += deposit

    def buy_stock(self, code: str, count: int, price: int) -> None:
        cost, fee = self.utility.calc_cost_of_buying(count, price)
        if cost > self.deposit:
            raise ValueError("cost > deposit", self.deposit, cost)
        # 保有株数増加
        self.stocks[code].append(count, cost)
        self.deposit -= cost
        self.total_fee += fee

    def sell_stock(self, code: str, count: int, price: int) -> None:
        subtotal = int(count * price)
        cost, fee = self.utility.calc_cost_of_selling(count, price)
        if cost > self.deposit + subtotal:
            raise ValueError("cost > deposit + subtotal", cost, self.deposit + subtotal)
            
        # 保有株数減少
        stock = self.stocks[code]
        average_cost = stock.average_cost
        stock.remove(count)
        if stock.current_count == 0:
            del self.stocks[code]
            
        # 利益計算
        profit = int((price - average_cost) * count - cost)
        self.total_profit += profit

        # トレード結果保存
        self.count_of_trades += 1
        if profit >= 0:
            self.count_of_wins += 1
            self.total_gains += profit
        else:
            self.total_losses += -profit

        # 源泉徴収額決定
        current_tax = self.utility.calc_tax(self.total_profit)
        withholding = current_tax - self.total_tax
        self.total_tax = current_tax

        self.deposit += subtotal - cost - withholding
        self.total_fee += fee

    def calc_current_total_price(self, get_current_proce_func) -> int:
        stock_price = sum(get_current_proce_func(code) 
                        * stock.current_count
                        for code, stock in self.stocks.items())
        return stock_price + self.deposit