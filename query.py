from model import db, User, Item, UserTransaction
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal


def is_user_exists(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    return None


def create_user(name, surname, email, password):
    db.session.add(User(name, surname, email, generate_password_hash(password)))
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def find_item(user_id, item_name):
    return Item.query.filter_by(user_id=user_id, name=item_name).first()


def get_amount_of_item(user_id, item_name):
    item = find_item(user_id, item_name)
    if item is None:
        return 0
    return item.amount


def make_transaction(action, user_id, value, total_value, item_name, item_amount):
    user = get_user_by_id(user_id)
    if action == 'buy':
        user.balance = Decimal(str(user.balance)) - Decimal(str(total_value))
        user.items_balance = Decimal(str(user.items_balance)) + Decimal(str(total_value))
        user.balance = Decimal(str(user.balance)).normalize()
        user.items_balance = Decimal(str(user.items_balance)).normalize()
        item = find_item(user_id, item_name)
        if item is None:
            db.session.add(Item(user_id, item_name, item_amount))
        else:
            item.amount += item_amount
        db.session.add(UserTransaction(user_id, item_name, item_amount, value, total_value, 'buy'))
        db.session.commit()
    elif action == 'sell':
        user.balance = Decimal(str(user.balance)) + Decimal(str(total_value))
        user.balance = Decimal(str(user.balance)).normalize()
        user.items_balance = Decimal(str(user.items_balance)) - Decimal(str(total_value))
        user.items_balance = Decimal(str(user.items_balance)).normalize()
        item = find_item(user_id, item_name)
        item.amount -= item_amount
        if item.amount == 0:
            Item.query.filter_by(user_id=user_id, name=item_name).delete()
        db.session.add(UserTransaction(user_id, item_name, item_amount, value, total_value, 'sell'))
        db.session.commit()


def user_transactions(user_id):
    transactions = UserTransaction.query.filter_by(user_id=user_id).all()
    return transactions


def update_user_items_balance(curr_user, cryptocurrencies):
    balance = 0.0
    items = Item.query.filter_by(user_id=curr_user.id).all()
    for c in items:
        balance = Decimal(str(balance)) + c.amount * Decimal(str(cryptocurrencies[c.name]['usd']))
        balance = Decimal(str(balance)).normalize()
    curr_user.items_balance = balance
    db.session.commit()
