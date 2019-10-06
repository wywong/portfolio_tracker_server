from flaskr import create_app

def test_config(client):
    assert not create_app().testing
    assert create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': \
            'postgresql+psycopg2://postgres@localhost:5432/portfoliotest',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }).testing
