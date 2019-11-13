from flaskr import db
from flaskr.utils.formatting_utils import FormattingUtils
from flaskr.model import (
    StockTransaction,
    StockTransactionType,
    StockPrice
)
from sqlalchemy import func


class MarketValueGenerator():
    def __init__(self, user_id, account_id=None):
        self.user_id = user_id
        self.account_id = account_id

    def next(self):
        return self.get_market_value()

    def get_market_value(self):
        """
        Returns the market value of all the stocks in the portfolio
        """
        total_value = 0
        breakdown = {}
        stock_values = self.build_market_price_query()
        for row in stock_values:
            value = row[0] * row[1]
            stock_symbol = row[2]
            transaction_type = row[3]
            breakdown.setdefault(stock_symbol, 0)
            if transaction_type == StockTransactionType.buy:
                total_value += value
                breakdown[stock_symbol] += value
            elif transaction_type == StockTransactionType.sell:
                total_value -= value
                breakdown[stock_symbol] -= value

        return dict(
            total = FormattingUtils.format_currency(total_value),
            breakdown = self.build_stock_market_values(breakdown, total_value)
        )

    def build_market_price_query(self):
        last_date = db.session.query(
            func.max(StockPrice.price_date).label('latest_price_date')
        ).subquery('last_date')
        price_query = db.session.query(
            StockPrice.stock_symbol,
            StockPrice.close_price.label('close_price')
        ).filter(
            StockPrice.price_date == last_date.c.latest_price_date
        ).subquery('price_query')

        market_price_query = db.session.query(
            func.sum(StockTransaction.quantity),
            func.min(price_query.c.close_price),
            StockTransaction.stock_symbol,
            StockTransaction.transaction_type
        ).join(price_query, StockTransaction.stock_symbol == \
               price_query.c.stock_symbol) \
            .group_by(StockTransaction.stock_symbol) \
            .group_by(StockTransaction.transaction_type)

        if self.account_id is None:
            return market_price_query \
                .filter(StockTransaction.user_id == self.user_id)
        else:
            return market_price_query \
                .filter((StockTransaction.account_id == self.account_id) & \
                        (StockTransaction.user_id == self.user_id))

    def build_stock_market_values(self, breakdown, total_value):
        values = {}
        for kv in breakdown.items():
            values[kv[0]] = dict(
                formatted_value = FormattingUtils.format_currency(kv[1]),
                raw_percent = kv[1],
                percent = FormattingUtils.format_percentage(kv[1], total_value)
            )
        return values
