from datetime import datetime

from flask_login import UserMixin
from crypto_portfolio import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    transactions = db.relationship('Transactions', backref='user', lazy=True)
    balance = db.relationship('Balance', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    txn_type = db.Column(db.String(50), default='buy')  # buy or sell
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime)
    fee = db.Column(db.Float)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    coin_id = db.Column(db.Integer, db.ForeignKey('coins.id', ondelete='CASCADE'))


class Coins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    current_price = db.Column(db.Float, nullable=False)
    transactions = db.relationship('Transactions', backref='coins', lazy=True)


class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_balance = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
