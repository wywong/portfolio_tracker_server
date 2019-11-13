from flaskr import db
from flaskr.utils.formatting_utils import FormattingUtils
from flaskr.model import (
    StockTransaction,
    StockTransactionType,
    StockPrice
)
from sqlalchemy import func


class BookCostGenerator():
    def __init__(self, user_id, account_id=None):
        self.user_id = user_id
        self.account_id = account_id

    def next(self):
        return self.get_book_cost()

    def get_book_cost(self):
        """
        Returns the computed book cost of all transactions in this account, if the
        account has no tranasctions then N/A is returned.
        """
        book_cost = self.build_book_cost_query()
        if book_cost is None:
            return "N/A"
        return FormattingUtils.format_currency(book_cost)

    def build_book_cost_query(self):
        aggregation = func.sum(
            StockTransaction.cost_per_unit * StockTransaction.quantity + \
            StockTransaction.trade_fee
        )
        query = None
        if self.account_id is None:
            query = aggregation.filter(StockTransaction.user_id == self.user_id)
        else:
            query = aggregation.filter(
                ((StockTransaction.user_id == self.user_id) & \
                 (StockTransaction.account_id == self.account_id))
            )
        return db.session.query(query).scalar()
