from flaskr import create_app, db
from flaskr.model import (
    User,
    StockMarker,
    StockPrice,
    StockTransactionType,
    StockTransaction,
    InvestmentAccount
)

app = create_app(None)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'StockMarker': StockMarker,
        'StockPrice': StockPrice,
        'StockTransaction': StockTransaction,
        'StockTransactionType': StockTransactionType,
        'InvestmentAccount': InvestmentAccount
    }
