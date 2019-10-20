from flask_login import login_required, current_user
from decimal import Decimal
import json
import logging
import traceback
from flask import Blueprint, jsonify, request
from flaskr import db, apply_user_id
from flaskr.model import InvestmentAccount, StockTransaction
from sqlalchemy import func


investment_accounts = Blueprint('investment_account_bp',
                                __name__,
                                url_prefix="/investment_account")

@investment_accounts.route('/<int:id>', methods=['GET'])
@login_required
def get_investment_account(id):
    investment_account = db.session.query(InvestmentAccount) \
        .filter((InvestmentAccount.id == id) & \
                (InvestmentAccount.user_id == current_user.id)) \
        .one_or_none()
    if investment_account is None:
        return jsonify(None)
    else:
        return jsonify(dict(investment_account))

@investment_accounts.route('/all', methods=['GET'])
@login_required
def get_all_investment_accounts():
    investment_accounts = db.session.query(InvestmentAccount) \
        .filter(InvestmentAccount.user_id == current_user.id) \
        .all()
    return jsonify(list(map(dict, investment_accounts)))

@investment_accounts.route('/transactions', methods=['GET'])
@login_required
def get_investment_account_transactions():
    id = request.args.get('account_id')
    transactions = db.session.query(StockTransaction) \
        .filter((StockTransaction.user_id == current_user.id) & \
                (StockTransaction.account_id == id)) \
        .all()
    return jsonify(list(map(dict, transactions)))

@investment_accounts.route('', methods=['POST'])
@login_required
def create_investment_account():
    try:
        json_data = apply_user_id(json.loads(request.data))
        if 'id' in json_data:
            del json_data['id']
        investment_account = InvestmentAccount(**json_data)
        db.session.add(investment_account)
        db.session.commit()
        return jsonify(dict(investment_account))
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)

@investment_accounts.route('/<int:id>', methods=['PUT'])
@login_required
def update_investment_account(id):
    try:
        json_data = apply_user_id(json.loads(request.data))
        if 'id' in json_data:
            del json_data['id']
        investment_account = InvestmentAccount(**json_data)
        db.session.query(InvestmentAccount) \
            .filter((InvestmentAccount.id == id) & \
                    (InvestmentAccount.user_id == current_user.id)) \
            .update(json_data)
        db.session.commit()
        return jsonify(json_data)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)


@investment_accounts.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_investment_account(id):
    try:
        db.session.query(StockTransaction) \
            .filter((StockTransaction.account_id == id) & \
                    (StockTransaction.user_id == current_user.id)) \
            .delete()
        db.session.query(InvestmentAccount) \
            .filter((InvestmentAccount.id == id) & \
                    (InvestmentAccount.user_id == current_user.id)) \
            .delete()
        db.session.commit()
        return jsonify(None)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        return jsonify(None)

@investment_accounts.route('/<int:id>/stats', methods=['GET'])
@login_required
def get_investment_account_stats(id):
    return jsonify(dict(
        book_cost = get_book_cost(id)
    ))

def get_book_cost(id):
    book_cost = db.session.query(
        func.sum(StockTransaction.cost_per_unit * StockTransaction.quantity + \
                 StockTransaction.trade_fee) \
            .filter((StockTransaction.account_id == id) & \
                    (StockTransaction.user_id == current_user.id)) \
    ).scalar()
    if book_cost is None:
        return "N/A"
    return "$%s" % str(Decimal(book_cost) / 100)

