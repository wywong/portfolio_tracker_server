import flask
import json
import pytest
from flaskr import db
from flaskr.model import User

some_user_email = "bob@mathematicianlineage.com"
totally_secure_password = "correct horse battery staple"

@pytest.fixture
def auth_setup(app):
    try:
        with app.app_context():
            user = User(email=some_user_email, password_hash="")
            user.set_password(totally_secure_password)
            db.session.add(user)
            db.session.commit()
        yield app
    except Exception as e:
        assert False
    finally:
        with app.app_context():
            User.query.delete()
            db.session.commit()


def test_login_success(auth_setup, client):
    response = client.post(
        '/auth/login',
        data=dict(
            email = some_user_email,
            password = totally_secure_password
        ),
        follow_redirects=True
    )
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert int(sess['user_id']) == 1

def test_login_fail(auth_setup, client):
    response = client.post(
        '/auth/login',
        data=dict(
            email = some_user_email,
            password = "Bad pass"
        ),
        follow_redirects=True
    )
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert 'user_id' not in sess.keys()
