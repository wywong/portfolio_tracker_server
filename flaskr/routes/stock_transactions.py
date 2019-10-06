
from flask import Blueprint, jsonify
from flaskr import db
from flaskr.model import StockTransaction

stock_transactions = Blueprint('main', __name__, url_prefix="/transaction")

@stock_transactions.route('/<int:id>')
def transaction(id):
    stock_transaction = StockTransaction.query.get(id)
    if stock_transaction is None:
        return jsonify(None)
    else:
        return jsonify(dict(stock_transaction))
