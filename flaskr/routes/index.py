from flask_login import current_user
from flask import Blueprint, redirect, url_for

index_bp = Blueprint('index_bp', __name__, url_prefix="/")

@index_bp.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_bp.login'))
    else:
        return redirect('/app', code=302)
