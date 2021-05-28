from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):

    __tablename__ = "user_accounts"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    balance = db.Column(db.Numeric, default=0.0, nullable=False)


class Item(db.Model):

    __tablename__ = "items"

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)

class UserTransaction(db.Model):

    __tablename__ = "user_transactions"

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.user_id'))
    #item_id
    action = db.Column(db.String(6)) #bought/sold
    value = db.Column(db.Numeric, nullable=False)