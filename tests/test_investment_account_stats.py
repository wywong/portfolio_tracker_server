from datetime import date
import json
import pytest
from flaskr import db
from flaskr.model import (
    InvestmentAccount,
    StockTransaction,
    StockTransactionType
)


investment_account_1 = dict(
    name = "TFSA",
    taxable = False,
    user_id = 1
)

stock_transaction_1 = dict(
    transaction_type = StockTransactionType.buy,
    stock_symbol = "VCN.TO",
    cost_per_unit = 3141,
    quantity = 100,
    trade_fee = 999,
    trade_date = date(2016, 4, 23),
    account_id = 1,
    user_id = 1
)

stock_transaction_2 = dict(
    transaction_type = StockTransactionType.buy,
    stock_symbol = "VAB.TO",
    cost_per_unit = 2601,
    quantity = 200,
    trade_fee = 999,
    trade_date = date(2016, 8, 23),
    account_id = 1,
    user_id = 1
)


@pytest.fixture
def investment_account_setup(auth_app_user_1):
    auth_app = auth_app_user_1
    try:
        with auth_app.app_context():
            db.session.add(InvestmentAccount(**investment_account_1))
            db.session.commit()
        yield auth_app
    except Exception as e:
        assert False
    finally:
        with auth_app.app_context():
            StockTransaction.query.delete()
            InvestmentAccount.query.delete()
            db.session.commit()

def test_get_empty_account_book_value(investment_account_setup, client):
    response = client.get('/investment_account/1/stats')
    json_data = json.loads(response.data)
    assert json_data['book_cost'] == "N/A"

def test_get_account_with_one_transaction_book_value(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()
    response = client.get('/investment_account/1/stats')
    json_data = json.loads(response.data)
    assert json_data['book_cost'] == "$3150.99"

def test_get_account_with_two_transaction_book_value(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.add(StockTransaction(**stock_transaction_2))
        db.session.commit()
    response = client.get('/investment_account/1/stats')
    json_data = json.loads(response.data)
    assert json_data['book_cost'] == "$8362.98"
