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

good_transactions_filename = 'tests/resources/transaction_good.csv'
bad_transactions_filename = 'tests/resources/transaction_bad.csv'

@pytest.fixture
def one_account(auth_app_user_1):
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

def test_batch_create_transactions(one_account, client):
    with open(good_transactions_filename, 'rb') as csv_file:
        data = {}
        data['file'] = (csv_file, csv_file.name)
        response = client.post('/transaction/batch',
                               data=data,
                               content_type='multipart/form-data')

    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 4
        assert transactions[0].transaction_type == StockTransactionType.buy
        assert transactions[0].stock_symbol == "XAW.TO"
        assert transactions[0].cost_per_unit == 2718
        assert transactions[0].quantity == 100
        assert transactions[0].trade_fee == 995
        assert transactions[0].trade_date.strftime('%Y-%m-%d') == '2016-05-15'
        assert transactions[1].transaction_type == StockTransactionType.buy
        assert transactions[2].transaction_type == StockTransactionType.sell
        assert transactions[3].transaction_type == StockTransactionType.buy
        for transaction in transactions:
            assert transaction.account_id == None
            assert transaction.user_id == 1


def test_batch_create_transactions_account(one_account, client):
    with open(good_transactions_filename, 'rb') as csv_file:
        data = { 'account_id': 1 }
        data['file'] = (csv_file, csv_file.name)
        response = client.post('/transaction/batch',
                               data=data,
                               content_type='multipart/form-data')

    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 4
        assert transactions[0].transaction_type == StockTransactionType.buy
        assert transactions[0].stock_symbol == "XAW.TO"
        assert transactions[0].cost_per_unit == 2718
        assert transactions[0].quantity == 100
        assert transactions[0].trade_fee == 995
        assert transactions[0].trade_date.strftime('%Y-%m-%d') == '2016-05-15'
        assert transactions[1].transaction_type == StockTransactionType.buy
        assert transactions[2].transaction_type == StockTransactionType.sell
        assert transactions[3].transaction_type == StockTransactionType.buy
        for transaction in transactions:
            assert transaction.account_id == 1
            assert transaction.user_id == 1

def test_batch_create_transactions_other_user(one_account, auth_app_user_2, client):
    with open(good_transactions_filename, 'rb') as csv_file:
        data = {}
        data['file'] = (csv_file, csv_file.name)
        response = client.post('/transaction/batch',
                               data=data,
                               content_type='multipart/form-data')

    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 4
        assert transactions[0].transaction_type == StockTransactionType.buy
        assert transactions[0].stock_symbol == "XAW.TO"
        assert transactions[0].cost_per_unit == 2718
        assert transactions[0].quantity == 100
        assert transactions[0].trade_fee == 995
        assert transactions[0].trade_date.strftime('%Y-%m-%d') == '2016-05-15'
        assert transactions[1].transaction_type == StockTransactionType.buy
        assert transactions[2].transaction_type == StockTransactionType.sell
        assert transactions[3].transaction_type == StockTransactionType.buy
        for transaction in transactions:
            assert transaction.account_id == None
            assert transaction.user_id == 2

def test_bad_batch_create_transactions(one_account, client):
    with open(bad_transactions_filename, 'rb') as csv_file:
        data = {}
        data['file'] = (csv_file, csv_file.name)
        response = client.post('/transaction/batch',
                               data=data,
                               content_type='multipart/form-data')

    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 0
