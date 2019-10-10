from flask_login import current_user, login_user
from flaskr import db
from flaskr.model import User
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


auth_bp = Blueprint('auth_bp', __name__, url_prefix="/auth")


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me", default = False)
    submit = SubmitField("Login")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_bp.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth_bp.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index_bp.index'))
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    email = StringField('email', validators=[
        DataRequired(),
        Email(),
        Length(min=4, max=128),
    ])
    password = PasswordField('password', validators=[
        DataRequired(),
        Length(min=8, max=128),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('repeat password')
    submit = SubmitField("Register")


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password_hash="")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('auth_bp.login'))
    return render_template('register.html', form=form)
