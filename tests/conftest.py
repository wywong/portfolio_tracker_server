import os
import tempfile
import pytest
from flaskr import create_app, db, login_manager
from flaskr.model import User


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'dev',
        'SQLALCHEMY_DATABASE_URI': \
            'postgresql+psycopg2://postgres@localhost:5432/portfoliotest',
        # 'SQLALCHEMY_ECHO':  True,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_app_base(app):
    with app.app_context():
        user1 = User(
            email="newton@mathematicianlineage.com",
            password_hash=""
        )
        user2 = User(email="leibnitz@mathematicianlineage.com",
                     password_hash="")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        yield app

@pytest.fixture
def auth_app_user_1(auth_app_base):
    app = auth_app_base
    @app.login_manager.request_loader
    def load_user_from_request(request):
        return User.query.get(1)
    yield app

@pytest.fixture
def auth_app_user_2(auth_app_base):
    app = auth_app_base
    @app.login_manager.request_loader
    def load_user_from_request(request):
        return User.query.get(2)
    yield app

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
