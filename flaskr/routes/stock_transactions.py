from decimal import Decimal
from flask_login import login_required, current_user
import csv
import io
import json
import logging
import traceback
from flask import Blueprint, jsonify, request
from flaskr import db
from flaskr.model import (
    StockTransaction,
    StockTransactionType
)


stock_transactions = Blueprint('stock_transaction_bp', __name__, url_prefix="/transaction")

@stock_transactions.route('/<int:id>', methods=['GET'])
@login_required
def get_transaction(id):
    stock_transaction = db.session.query(StockTransaction) \
            .filter((StockTransaction.id == id) & \
                    (StockTransaction.user_id == current_user.id)) \
            .one_or_none()
    if stock_transaction is None:
        return jsonify(None)
    else:
        return jsonify(dict(stock_transaction))

@stock_transactions.route('/all', methods=['GET'])
@login_required
def get_all_transaction():
    stock_transactions = db.session.query(StockTransaction) \
            .filter(StockTransaction.user_id == current_user.id) \
            .all()
    return jsonify(list(map(dict, stock_transactions)))

@stock_transactions.route('/', methods=['POST'])
@login_required
def create_transaction():
    try:
        json_data = json.loads(request.data)
        if 'id' in json_data:
            del json_data['id']
        transaction = StockTransaction(**StockTransaction.deserialize(json_data))
        db.session.add(transaction)
        db.session.commit()
        return jsonify(dict(transaction))
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)

@stock_transactions.route('/<int:id>', methods=['PUT'])
@login_required
def update_transaction(id):
    try:
        json_data = json.loads(request.data)
        update_data = StockTransaction.deserialize(json_data)
        update_data['id'] = id
        db.session.query(StockTransaction) \
            .filter((StockTransaction.id == id) & \
                    (StockTransaction.user_id == current_user.id)) \
            .update(update_data)
        db.session.commit()
        return jsonify(StockTransaction.serialize(update_data))
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)

@stock_transactions.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_transaction(id):
    try:
        db.session.query(StockTransaction) \
            .filter((StockTransaction.id == id) & \
                    (StockTransaction.user_id == current_user.id)) \
            .delete()
        db.session.commit()
        return jsonify(None)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)

@stock_transactions.route('/batch', methods=['POST'])
@login_required
def batch_create_transaction():
    try:
        if 'file' not in request.files:
            return ''
        account_id = None
        if 'account_id' in request.form:
            account_id = int(request.form['account_id'])
        csv_file = request.files['file']
        stream = io.StringIO(csv_file.stream.read().decode("utf8"),
                             newline=None)
        csv_iterator = csv.reader(stream)

        keys = StockTransaction.DATA_KEYS
        col_keys = csv_iterator.__next__()
        key_index_map = {}
        for index, col_key in enumerate(col_keys):
            if col_key in keys:
                key_index_map[col_key] = index
        transactions = []
        for row in csv_iterator:
            row_data = {}
            for key, index in key_index_map.items():
                value = row[index]
                row_data[key] = value
            row_data['account_id'] = account_id
            transactions.append(StockTransaction(
                **StockTransaction.deserialize(row_data)
            ))

        db.session.bulk_save_objects(transactions)
        db.session.commit()
        return ''
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return ''
