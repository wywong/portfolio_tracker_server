import os

from flask import Flask
from flask.cli import with_appcontext, AppGroup
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
import click
import logging
import traceback


db = SQLAlchemy()
login_manager = LoginManager()
stock_cli = AppGroup("stock")

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    try:
        import flaskr.model
        if test_config is None:
            # load the instance config, if it exists, when not testing
            config_file = os.environ['PORTFOLIO_CONFIG_FILE']
            app.config.from_pyfile(config_file, silent=True)

        else:
            # load the test config if passed in
            app.config.from_mapping(test_config)
        db.init_app(app)
        app.url_map.strict_slashes = False

        # add command line commands
        migrate = Migrate(app, db)
        app.cli.add_command(migrate_command)
        app.cli.add_command(stock_cli)

        # register routes
        from flaskr.routes.investment_accounts import investment_accounts
        app.register_blueprint(investment_accounts)
        from flaskr.routes.stock_transactions import stock_transactions
        app.register_blueprint(stock_transactions)
        from flaskr.routes.auth import auth_bp
        app.register_blueprint(auth_bp)
        from flaskr.routes.index import index_bp
        app.register_blueprint(index_bp)
    except Exception as e:
        logging.error(e)
    login_manager.init_app(app)

    return app

def apply_user_id(data):
    data['user_id'] = int(current_user.get_id())
    return data

@click.command("db")
@with_appcontext
def migrate_command():
    MigrateCommand()

@stock_cli.command("generate")
@with_appcontext
def generate_markers():
    """
    Creates new StockMarker entries for stocks in StockTransaction's table that
    do not have an existing StockMarker
    """
    try:
        from flaskr.model import StockTransaction, StockMarker
        from sqlalchemy import func
        stock_symbols = db.session.query(
            func.upper(StockTransaction.stock_symbol),
            func.upper(StockMarker.stock_symbol)
        ).outerjoin(StockMarker,
                    func.upper(StockTransaction.stock_symbol) == \
                    func.upper(StockMarker.stock_symbol)) \
            .filter(StockMarker.stock_symbol == None) \
            .distinct()
        db.session.bulk_save_objects([
            StockMarker(stock_symbol=r[0], exists=None) for r in stock_symbols
        ])
        db.session.commit()
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        db.session.rollback()
        raise e

