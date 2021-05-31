from model import db, User, Item, UserTransaction
from werkzeug.security import generate_password_hash, check_password_hash


def is_user_exists(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    return None


def create_user(name, surname, email, password):
    db.session.add(User(name, surname, email, generate_password_hash(password)))
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(int(user_id))


def find_item(user_id, item_name):
    return Item.query.filter_by(user_id=user_id, name=item_name).first()


def get_amount_of_item(user_id, item_name):
    item = find_item(user_id, item_name)
    if item is None:
        return 0.0
    return item.amount


def make_transaction(action, user_id, value, item_name, item_amount):
    user = get_user_by_id(user_id)
    if action == 'buy':
        user.balance = float(user.balance) - value
        user.items_balance = float(user.items_balance) + value
        item = find_item(user_id, item_name)
        if item is None:
            db.session.add(Item(user_id, item_name, item_amount))
        else:
            item.amount = float(item_amount) + item_amount
        db.session.add(UserTransaction(user_id, item_name, item_amount, value, 'buy'))
        db.session.commit()
    elif action == 'sell':
        user.balance = float(user.balance) + value
        user.items_balance = float(user.items_balance) - value
        item = find_item(user_id, item_name)
        item.amount = float(item.amount) - float(item_amount)
        if item_amount == 0.0:
            Item.query.filter_by(user_id=user_id, item_name=item_name).delete()
        db.session.add(UserTransaction(user_id, item_name, item_amount, value, 'sell'))
        db.session.commit()


def user_transactions(user_id):
    transacion = UserTransaction.query.filter_by(user_id=user_id).all()
    print(transacion)
    return transacion
