import json
import logging
import traceback
from flask import Blueprint, jsonify, request
from flaskr import db
from flaskr.model import StockTransaction, StockTransactionType

stock_transactions = Blueprint('stock_transaction_bp', __name__, url_prefix="/transaction")

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
        transaction = StockTransaction(**deserialize_transaction(json_data))
        db.session.add(transaction)
        db.session.commit()
        return jsonify(dict(transaction))
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)


@stock_transactions.route('/<int:id>', methods=['PUT'])
def update_transaction(id):
    try:
        json_data = json.loads(request.data)
        update_data = deserialize_transaction(json_data)
        if 'id' in update_data:
            del update_data['id']
        db.session.query(StockTransaction) \
            .filter(StockTransaction.id == id) \
            .update(update_data)
        db.session.commit()
        return jsonify(json_data)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)

def deserialize_transaction(data):
    json_data = data.copy()
    transaction_type = StockTransactionType(json_data['transaction_type'])
    json_data['transaction_type'] = transaction_type
    return json_data

@stock_transactions.route('/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    try:
        db.session.query(StockTransaction) \
            .filter(StockTransaction.id == id) \
            .delete()
        db.session.commit()
        return jsonify(None)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)
