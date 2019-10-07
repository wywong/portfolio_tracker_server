
import json
from flask import Blueprint, jsonify, request
from flaskr import db
from flaskr.model import StockTransaction, StockTransactionType
import logging

stock_transactions = Blueprint('main', __name__, url_prefix="/transaction")

@stock_transactions.route('/<int:id>', methods=['GET'])
def get_transaction(id):
    stock_transaction = StockTransaction.query.get(id)
    if stock_transaction is None:
        return jsonify(None)
    else:
        return jsonify(dict(stock_transaction))

@stock_transactions.route('/', methods=['POST'])
def create_transaction():
    try:
        json_data = json.loads(request.data)
        transaction_type = StockTransactionType(json_data['transaction_type'])
        json_data['transaction_type'] = transaction_type
        transaction = StockTransaction(**json_data)
        db.session.add(transaction)
        db.session.commit()
        return jsonify(dict(transaction))
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(None)
