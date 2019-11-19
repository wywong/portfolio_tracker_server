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

investment_account_2 = dict(
    name = "Taxable Account",
    taxable = True,
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

stock_transaction_3 = dict(
    transaction_type = StockTransactionType.buy,
    stock_symbol = "ZPR.TO",
    cost_per_unit = 960,
    quantity = 555,
    trade_fee = 995,
    trade_date = date(2016, 8, 23),
    account_id = None,
    user_id = 1
)

stock_transaction_4 = dict(
    transaction_type = StockTransactionType.buy,
    stock_symbol = "Bagel",
    cost_per_unit = 1000,
    quantity = 555,
    trade_fee = 995,
    trade_date = date(2016, 8, 23),
    account_id = 2,
    user_id = 1
)

stock_transaction_5 = dict(
    transaction_type = StockTransactionType.buy,
    stock_symbol = "Bagel",
    cost_per_unit = 1100,
    quantity = 45,
    trade_fee = 995,
    trade_date = date(2016, 8, 24),
    account_id = 2,
    user_id = 1
)

stock_transaction_6 = dict(
    transaction_type = StockTransactionType.sell,
    stock_symbol = "Bagel",
    cost_per_unit = 1200,
    quantity = 100,
    trade_fee = 995,
    trade_date = date(2016, 8, 25),
    account_id = 2,
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

def test_get_non_taxable_account_acb(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.commit()
    response = client.get('/investment_account/1/acb')
    json_data = json.loads(response.data)
    assert json_data['adjust_cost_base'] == {}


def test_get_empty_account_acb(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.commit()
    response = client.get('/investment_account/2/acb')
    json_data = json.loads(response.data)
    assert json_data['adjust_cost_base'] == {}

def test_get_one_stock_acb(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.add(StockTransaction(**stock_transaction_4))
        db.session.add(StockTransaction(**stock_transaction_5))
        db.session.add(StockTransaction(**stock_transaction_6))
        db.session.commit()
    response = client.get('/investment_account/2/acb')
    json_data = json.loads(response.data)
    acbs = json_data['adjust_cost_base']
    assert len(acbs) == 1
    assert acbs['Bagel'] == '$5,054.08'
