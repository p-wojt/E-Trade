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
