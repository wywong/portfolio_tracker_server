from flask_login import login_required, current_user
import json
import logging
import traceback
from flask import Blueprint, jsonify, request
from flaskr import db, apply_user_id
from flaskr.generators.adjust_cost_base import AdjustCostBaseGenerator
from flaskr.generators.book_cost import BookCostGenerator
from flaskr.generators.market_value import MarketValueGenerator
from flaskr.model import (
    InvestmentAccount,
    StockTransaction
)
from sqlalchemy import func


investment_accounts = Blueprint('investment_account_bp',
                                __name__,
                                url_prefix="/investment_account")

@investment_accounts.route('/<int:id>', methods=['GET'])
@login_required
def get_investment_account(id):
    """
    Returns json with the data for the specified investment account

    Keyword arguments:
    id -- the id of the investment account
    """
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
    """
    Returns an array of all investment accounts belonging to the current user
    """
    investment_accounts = db.session.query(InvestmentAccount) \
        .filter(InvestmentAccount.user_id == current_user.id) \
        .all()
    return jsonify(list(map(dict, investment_accounts)))

@investment_accounts.route('/transactions', methods=['GET'])
@login_required
def get_investment_account_transactions():
    """
    Returns the stock transactions that belong to the investment account with id
    account_id
    """
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
    """
    Updates the values of the investment account with the values provided in
    request data
    """
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
    """
    Deletes the investment account with the provided id
    """
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
    """
    Returns a json object with stat values for the investment account
    """
    return jsonify(dict(
        book_cost = BookCostGenerator(current_user.id, id).next(),
        market_value = MarketValueGenerator(current_user.id, id).next()
    ))

@investment_accounts.route('/<int:id>/acb', methods=['GET'])
@login_required
def get_investment_account_acb(id):
    """
    Returns an object with adjusted cost base values for the investment account
    """
    return jsonify(dict(
        adjust_cost_base = AdjustCostBaseGenerator(current_user.id, id).next()
    ))
