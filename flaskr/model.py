import enum
from datetime import date
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from flaskr import db, login_manager , apply_user_id
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "portfolio_user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    accounts = db.relationship('InvestmentAccount')
    stock_transactions = db.relationship('StockTransaction')

    def __iter__(self):
        yield ('email', self.email)

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
    trade_date = db.Column(db.DateTime, nullable=False)
    account_id = db.Column(db.Integer,
                           db.ForeignKey('investment_account.id'))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('portfolio_user.id'),
                        nullable=False)

    DATA_KEYS = set([
        'transaction_type',
        'stock_symbol',
        'cost_per_unit',
        'quantity',
        'trade_fee',
        'trade_date'
    ])

    def __iter__(self):
        yield ('id', self.id)
        yield ('transaction_type', self.transaction_type.name)
        yield ('stock_symbol', self.stock_symbol)
        yield ('cost_per_unit', str(Decimal(self.cost_per_unit) / 100))
        yield ('quantity', self.quantity)
        yield ('trade_fee', str(Decimal(self.trade_fee) / 100))
        yield ('trade_date', self.trade_date.strftime('%Y-%m-%d'))
        yield ('account_id', self.account_id)

    @staticmethod
    def serialize(data):
        return dict(
            id = data['id'],
            transaction_type = data['transaction_type'].name,
            stock_symbol = data['stock_symbol'].upper(),
            cost_per_unit = str(Decimal(data['cost_per_unit']) / 100),
            quantity = data['quantity'],
            trade_fee = str(Decimal(data['trade_fee']) / 100),
            trade_date = data['trade_date'].strftime('%Y-%m-%d'),
            account_id = data['account_id']
        )

    @staticmethod
    def deserialize(data):
        data['transaction_type'] = \
            StockTransactionType[data['transaction_type'].lower()]
        data['stock_symbol'] = data['stock_symbol'].upper()
        data['cost_per_unit'] = int(Decimal(data['cost_per_unit']) * 100)
        data['quantity'] = int(data['quantity'])
        data['trade_fee'] = int(Decimal(data['trade_fee']) * 100)
        data['trade_date'] = date.fromisoformat(data['trade_date'])
        return apply_user_id(data)


class InvestmentAccount(db.Model):
    __tablename__ = "investment_account"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    taxable = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('portfolio_user.id'),
                        nullable=False)
    transactions = db.relationship('StockTransaction',
                                   backref="investment_account")
    def __iter__(self):
        yield ('id', self.id)
        yield ('name', self.name)
        yield ('taxable', self.taxable)
