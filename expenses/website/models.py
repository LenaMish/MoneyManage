from flask_login import UserMixin
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    incomes = db.relationship("Incomes")
    expenses = db.relationship("Expenses")


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    category = db.Column(db.String(150))
    amount = db.Column(db.String(150))
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Incomes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.String(150))
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
