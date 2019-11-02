from datetime import date
import csv
import json
import pytest
from flaskr import db
from flaskr.model import (
    InvestmentAccount,
    StockPrice,
    StockTransaction,
    StockTransactionType
)
import logging
import traceback


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
            with open('tests/resources/stock_price.csv', 'r') as csv_file:
                csv_iterator = csv.reader(csv_file)
                csv_iterator.__next__() # ignore the headers
                for row in csv_iterator:
                    db.session.add(StockPrice(**dict(
                        stock_symbol = row[0],
                        price_date = date.fromisoformat(row[1]),
                        close_price = int(row[2])
                    )))
            db.session.add(InvestmentAccount(**investment_account_1))
            db.session.commit()
        yield auth_app
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(e)
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

def test_get_account_with_one_transaction_market_value(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()
    response = client.get('/investment_account/1/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value'] == "$3312.00"

def test_get_account_no_transactions_market_value(investment_account_setup, client):
    app = investment_account_setup
    response = client.get('/investment_account/1/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value'] == "$0.00"

def test_get_account_buy_sell_market_value(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        sell_transaction = stock_transaction_1.copy()
        sell_transaction['quantity'] = 50
        sell_transaction['transaction_type'] = StockTransactionType.sell
        sell_transaction['trade_date'] = date(2016, 4, 28)
        db.session.add(StockTransaction(**sell_transaction))
        db.session.commit()
    response = client.get('/investment_account/1/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value'] == "$1656.00"
