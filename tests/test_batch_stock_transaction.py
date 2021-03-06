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
    account_id = None,
    user_id = 1
)

good_transactions_filename = 'tests/resources/transaction_good.csv'
other_transactions_filename = 'tests/resources/transaction_other_types.csv'
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
        response = client.post('/transaction/import',
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

def test_batch_create_transactions(one_account, client):
    with open(good_transactions_filename, 'rb') as csv_file:
        data = {}
        data['file'] = (csv_file, csv_file.name)
        response = client.post('/transaction/import',
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
    with open(other_transactions_filename, 'rb') as csv_file:
        data = { 'account_id': 1 }
        data['file'] = (csv_file, csv_file.name)
        response = client.post('/transaction/import',
                               data=data,
                               content_type='multipart/form-data')

    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 3
        div = transactions[0]
        roc = transactions[1]
        rcd = transactions[2]
        assert div.transaction_type == StockTransactionType.dividend
        assert roc.transaction_type == StockTransactionType.return_of_capital
        assert rcd.transaction_type == \
            StockTransactionType.reinvested_capital_distribution
        for transaction in transactions:
            assert transaction.account_id == 1
            assert transaction.user_id == 1

def test_batch_create_transactions_other_user(one_account, auth_app_user_2, client):
    with open(good_transactions_filename, 'rb') as csv_file:
        data = {}
        data['file'] = (csv_file, csv_file.name)
        response = client.post('/transaction/import',
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
        response = client.post('/transaction/import',
                               data=data,
                               content_type='multipart/form-data')

    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 0

def test_batch_move_transactions(one_account, client):
    with one_account.app_context():
        for i in range(0, 5):
            db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()

    response = client.put('/transaction/move', data=json.dumps(dict(
        new_account_id = 1,
        transaction_ids = [1, 2, 3, 4, 5]
    )))
    with one_account.app_context():
        transactions = StockTransaction.query.all()
        for transaction in transactions:
            assert transaction.account_id == 1

def test_batch_move_transactions_other_user(one_account, auth_app_user_2, client):
    with one_account.app_context():
        for i in range(0, 5):
            db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()

    response = client.put('/transaction/move', data=json.dumps(dict(
        new_account_id = 1,
        transaction_ids = [1, 2, 3, 4, 5]
    )))
    with one_account.app_context():
        transactions = StockTransaction.query.all()
        for transaction in transactions:
            assert transaction.account_id is None

def test_batch_delete_transactions(one_account, client):
    with one_account.app_context():
        for i in range(0, 5):
            db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()

    response = client.delete('/transaction/batch', data=json.dumps(dict(
        transaction_ids = [1, 2, 3, 5]
    )))
    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 1

def test_batch_delete_transactions_other_user(one_account, auth_app_user_2, client):
    with one_account.app_context():
        for i in range(0, 5):
            db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()

    response = client.delete('/transaction/batch', data=json.dumps(dict(
        transaction_ids = [1, 2, 3, 4, 5]
    )))
    with one_account.app_context():
        transactions = StockTransaction.query.all()
        assert len(transactions) == 5

def test_export_empty_transactions(one_account, client):
    response = client.get('/transaction/export')
    csv_string = response.data.decode('utf8').strip()
    assert csv_string == ",".join(StockTransaction.DATA_KEYS)

def test_export_one_transaction(one_account, client):
    expected_row = []
    with one_account.app_context():
        stock_1 = StockTransaction(**stock_transaction_1)
        db.session.add(stock_1)
        db.session.commit()
        stock_fields = dict(stock_1)
        for key in StockTransaction.DATA_KEYS:
            expected_row.append(str(stock_fields[key]))

    response = client.get('/transaction/export')
    csv_rows = response.data.decode('utf8').strip().split('\r\n')
    assert len(csv_rows) == 2
    assert csv_rows[0] == ",".join(StockTransaction.DATA_KEYS)
    assert csv_rows[1] == ",".join(expected_row)
