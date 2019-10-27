from datetime import date
import pytest
from flaskr import db, generate_markers
from flaskr.model import (
    StockMarker,
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
            StockMarker.query.delete()
            StockTransaction.query.delete()
            db.session.commit()

def test_generate_markers_empty(stock_transaction_setup, client):
    app = stock_transaction_setup
    runner = app.test_cli_runner()
    runner.invoke(generate_markers)
    with app.app_context():
        markers = StockMarker.query.all()
        assert len(markers) == 1
        assert markers[0].stock_symbol == "VCN.TO"
        assert markers[0].exists == None

def test_generate_markers_existing(stock_transaction_setup, client):
    app = stock_transaction_setup
    with app.app_context():
        db.session.add(StockMarker(stock_symbol="VCN.TO", exists=True))
        db.session.commit()

    runner = app.test_cli_runner()
    runner.invoke(generate_markers)
    with app.app_context():
        markers = StockMarker.query.all()
        assert len(markers) == 1
        assert markers[0].stock_symbol == "VCN.TO"
        assert markers[0].exists == True

def test_generate_markers_partial_existing(stock_transaction_setup, client):
    app = stock_transaction_setup
    with app.app_context():
        db.session.add(StockMarker(stock_symbol="VCN.TO", exists=True))
        db.session.add(StockTransaction(**stock_transaction_2))
        db.session.commit()

    runner = app.test_cli_runner()
    runner.invoke(generate_markers)
    with app.app_context():
        markers = StockMarker.query.all()
        assert len(markers) == 2
        marker_map = dict()
        for marker in markers:
            marker_map[marker.stock_symbol] = marker.exists
        assert "VCN.TO" in marker_map
        assert "VAB.TO" in marker_map
        assert marker_map["VCN.TO"] == True
        assert marker_map["VAB.TO"] is None

def test_generate_markers_multiple_same(stock_transaction_setup, client):
    app = stock_transaction_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_1))
        db.session.commit()

    runner = app.test_cli_runner()
    runner.invoke(generate_markers)
    with app.app_context():
        markers = StockMarker.query.all()
        assert len(markers) == 1
        assert markers[0].stock_symbol == "VCN.TO"
        assert markers[0].exists == None

def test_generate_markers_multiple_different(stock_transaction_setup, client):
    app = stock_transaction_setup
    with app.app_context():
        db.session.add(StockTransaction(**stock_transaction_2))
        db.session.add(StockTransaction(**stock_transaction_3))
        db.session.commit()

    runner = app.test_cli_runner()
    runner.invoke(generate_markers)
    with app.app_context():
        markers = StockMarker.query.all()
        assert len(markers) == 3
        symbols = set(map(lambda x: x.stock_symbol, markers))
        assert "VCN.TO" in symbols
        assert "VAB.TO" in symbols
        assert "ZPR.TO" in symbols
