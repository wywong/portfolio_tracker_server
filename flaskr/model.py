import enum
from flask_sqlalchemy import SQLAlchemy
from flaskr import db, login_manager
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
    account_id = db.Column(db.Integer,
                           db.ForeignKey('investment_account.id'))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('portfolio_user.id'),
                        nullable=False)

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
    user_id = db.Column(db.Integer,
                        db.ForeignKey('portfolio_user.id'),
                        nullable=False)
    transactions = db.relationship('StockTransaction',
                                   backref="investment_account")
    def __iter__(self):
        yield ('id', self.id)
        yield ('name', self.name)
        yield ('taxable', self.taxable)
