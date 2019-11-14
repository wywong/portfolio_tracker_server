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
    name = "Cash account",
    taxable = True,
    user_id = 1
)

investment_account_3 = dict(
    name = "High risk account",
    taxable = True,
    user_id = 2
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

def test_get_empty_book_value(investment_account_setup, client):
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['book_cost'] == "N/A"

def test_stats_one_transaction_book_value(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['book_cost'] == "$3,150.99"

def test_stats_two_transaction_diff_account_book_value(investment_account_setup,
                                                       client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.add(StockTransaction(**stock_transaction_1))
        stock_account_2 = stock_transaction_2.copy()
        stock_account_2['account_id'] = 2
        db.session.add(StockTransaction(**stock_account_2))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['book_cost'] == "$8,362.98"


def test_stats_two_transaction_diff_user_book_value(investment_account_setup,
                                                    client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.add(InvestmentAccount(**investment_account_3))
        db.session.add(StockTransaction(**stock_transaction_1))
        stock_account_2 = stock_transaction_2.copy()
        stock_account_2['user_id'] = 2
        stock_account_2['account_id'] = 3
        db.session.add(StockTransaction(**stock_account_2))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['book_cost'] == "$3,150.99"

def test_stats_one_transaction_market_value(investment_account_setup,
                                            client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$3,312.00"
    breakdown = json_data['market_value']['breakdown']
    assert breakdown['VCN.TO']["formatted_value"] == "$3,312.00"
    assert breakdown['VCN.TO']['percent'] == '100.0%'

def test_stats_one_transaction_market_value_other_user(investment_account_setup,
                                                       auth_app_user_2,
                                                       client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$0.00"
    breakdown = json_data['market_value']['breakdown']
    assert len(breakdown) == 0

def test_get_account_no_transactions_market_value(investment_account_setup,
                                                  client):
    app = investment_account_setup
    response = client.get('/transaction/stats')
    logging.error(response.data)
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$0.00"
    assert len(json_data['market_value']['breakdown']) == 0

def test_get_account_buy_sell_market_value(investment_account_setup,
                                           client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        sell_transaction = stock_transaction_1.copy()
        sell_transaction['quantity'] = 50
        sell_transaction['transaction_type'] = StockTransactionType.sell
        sell_transaction['trade_date'] = date(2016, 4, 28)
        db.session.add(StockTransaction(**sell_transaction))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$1,656.00"
    breakdown = json_data['market_value']['breakdown']
    assert breakdown['VCN.TO']["formatted_value"] == "$1,656.00"
    assert breakdown['VCN.TO']['percent'] == '100.0%'

def test_stats_multi_stock_market_value(investment_account_setup,
                                        client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.add(StockTransaction(**stock_transaction_2))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$8,508.00"
    breakdown = json_data['market_value']['breakdown']
    assert len(breakdown) == 2
    assert breakdown['VCN.TO']["formatted_value"] == "$3,312.00"
    assert breakdown['VAB.TO']["formatted_value"] == "$5,196.00"
    assert breakdown['VCN.TO']['percent'] == '38.9%'
    assert breakdown['VAB.TO']['percent'] == '61.1%'

def test_stats_multi_stock_account_market_value(investment_account_setup,
                                                client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.add(StockTransaction(**stock_transaction_1))
        stock_account_2 = stock_transaction_2.copy()
        stock_account_2['user_id'] = 1
        stock_account_2['account_id'] = 2
        db.session.add(StockTransaction(**stock_account_2))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$8,508.00"
    breakdown = json_data['market_value']['breakdown']
    assert len(breakdown) == 2
    assert breakdown['VCN.TO']["formatted_value"] == "$3,312.00"
    assert breakdown['VAB.TO']["formatted_value"] == "$5,196.00"
    assert breakdown['VCN.TO']['percent'] == '38.9%'
    assert breakdown['VAB.TO']['percent'] == '61.1%'

def test_stats_multi_stock_user_market_value(investment_account_setup,
                                             client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.add(InvestmentAccount(**investment_account_3))
        db.session.add(StockTransaction(**stock_transaction_1))
        stock_account_2 = stock_transaction_2.copy()
        stock_account_2['user_id'] = 2
        stock_account_2['account_id'] = 3
        db.session.add(StockTransaction(**stock_account_2))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$3,312.00"
    breakdown = json_data['market_value']['breakdown']
    assert len(breakdown) == 1
    assert breakdown['VCN.TO']["formatted_value"] == "$3,312.00"
    assert breakdown['VCN.TO']['percent'] == '100.0%'

def test_stats_missing_stock_market_value(investment_account_setup,
                                          client):
    app = investment_account_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        vsb = stock_transaction_2.copy()
        vsb['stock_symbol'] = "VSB.TO"
        db.session.add(StockTransaction(**vsb))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$3,312.00"
    breakdown = json_data['market_value']['breakdown']
    assert len(breakdown) == 1
    assert breakdown['VCN.TO']["formatted_value"] == "$3,312.00"
    assert breakdown['VCN.TO']['percent'] == '100.0%'

def test_stats_large_market_value(investment_account_setup, client):
    app = investment_account_setup
    with app.app_context():
        large = stock_transaction_1.copy()
        large['quantity'] = 123456
        db.session.add(StockTransaction(**large))
        db.session.commit()
    response = client.get('/transaction/stats')
    json_data = json.loads(response.data)
    assert json_data['market_value']['total'] == "$4,088,862.72"
    breakdown = json_data['market_value']['breakdown']
    assert len(breakdown) == 1
    assert breakdown['VCN.TO']["formatted_value"] == "$4,088,862.72"
    assert breakdown['VCN.TO']['percent'] == '100.0%'
