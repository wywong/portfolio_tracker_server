from flaskr import create_app, db
from flaskr.model import (
    User, StockTransactionType, StockTransaction, InvestmentAccount
)

app = create_app(None)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'StockTransaction': StockTransaction,
        'StockTransactionType': StockTransactionType,
        'InvestmentAccount': InvestmentAccount
    }
