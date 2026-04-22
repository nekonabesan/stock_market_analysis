import datetime as dt

class Order(object):

    def __init__(self, code):
        self.code = code

    def execute(self, date, portfolio, get_price_func):
        pass

    @classmethod
    def default_order_logger(cls, order_type, date, code, count, price, before_deposit, after_deposit):
        print("{} {} code:{} count:{} price:{} deposit:{} -> {}".format(
            date.strftime('%Y-%m-%d'),
            order_type,
            code,
            count,
            price,
            before_deposit,
            after_deposit
        ))
    logger = default_order_logger

class BuyMarketOrderAsPossible(Order):
    def __init__(self, code: str, unit: int):
        super().__init__(code)
        self.unit = unit
    
    def execute(self, date, portfolio, get_price_func) -> None:
        price = get_price_func(self.code)
        count_of_buying_unit = int(portfolio.deposit / price / self.unit)
        while count_of_buying_unit:
            try:
                count = count_of_buying_unit * self.unit
                prev_deposit = portfolio.deposit
                portfolio.buy_stock(self.code, count, price)
                self.logger("BUY", date, self.code, count, price,
                            prev_deposit, portfolio.deposit)
            except ValueError:
                count_of_buying_unit -= 1
            else:
                break

class BuyMarketOrderMoreThan(Order):
    def __init__(self, code: str, unit: int, under_limit: int):
        super().__init__(code)
        self.unit = unit
        self.under_limit = under_limit
        
    def execute(self, date, portfolio, get_price_func) -> None:
        price = get_price_func(self.code)
        unit_price = price * self.unit
        if unit_price > self.under_limit:
            count_of_buying_unit = 1
        else:
            count_of_buying_unit = int(self.under_limit / unit_price)
        while count_of_buying_unit:
            try:
                count = count_of_buying_unit * self.unit
                prev_deposit = portfolio.deposit
                portfolio.buy_stock(self.code, count, price)
                self.logger("BUY", date, self.code, count, price, prev_deposit, portfolio.deposit)
            except ValueError:
                count_of_buying_unit -= 1
            else:
                break

class SellMarketOrder(Order):
    def __init__(self, code: str, count: int):
        super().__init__(code)
        self.count = count
    
    def execute(self, date, portfolio, get_price_func) -> None:
        price = get_price_func(self.code)
        prev_deposit = portfolio.deposit
        portfolio.sell_stock(self.code, self.count, price)
        self.logger("SELL", date, self.code, self.count, price,
                    prev_deposit, portfolio.deposit)
        