import os
import tempfile

import pytest
from flaskr import create_app, db

@pytest.fixture
def app():

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': \
            'postgresql+psycopg2://postgres@localhost:5432/portfoliotest',
        'SQLALCHEMY_ECHO':  True,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    print(app.config)

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
