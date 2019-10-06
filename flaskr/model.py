import enum
from flask_sqlalchemy import SQLAlchemy
from flaskr import db


class StockTransactionType(enum.Enum):
    buy = 0
    sell = 1


class StockTransaction(db.Model):
    __tablename__ = "stock_transaction"
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.Enum(StockTransactionType), nullable=False)
    stock_symbol = db.Column(db.String, nullable=False)
    cost_per_unit = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    trade_fee = db.Column(db.Integer, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('investment_account.id'))

    def __iter__(self):
        yield ('id', self.id)
        yield ('transaction_type', self.transaction_type.value)
        yield ('stock_symbol', self.stock_symbol)
        yield ('cost_per_unit', self.cost_per_unit)
        yield ('quantity', self.quantity)
        yield ('trade_fee', self.trade_fee)


class InvestmentAccount(db.Model):
    __tablename__ = "investment_account"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    taxable = db.Column(db.Boolean, nullable=False)
    transactions = db.relationship('stock_transaction')
