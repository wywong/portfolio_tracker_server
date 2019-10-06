
from flask import Blueprint, jsonify
from flaskr import db
from flaskr.model import StockTransaction

stock_transactions = Blueprint('main', __name__, url_prefix="/transaction")

@stock_transactions.route('/<int:id>')
def transaction(id):
    return jsonify(dict(StockTransaction.query.get(id)))
