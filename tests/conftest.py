import os
import tempfile
import pytest
from flask_login import login_user
from flaskr import create_app, db
from flaskr.model import User


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'LOGIN_DISABLED': True,
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
def runner(app):
    return app.test_cli_runner()
