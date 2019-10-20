from datetime import date
import json
import pytest
from flaskr import db
from flaskr.model import (
    StockTransaction,
    StockTransactionType
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

stock_transaction_2 = dict(
    transaction_type = StockTransactionType.buy,
    stock_symbol = "VAB.TO",
    cost_per_unit = 2601,
    quantity = 200,
    trade_fee = 999,
    trade_date = date(2016, 8, 23),
    account_id = None,
    user_id = 1
)

stock_transaction_3 = dict(
    transaction_type = StockTransactionType.buy,
    stock_symbol = "ZPR.TO",
    cost_per_unit = 992,
    quantity = 500,
    trade_fee = 999,
    trade_date = date(2016, 12, 9),
    account_id = None,
    user_id = 2
)

@pytest.fixture
def stock_transaction_setup(auth_app_user_1):
    auth_app = auth_app_user_1
    try:
        with auth_app.app_context():
            db.session.add(StockTransaction(**stock_transaction_1))
            db.session.commit()
        yield auth_app
    except Exception as e:
        assert False
    finally:
        with auth_app.app_context():
            StockTransaction.query.delete()
            db.session.commit()

def test_get_non_existing_transaction(auth_app_user_1, client):
    response = client.get('/transaction/999')
    assert response.data == b'null\n'

def test_get_existing_transaction(stock_transaction_setup, client):
    response = client.get('/transaction/1')
    json_data = json.loads(response.data)
    assert json_data['id'] == 1
    assert json_data['transaction_type'] == 'buy'
    assert json_data['stock_symbol'] == 'VCN.TO'
    assert json_data['cost_per_unit'] == "31.41"
    assert json_data['quantity'] == 100
    assert json_data['trade_fee'] == "9.99"

def test_get_transaction_other_user(stock_transaction_setup, auth_app_user_2, client):
    response = client.get('/transaction/1')
    assert response.data == b'null\n'

def test_get_all_transactions(stock_transaction_setup, client):
    with stock_transaction_setup.app_context():
        db.session.add(StockTransaction(**stock_transaction_2))
        db.session.add(StockTransaction(**stock_transaction_3))
        db.session.commit()
    response = client.get('/transaction/all')
    json_data = json.loads(response.data)
    assert len(json_data) == 2

def test_get_all_transactions(stock_transaction_setup, auth_app_user_2, client):
    with stock_transaction_setup.app_context():
        db.session.add(StockTransaction(**stock_transaction_2))
        db.session.add(StockTransaction(**stock_transaction_3))
        db.session.commit()
    response = client.get('/transaction/all')
    json_data = json.loads(response.data)
    assert len(json_data) == 1


def test_create_transaction(stock_transaction_setup, client):
    response = client.post('/transaction/', data=json.dumps(dict(
        transaction_type = 'sell',
        stock_symbol = "XAW.TO",
        cost_per_unit = "27.18",
        quantity = 200,
        trade_fee = "9.99",
        trade_date = date(2016, 11, 11).isoformat(),
        account_id = None,
        user_id = 1
    )))
    json_data = json.loads(response.data)
    assert json_data['transaction_type'] == 'sell'
    assert json_data['stock_symbol'] == 'XAW.TO'
    assert json_data['cost_per_unit'] == "27.18"
    assert json_data['quantity'] == 200
    assert json_data['trade_fee'] == "9.99"

def test_create_transaction_bad(stock_transaction_setup, client):
    response = client.post('/transaction/', data=json.dumps(dict(
        transaction_type = 'sell',
        stock_symbol = "XAW.TO",
        cost_per_unit = "asdf",
        quantity = 200,
        trade_fee = "9.99",
        trade_date = date(2016, 11, 11).isoformat(),
        account_id = None,
        user_id = 1
    )))
    assert json.loads(response.data) == None

def test_create_transaction_other_user(stock_transaction_setup,
                                       auth_app_user_2,
                                       client):
    request_data = dict(
        transaction_type = 'sell',
        stock_symbol = "XAW.TO",
        cost_per_unit = "27.18",
        quantity = 200,
        trade_fee = "9.99",
        trade_date = date(2016, 11, 11).isoformat(),
        account_id = None,
        user_id = 1
    )
    response = client.post('/transaction/', data=json.dumps(request_data))
    json_data = json.loads(response.data)
    for k, v in json_data.items():
        if k == 'id':
            continue
        if k == 'trade_date':
            v = date.fromisoformat(v)
            continue
        assert v == request_data[k]

def test_update_transaction(stock_transaction_setup, client):
    data_dict = stock_transaction_1.copy()
    data_dict['id'] = 1
    data_dict['transaction_type'] = data_dict['transaction_type'].name
    data_dict['trade_date'] = data_dict['trade_date'].isoformat()
    data_dict['quantity'] = 123
    response = client.put('/transaction/1', data=json.dumps(
        data_dict
    ))
    with stock_transaction_setup.app_context():
        transaction = StockTransaction.query.get(1)
        assert transaction.quantity == 123

def test_update_transaction_other_user(stock_transaction_setup, auth_app_user_2, client):
    data_dict = stock_transaction_1.copy()
    data_dict['id'] = 1
    data_dict['transaction_type'] = data_dict['transaction_type'].name
    data_dict['trade_date'] = data_dict['trade_date'].isoformat()
    data_dict['quantity'] = 123
    response = client.put('/transaction/1', data=json.dumps(
        data_dict
    ))
    with stock_transaction_setup.app_context():
        transaction = StockTransaction.query.get(1)
        assert transaction.quantity == stock_transaction_1['quantity']

def test_update_transaction_bad(stock_transaction_setup, client):
    data_dict = stock_transaction_1.copy()
    data_dict['transaction_type'] = data_dict['transaction_type'].name
    data_dict['trade_fee'] = 'bad input'
    data_dict['trade_date'] = data_dict['trade_date'].isoformat()
    data_dict['quantity'] = 123
    response = client.post('/transaction/', data=json.dumps(
        data_dict
    ))
    with stock_transaction_setup.app_context():
        transaction = StockTransaction.query.get(1)
        assert transaction.quantity == 100

def test_delete_transaction(stock_transaction_setup, client):
    client.delete('/transaction/1')
    with stock_transaction_setup.app_context():
        transaction = StockTransaction.query.get(1)
        assert transaction == None

def test_delete_transaction_other_user(stock_transaction_setup, auth_app_user_2, client):
    client.delete('/transaction/1')
    with stock_transaction_setup.app_context():
        transaction = StockTransaction.query.get(1)
        assert transaction is not None
