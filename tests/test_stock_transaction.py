import json
import pytest
from flaskr import db
from flaskr.model import StockTransaction, StockTransactionType


stock_transaction_1 = dict(
    id = 1,
    transaction_type = StockTransactionType.buy,
    stock_symbol = "VCN.TO",
    cost_per_unit = 3141,
    quantity = 100,
    trade_fee = 999,
    account_id = None
)

def test_get_non_existing_transaction(client):
    response = client.get('/transaction/999')
    assert response.data == b'null\n'

def test_get_existing_transaction(app, client):
    try:
        with app.app_context():
            data_dict = stock_transaction_1.copy()
            db.session.add(StockTransaction(**data_dict))
            db.session.commit()
        response = client.get('/transaction/1')
        json_data = json.loads(response.data)
        assert json_data['id'] == 1
        assert json_data['transaction_type'] == 0
        assert json_data['stock_symbol'] == 'VCN.TO'
        assert json_data['cost_per_unit'] == 3141
        assert json_data['quantity'] == 100
        assert json_data['trade_fee'] == 999
    except Exception as e:
        assert False
    finally:
        with app.app_context():
            StockTransaction.query.delete()
            db.session.commit()

def test_create_transaction(app, client):
    response = client.post('/transaction/', data=json.dumps(dict(
        transaction_type = 1,
        stock_symbol = "XAW.TO",
        cost_per_unit = 2718,
        quantity = 200,
        trade_fee = 999,
        account_id = None
    )))
    json_data = json.loads(response.data)
    assert json_data['transaction_type'] == 1
    assert json_data['stock_symbol'] == 'XAW.TO'
    assert json_data['cost_per_unit'] == 2718
    assert json_data['quantity'] == 200
    assert json_data['trade_fee'] == 999

def test_create_transaction_bad(app, client):
    response = client.post('/transaction/', data=json.dumps(dict(
        transaction_type = 1,
        stock_symbol = "XAW.TO",
        cost_per_unit = "asdf",
        quantity = 200,
        trade_fee = 999,
        account_id = None
    )))
    assert json.loads(response.data) == None

def test_update_transaction(app, client):
    try:
        with app.app_context():
            db.session.add(StockTransaction(**stock_transaction_1))
            db.session.commit()

        data_dict = stock_transaction_1.copy()
        data_dict['id'] = 1
        data_dict['transaction_type'] = data_dict['transaction_type'].value
        data_dict['quantity'] = 123
        response = client.put('/transaction/1', data=json.dumps(
            data_dict
        ))
        with app.app_context():
            transaction = StockTransaction.query.get(1)
            assert transaction.quantity == 123
            StockTransaction.query.delete()
            db.session.commit()
    except Exception as e:
        assert False
    finally:
        with app.app_context():
            StockTransaction.query.delete()
            db.session.commit()

def test_update_transaction_bad(app, client):
    try:
        with app.app_context():
            db.session.add(StockTransaction(**stock_transaction_1))
            db.session.commit()

        data_dict = stock_transaction_1.copy()
        data_dict['transaction_type'] = data_dict['transaction_type'].value
        data_dict['trade_fee'] = 'bad input'
        data_dict['quantity'] = 123
        response = client.post('/transaction/', data=json.dumps(
            data_dict
        ))
        with app.app_context():
            transaction = StockTransaction.query.get(1)
            assert transaction.quantity == 100
    except Exception as e:
        assert False
    finally:
        with app.app_context():
            StockTransaction.query.delete()
            db.session.commit()

def test_delete_transaction(app, client):
    try:
        with app.app_context():
            db.session.add(StockTransaction(**stock_transaction_1))
            db.session.commit()

        client.delete('transaction/1')
        with app.app_context():
            transaction = StockTransaction.query.get(1)
            assert transaction == None
    except Exception as e:
        assert False
    finally:
        with app.app_context():
            StockTransaction.query.delete()
            db.session.commit()
