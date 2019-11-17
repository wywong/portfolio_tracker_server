from flaskr import db
from flaskr.utils.formatting_utils import FormattingUtils
from flaskr.model import (
    InvestmentAccount,
    StockTransaction,
    StockTransactionType
)
from sqlalchemy import func


class AdjustCostBaseGenerator():
    def __init__(self, user_id, account_id):
        self.user_id = user_id
        self.account_id = account_id

    def next(self):
        return self.get_adjust_cost_base()

    def get_adjust_cost_base(self):
        is_account_taxable = db.session.query(InvestmentAccount.taxable) \
                .filter((InvestmentAccount.id == self.account_id) & \
                        (InvestmentAccount.user_id == self.user_id)).scalar()

        stock_acbs = dict()
        stock_quantities = dict()
        if not is_account_taxable:
            return stock_acbs

        for row in self.build_transaction_iterator():
            stock_symbol = row[0]
            quantity = row[1]
            cost_per_unit = row[2]
            trade_fee = row[3]
            transaction_type = row[4]
            stock_acbs.setdefault(stock_symbol, 0.0)
            stock_quantities.setdefault(stock_symbol, 0)
            if transaction_type == StockTransactionType.buy:
                acb_change = (quantity * cost_per_unit) + trade_fee
                stock_acbs[stock_symbol] += acb_change
                stock_quantities[stock_symbol] += quantity
            elif transaction_type == StockTransactionType.sell:
                prev_quantity = stock_quantities[stock_symbol]
                acb_multiplier = (prev_quantity - quantity) / prev_quantity
                stock_acbs[stock_symbol] *= acb_multiplier
                stock_quantities[stock_symbol] -= quantity

        return dict(
            map(lambda kv: self.format_value(kv[0], kv[1]), stock_acbs.items())
        )

    def build_transaction_iterator(self):
        return db.session.query(StockTransaction) \
                .filter((StockTransaction.account_id == self.account_id) & \
                        (StockTransaction.user_id == self.user_id)) \
                .order_by(StockTransaction.trade_date) \
                .values(
                    StockTransaction.stock_symbol,
                    StockTransaction.quantity,
                    StockTransaction.cost_per_unit,
                    StockTransaction.trade_fee,
                    StockTransaction.transaction_type
                )

    def format_value(self, key, value):
        return (key, FormattingUtils.format_currency(round(value)))
