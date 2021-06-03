from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from model import db
from utils import any_empty, correct_email, more_than, check_buysell_buttons
from query import create_user, is_user_exists, get_user_by_id, get_amount_of_item, make_transaction, find_item, user_transactions, update_user_items_balance
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
        if current_user.is_authenticated:
            return redirect(url_for('index'))

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
        if current_user.is_authenticated:
            return redirect(url_for('index'))

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
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        update_user_items_balance(current_user, response.json())
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

    if request.method == 'POST':
        template_from_button = check_buysell_buttons(request.form)
        if template_from_button is not None:
            return redirect(url_for(template_from_button))
        return render_template('trade.html')


@app.route('/items', methods=['POST', 'GET'])
@login_required
def items():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        user_items = []
        response_json = response.json()

        for item_name in ['bitcoin', 'litecoin', 'ethereum', 'dogecoin']:
            item = find_item(current_user.id, item_name)
            if item is not None:
                user_items.append(
                    [item,
                     float(response_json[item_name]['usd']),
                     float(response_json[item_name]['usd'])*float(item.amount)
                     ]
                )

        return render_template('items.html', all_items=user_items)


@app.route('/transactions', methods=['POST', 'GET'])
@login_required
def transactions():
    if request.method == 'GET':
        return render_template('transactions.html', all_transactions=user_transactions(current_user.id))


@app.route('/buy_bitcoin', methods=['POST', 'GET'])
@login_required
def buy_bitcoin():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        update_user_items_balance(current_user, response.json())

        return render_template('buy_bitcoin.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'bitcoin'),
                               price=response.json()['bitcoin']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount <= 0.0:
            flash('Amount is invalid!')
            return render_template('buy_bitcoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'bitcoin'),
                                   price=response.json()['bitcoin']['usd'])
        else:
            value = float(response.json()['bitcoin']['usd'])
            total_value = float(response.json()['bitcoin']['usd']) * amount

            if float(current_user.balance) < value:
                flash('You don\'t have enough money!')
                return render_template('buy_bitcoin.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'bitcoin'),
                                       price=response.json()['bitcoin']['usd'])
            else:
                update_user_items_balance(current_user, response.json())
                make_transaction('buy', current_user.id, value, total_value, 'bitcoin', amount)
                flash('You\'ve successfully purchased %s BTC for $%s' % (amount, total_value))
                return render_template('buy_bitcoin.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'bitcoin'),
                                       price=response.json()['bitcoin']['usd'])


@app.route('/sell_bitcoin', methods=['POST', 'GET'])
@login_required
def sell_bitcoin():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        update_user_items_balance(current_user, response.json())

        return render_template('sell_bitcoin.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'bitcoin'),
                               price=response.json()['bitcoin']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        user_amount = float(get_amount_of_item(current_user.id, 'bitcoin'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount > user_amount or amount <= 0.0:
            flash('Amount is invalid or you don\'t have enough BTC!')
            return render_template('sell_bitcoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'bitcoin'),
                                   price=response.json()['bitcoin']['usd'])
        else:
            value = float(response.json()['bitcoin']['usd'])
            total_value = float(response.json()['bitcoin']['usd']) * amount
            update_user_items_balance(current_user, response.json())
            make_transaction('sell', current_user.id, value, total_value, 'bitcoin', amount)
            flash('You\'ve successfully sold %s BTC for $%s' % (amount, total_value))
            return render_template('sell_bitcoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'bitcoin'),
                                   price=response.json()['bitcoin']['usd'])


@app.route('/buy_dogecoin', methods=['POST', 'GET'])
@login_required
def buy_dogecoin():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        print(response.json()['dogecoin']['usd'])
        update_user_items_balance(current_user, response.json())

        return render_template('buy_dogecoin.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'dogecoin'),
                               price=response.json()['dogecoin']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount <= 0.0:
            flash('Amount is invalid!')
            return render_template('buy_dogecoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'dogecoin'),
                                   price=response.json()['dogecoin']['usd'])
        else:
            value = float(response.json()['dogecoin']['usd'])
            total_value = float(response.json()['dogecoin']['usd']) * amount

            if float(current_user.balance) < value:
                flash('You don\'t have enough money!')
                return render_template('buy_dogecoin.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'dogecoin'),
                                       price=response.json()['dogecoin']['usd'])
            else:
                update_user_items_balance(current_user, response.json())
                make_transaction('buy', current_user.id, value, total_value, 'dogecoin', amount)
                flash('You\'ve successfully purchased %s DOGE for $%s' % (amount, total_value))
                return render_template('buy_dogecoin.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'dogecoin'),
                                       price=response.json()['dogecoin']['usd'])


@app.route('/sell_dogecoin', methods=['POST', 'GET'])
@login_required
def sell_dogecoin():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        update_user_items_balance(current_user, response.json())

        return render_template('sell_dogecoin.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'dogecoin'),
                               price=response.json()['dogecoin']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        user_amount = float(get_amount_of_item(current_user.id, 'dogecoin'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount > user_amount or amount <= 0.0:
            flash('Amount is invalid or you don\'t have enough DOGE!')
            return render_template('sell_dogecoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'dogecoin'),
                                   price=response.json()['dogecoin']['usd'])
        else:
            value = float(response.json()['dogecoin']['usd'])
            total_value = float(response.json()['dogecoin']['usd']) * amount
            update_user_items_balance(current_user, response.json())
            make_transaction('sell', current_user.id, value, total_value, 'dogecoin', amount)
            flash('You\'ve successfully sold %s DOGE for $%s' % (amount, total_value))
            return render_template('sell_dogecoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'dogecoin'),
                                   price=response.json()['dogecoin']['usd'])


@app.route('/buy_ethereum', methods=['POST', 'GET'])
@login_required
def buy_ethereum():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        update_user_items_balance(current_user, response.json())

        return render_template('buy_ethereum.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'ethereum'),
                               price=response.json()['ethereum']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount <= 0.0:
            flash('Amount is invalid!')
            return render_template('buy_ethereum.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'ethereum'),
                                   price=response.json()['ethereum']['usd'])
        else:
            value = float(response.json()['ethereum']['usd'])
            total_value = float(response.json()['ethereum']['usd']) * amount

            if float(current_user.balance) < value:
                flash('You don\'t have enough money!')
                return render_template('buy_ethereum.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'ethereum'),
                                       price=response.json()['ethereum']['usd'])
            else:
                update_user_items_balance(current_user, response.json())
                make_transaction('buy', current_user.id, value, total_value, 'ethereum', amount)
                flash('You\'ve successfully purchased %s ETH for $%s' % (amount, total_value))
                return render_template('buy_ethereum.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'ethereum'),
                                       price=response.json()['ethereum']['usd'])


@app.route('/sell_ethereum', methods=['POST', 'GET'])
@login_required
def sell_ethereum():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        update_user_items_balance(current_user, response.json())

        return render_template('sell_ethereum.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'ethereum'),
                               price=response.json()['ethereum']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        user_amount = float(get_amount_of_item(current_user.id, 'ethereum'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount > user_amount or amount <= 0.0:
            flash('Amount is invalid or you don\'t have enough ETH!')
            return render_template('sell_ethereum.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'ethereum'),
                                   price=response.json()['ethereum']['usd'])
        else:
            value = float(response.json()['ethereum']['usd'])
            total_value = float(response.json()['ethereum']['usd']) * amount
            update_user_items_balance(current_user, response.json())
            make_transaction('sell', current_user.id, value, total_value, 'ethereum', amount)
            flash('You\'ve successfully sold %s ETH for $%s' % (amount, total_value))
            return render_template('sell_ethereum.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'ethereum'),
                                   price=response.json()['ethereum']['usd'])


@app.route('/buy_litecoin', methods=['POST', 'GET'])
@login_required
def buy_litecoin():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        update_user_items_balance(current_user, response.json())

        return render_template('buy_litecoin.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'litecoin'),
                               price=response.json()['litecoin']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount <= 0.0:
            flash('Amount is invalid!')
            return render_template('buy_litecoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'litecoin'),
                                   price=response.json()['litecoin']['usd'])
        else:
            value = float(response.json()['litecoin']['usd'])
            total_value = float(response.json()['litecoin']['usd']) * amount

            if float(current_user.balance) < value:
                flash('You don\'t have enough money!')
                return render_template('buy_litecoin.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'litecoin'),
                                       price=response.json()['litecoin']['usd'])
            else:
                update_user_items_balance(current_user, response.json())
                make_transaction('buy', current_user.id, value, total_value, 'litecoin', amount)
                flash('You\'ve successfully purchased %s LTC for $%s' % (amount, total_value))
                return render_template('buy_litecoin.html',
                                       user=current_user,
                                       amount=get_amount_of_item(current_user.id, 'litecoin'),
                                       price=response.json()['litecoin']['usd'])


@app.route('/sell_litecoin', methods=['POST', 'GET'])
@login_required
def sell_litecoin():
    if request.method == 'GET':
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )

        update_user_items_balance(current_user, response.json())

        return render_template('sell_litecoin.html',
                               user=current_user,
                               amount=get_amount_of_item(current_user.id, 'litecoin'),
                               price=response.json()['litecoin']['usd']
                               )

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        user_amount = float(get_amount_of_item(current_user.id, 'litecoin'))
        parameters = {
            'ids': 'bitcoin,litecoin,ethereum,dogecoin',
            'vs_currencies': 'usd'
        }

        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params=parameters
        )
        if amount > user_amount or amount <= 0.0:
            flash('Amount is invalid or you don\'t have enough LTC!')
            return render_template('sell_litecoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'litecoin'),
                                   price=response.json()['litecoin']['usd'])
        else:
            value = float(response.json()['litecoin']['usd'])
            total_value = float(response.json()['litecoin']['usd']) * amount
            update_user_items_balance(current_user, response.json())
            make_transaction('sell', current_user.id, value, total_value, 'litecoin', amount)
            flash('You\'ve successfully sold %s LTC for $%s' % (amount, total_value))
            return render_template('sell_litecoin.html',
                                   user=current_user,
                                   amount=get_amount_of_item(current_user.id, 'litecoin'),
                                   price=response.json()['litecoin']['usd'])


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'mZq4t7w!z$C&F)J@'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    db.create_all(app=app)

    app.run()
