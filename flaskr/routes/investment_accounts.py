from flask_login import login_required, current_user
from decimal import Decimal
import json
import logging
import traceback
from flask import Blueprint, jsonify, request
from flaskr import db, apply_user_id
from flaskr.model import (
    InvestmentAccount,
    StockTransaction,
    StockTransactionType,
    StockPrice
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
    Returns a json object with relevant values for the investment account
    """
    return jsonify(dict(
        book_cost = get_book_cost(id),
        market_value = get_investment_account_market_price(id)
    ))

def get_book_cost(id):
    """
    Returns the computed book cost of all transactions in this account, if the
    account has no tranasctions then N/A is returned.
    """
    book_cost = db.session.query(
        func.sum(StockTransaction.cost_per_unit * StockTransaction.quantity + \
                 StockTransaction.trade_fee) \
            .filter((StockTransaction.account_id == id) & \
                    (StockTransaction.user_id == current_user.id)) \
    ).scalar()
    if book_cost is None:
        return "N/A"
    return format_currency(book_cost)

def get_investment_account_market_price(id):
    """
    Returns the market value of all the stocks in the portfolio
    """
    total_value = 0
    breakdown = {}
    stock_values = build_market_price_query(id)
    for row in stock_values:
        logging.error(row)
        value = row[0] * row[1]
        stock_symbol = row[2]
        transaction_type = row[3]
        breakdown.setdefault(stock_symbol, 0)
        if transaction_type == StockTransactionType.buy:
            total_value += value
            breakdown[stock_symbol] += value
        elif transaction_type == StockTransactionType.sell:
            total_value -= value
            breakdown[stock_symbol] -= value

    return dict(
        total = format_currency(total_value),
        breakdown = build_stock_market_values(breakdown, total_value)
    )

def build_market_price_query(id):
    last_date = db.session.query(
        func.max(StockPrice.price_date).label('latest_price_date')
    ).subquery('last_date')
    price_query = db.session.query(
        StockPrice.stock_symbol,
        StockPrice.close_price.label('close_price')
    ).filter(
        StockPrice.price_date == last_date.c.latest_price_date
    ).subquery('price_query')

    return db.session.query(
        func.sum(StockTransaction.quantity),
        func.min(price_query.c.close_price),
        StockTransaction.stock_symbol,
        StockTransaction.transaction_type
    ).filter((StockTransaction.account_id == id) & \
             (StockTransaction.user_id == current_user.id)) \
        .join(price_query, StockTransaction.stock_symbol == \
              price_query.c.stock_symbol) \
        .group_by(StockTransaction.stock_symbol) \
        .group_by(StockTransaction.transaction_type)

def build_stock_market_values(breakdown, total_value):
    values = {}
    for kv in breakdown.items():
        values[kv[0]] = dict(
            formatted_value = format_currency(kv[1]),
            raw_percent = kv[1],
            percent = format_percentage(kv[1], total_value)
        )
    return values

def format_currency(value):
    return "$%s.%02d" % ("{:,}".format(value // 100), value % 100)

def format_percentage(numerator, denominator):
    return "%.1f%%" % (float(numerator) / denominator * 100)
