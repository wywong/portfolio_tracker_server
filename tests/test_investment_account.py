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

investment_account_2 = dict(
    name = "Taxable",
    taxable = True,
    user_id = 1
)

investment_account_3 = dict(
    name = "RRSP",
    taxable = False,
    user_id = 2
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
            InvestmentAccount.query.delete()
            db.session.commit()

def test_get_non_existing_account(auth_app_user_1, client):
    response = client.get('/investment_account/999')
    assert response.data == b'null\n'

def test_get_existing_account(investment_account_setup, client):
    response = client.get('/investment_account/1')
    json_data = json.loads(response.data)
    for k, v in json_data.items():
        if k == 'id':
            continue
        assert v == json_data[k]
    assert json_data['id'] == 1

def test_get_existing_account(investment_account_setup, client):
    with investment_account_setup.app_context():
        db.session.add(InvestmentAccount(**investment_account_2))
        db.session.add(InvestmentAccount(**investment_account_3))
        db.session.commit()
    response = client.get('/investment_account/all')
    accounts = json.loads(response.data)
    assert len(accounts) == 2

def test_create_account(investment_account_setup, client):
    request_data = dict(
        name = "Magical Taxable Account",
        taxable = True,
        user_id = 1
    )
    response = client.post('/investment_account', data=json.dumps(request_data))
    json_data = json.loads(response.data)
    for k, v in json_data.items():
        if k == 'id':
            continue
        assert v == request_data[k]
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(2)
        assert account.name == request_data['name']
        assert account.taxable == request_data['taxable']
        assert account.user_id == request_data['user_id']

def test_create_account_bad(investment_account_setup, client):
    request_data = dict(
        name = "Magical Taxable Account",
        taxable = None,
        user_id = 1
    )
    response = client.post('/investment_account', data=json.dumps(request_data))
    json_data = json.loads(response.data)
    assert json_data == None
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(2)
        assert account == None

def test_create_account_other_user(investment_account_setup, auth_app_user_2, client):
    request_data = dict(
        name = "Magical Taxable Account",
        taxable = True,
        user_id = 1
    )
    response = client.post('/investment_account', data=json.dumps(request_data))
    json_data = json.loads(response.data)
    for k, v in json_data.items():
        if k == 'id':
            continue
        assert v == request_data[k]
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(2)
        assert account.name == request_data['name']
        assert account.taxable == request_data['taxable']
        assert account.user_id == 2

def test_update_account(investment_account_setup, client):
    request_data = investment_account_1.copy()
    request_data['name'] = 'Mathematical Investments'
    response = client.put('/investment_account/1',
                          data=json.dumps(request_data))
    json_data = json.loads(response.data)
    assert request_data['name'] == json_data['name']
    assert request_data['taxable'] == json_data['taxable']
    assert request_data['user_id'] == json_data['user_id']
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(1)
        assert request_data['name'] == account.name
        assert request_data['taxable'] == account.taxable
        assert request_data['user_id'] == account.user_id

def test_update_account_bad(investment_account_setup, client):
    request_data = investment_account_1.copy()
    request_data['name'] = 'Mathematical Investments'
    request_data['taxable'] = None
    response = client.put('/investment_account/1',
                          data=json.dumps(request_data))
    json_data = json.loads(response.data)
    assert json_data == None
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(1)
        assert investment_account_1['name'] == account.name
        assert investment_account_1['taxable'] == account.taxable
        assert investment_account_1['user_id'] == account.user_id

def test_update_account_other_user(investment_account_setup, auth_app_user_2, client):
    request_data = investment_account_1.copy()
    request_data['name'] = 'Mathematical Investments'
    response = client.put('/investment_account/1',
                          data=json.dumps(request_data))
    json_data = json.loads(response.data)
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(1)
        assert investment_account_1['name'] == account.name
        assert investment_account_1['taxable'] == account.taxable
        assert investment_account_1['user_id'] == account.user_id

def test_delete_account(investment_account_setup, client):
    response = client.delete('/investment_account/1')
    assert json.loads(response.data) == None
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(1)
        assert account == None

def test_delete_account_non_existent(investment_account_setup, client):
    response = client.delete('/investment_account/999')
    assert json.loads(response.data) == None
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(1)
        assert account is not None

def test_delete_account_other_user(investment_account_setup,
                                   auth_app_user_2,
                                   client):
    response = client.delete('/investment_account/1')
    assert json.loads(response.data) == None
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(1)
        assert account is not None

def test_delete_account_with_transactions(investment_account_setup, client):
    with investment_account_setup.app_context():
        db.session.add(StockTransaction(
            transaction_type = StockTransactionType.buy,
            stock_symbol = "XAW.TO",
            cost_per_unit = 2612,
            quantity = 600,
            trade_fee = 995,
            account_id = 1,
            user_id = 1
        ))
        db.session.commit()
    response = client.delete('/investment_account/1')
    assert json.loads(response.data) == None
    with investment_account_setup.app_context():
        account = InvestmentAccount.query.get(1)
        assert account == None
        transaction = StockTransaction.query.get(1)
        assert transaction is None
        StockTransaction.query.delete()
