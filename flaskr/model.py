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
    """User's id"""
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    """User's email"""
    password_hash = db.Column(db.String(128), nullable=False)
    """User's hashed password"""
    accounts = db.relationship('InvestmentAccount')
    """Accounts owned by the user"""
    stock_transactions = db.relationship('StockTransaction')
    """StockTransactions beloning to the user"""

    def __iter__(self):
        yield ('email', self.email)

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        """
        Hashes the password and saves it as the user's password_hash

        Keyword arguments:
        password -- the user's password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Hashes the password and checks if it is equal to the user's password_hash

        Keyword arguments:
        password -- the user's password
        """
        return check_password_hash(self.password_hash, password)


class StockTransactionType(enum.Enum):
    buy = 0
    """Buy transaction type"""
    sell = 1
    """Sell transaction type"""


class StockTransaction(db.Model):
    __tablename__ = "stock_transaction"
    id = db.Column(db.Integer, primary_key=True)
    """StockTransaction's id"""
    transaction_type = db.Column(db.Enum(StockTransactionType), nullable=False)
    """StockTransaction's transaction type"""
    stock_symbol = db.Column(db.String, nullable=False)
    """StockTransaction's stock ticker symbol"""
    cost_per_unit = db.Column(db.Integer, nullable=False)
    """StockTransaction's cost per unit of stock in cents"""
    quantity = db.Column(db.Integer, nullable=False)
    """The quantity of the stock symbol in this stock transaction"""
    trade_fee = db.Column(db.Integer, nullable=False)
    """StockTransaction's trade commission fee in cents"""
    trade_date = db.Column(db.DateTime, nullable=False)
    """The date that this stock transaction occurred"""
    account_id = db.Column(db.Integer,
                           db.ForeignKey('investment_account.id'))
    """The investment account's id that this stock transaction belongs to"""
    user_id = db.Column(db.Integer,
                        db.ForeignKey('portfolio_user.id'),
                        nullable=False)
    """The id of the user that made this stock transaction"""

    DATA_KEYS = set([
        'transaction_type',
        'stock_symbol',
        'cost_per_unit',
        'quantity',
        'trade_fee',
        'trade_date'
    ])
    """The names of the data fields that need to be serialized"""

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
        """
        Returns a dict with the fields formatted in the way the client
        expects them
        """
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
        """
        Returns a dict with the fields formatt

        Keyword arguments:
        data -- a dict with the stock transaction fields in the client format
        """
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
    """InvestmentAccount's id"""
    name = db.Column(db.String, nullable=False)
    """InvestmentAccount's given display name"""
    taxable = db.Column(db.Boolean, nullable=False)
    """If true that means this investment account is a taxable account"""
    user_id = db.Column(db.Integer,
                        db.ForeignKey('portfolio_user.id'),
                        nullable=False)
    """The id of the user that owns this investment account"""
    transactions = db.relationship('StockTransaction',
                                   backref="investment_account")
    """The stock transactions that belong to this investment account"""

    def __iter__(self):
        yield ('id', self.id)
        yield ('name', self.name)
        yield ('taxable', self.taxable)
