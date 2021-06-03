from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()


class User(db.Model, UserMixin):

    __tablename__ = 'user_accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.String(100), default=20000.0, nullable=False)
    items_balance = db.Column(db.String(100), default=0.0, nullable=False)

    def __init__(self, name, surname, email, password):
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password


class Item(db.Model):

    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.String(100), default=0.0, nullable=False)

    def __init__(self, user_id, name, amount):
        self.user_id = user_id
        self.name = name
        self.amount = amount


class UserTransaction(db.Model):

    __tablename__ = 'user_transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=False)
    item_name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    total_value = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(6), nullable=False) #bought/sold

    def __init__(self, user_id, item_name, amount, value, total_value, action):
        self.user_id = user_id
        self.item_name = item_name
        self.date = date.today()
        self.amount = amount
        self.value = value
        self.total_value = total_value
        self.action = action


