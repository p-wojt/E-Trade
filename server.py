from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from model import db
from utils import any_empty, correct_email, more_than
from query import create_user, is_user_exists, get_user_by_id
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests

app = Flask(__name__)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        email = request.form.get('email')

        if correct_email(email) is False:
            flash('Yours e-mail is not correct!')
            return render_template('register.html')

        if is_user_exists(email):
            flash('User with this email already exists!')
            return render_template('register.html')

        name = request.form.get('name')
        surname = request.form.get('surname')
        password = request.form.get('password')

        if any_empty(name, surname, password):
            flash('All fields must be completed!')
            return render_template('register.html')

        if more_than(password, length=6) is False:
            flash('Password must have more than 5 characters!')
            return render_template('register.html')

        create_user(name, surname, email, password)
        flash('You account has been created successfully!')
        return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('email')

        if correct_email(email) is False:
            flash('Yours e-mail is not correct!')
            return render_template('login.html')

        password = request.form.get('password')

        if any_empty(password):
            flash('All fields must be completed!')
            return render_template('login.html')

        user = is_user_exists(email)

        if user is None:
            flash('User with this email does not exists!')
            return render_template('login.html')

        print(user.password)
        print(password)
        print(check_password_hash(user.password, password))
        if check_password_hash(user.password, password):
            login_user(user)
            flash('You have been logged in')
            return redirect(url_for('profile'))
        else:
            flash('Password is not correct!')
            return render_template('login.html')


@app.route('/logout/')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out')
    else:
        flash('You have to be logged in to log out')
    return redirect(url_for('index'))


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == 'GET':
        return render_template('profile.html', user=current_user)


@app.route('/trade', methods=['POST', 'GET'])
@login_required
def trade():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        return render_template('trade.html', crypto=response.json())


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'mZq4t7w!z$C&F)J@'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    db.create_all(app=app)

    app.run()
