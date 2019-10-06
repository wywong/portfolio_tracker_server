import json
import pytest
from flaskr import db
from flaskr.model import StockTransaction, StockTransactionType


def test_get_non_existing_transaction(client):
    response = client.get('/transaction/999')
    assert response.data == b'null\n'

def test_get_existing_transaction(app, client):
    with app.app_context():
        db.session.add(StockTransaction(
            id = 1,
            transaction_type = StockTransactionType.buy,
            stock_symbol = "VCN.TO",
            cost_per_unit = 3141,
            quantity = 100,
            trade_fee = 999,
            account_id = None
        ))
        db.session.commit()
    response = client.get('/transaction/1')
    json_data = json.loads(response.data)
    assert json_data['id'] == 1
    assert json_data['transaction_type'] == 0
    assert json_data['stock_symbol'] == 'VCN.TO'
    assert json_data['cost_per_unit'] == 3141
    assert json_data['quantity'] == 100
    assert json_data['trade_fee'] == 999
    with app.app_context():
        StockTransaction.query.filter_by(id=1).delete()
        db.session.commit()
