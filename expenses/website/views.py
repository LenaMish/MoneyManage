import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from pandas import DataFrame
from werkzeug.security import check_password_hash, generate_password_hash
from . import User, db, Expenses, Incomes
import requests
import plotly.express as px
import pandas as pd
import json
import plotly
import plotly.graph_objects as go

views_blueprint = Blueprint("views", __name__)


@views_blueprint.route("/")
@login_required
def home():
    return render_template("home.html")


@views_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Invalid email")
        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("views.home"))
        else:
            flash("Invalid password")
    return render_template("login.html")


@views_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("confirm-password")

        if not password:
            flash("Password is empty")
        elif password != password2:
            flash("Passwords are not equal")
        else:
            user = User(email=email, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("User registered")
            return redirect(url_for("views.login"))

    return render_template("register.html")


@views_blueprint.route("/incomes", methods=["GET", "POST"])
@login_required
def incomes():
    if request.method == "POST":
        amount = request.form.get("amount")
        date = request.form.get("date")

        if not amount or not date:
            flash("Fill all fields!")
        else:
            income = Incomes(amount=amount, date=date, user_id=current_user.id)
            db.session.add(income)
            db.session.commit()
            flash("Income added!")

    return render_template("incomes.html")


@views_blueprint.route("/incomes_update/<int:id>", methods=["GET", "POST"])
def update_incomes(id):
    income = Incomes.query.filter_by(id=id, user_id=current_user.id).first()
    if not income:
        flash("Invalid income id")
        return redirect(url_for("views.incomes"))

    if request.method == "POST":
        amount = request.form.get('amount')
        date = request.form.get('date')

        if not amount or not date:
            flash("Fill all fields!")
        else:
            income.date = date
            income.amount = amount
            db.session.commit()
            flash("Income edited!")
            return redirect(url_for("views.incomes"))

    return render_template("incomes_update.html", income=income)


@views_blueprint.route("/delete_income/<int:id>", methods=["GET"])
@login_required
def delete_income(id):
    income = Incomes.query.filter_by(id=id, user_id=current_user.id).first()
    if not income:
        flash("Invalid income id")
    else:
        flash("Income deleted!")
        Incomes.query.filter_by(id=id).delete()
        db.session.commit()
    return redirect(url_for("views.incomes"))


@views_blueprint.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        amount = request.form.get("amount")
        date = request.form.get("date")

        if not name or not category or not amount or not date:
            flash("Fill all fields!")
        else:
            expense = Expenses(name=name, category=category, amount=amount, date=date, user_id=current_user.id)
            db.session.add(expense)
            db.session.commit()
            flash("Expense added!")

    return render_template("expenses.html")


@views_blueprint.route("/expenses_update/<int:id>", methods=["GET", "POST"])
def update_expenses(id):
    expense = Expenses.query.filter_by(id=id, user_id=current_user.id).first()
    if not expense:
        flash("Invalid expense id")
        return redirect(url_for("views.expenses"))

    if request.method == "POST":
        name = request.form.get('name')
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')

        if not name or not category or not amount or not date:
            flash("Fill all fields!")
        else:
            expense.name = name
            expense.category = category
            expense.amount = amount
            expense.date = date
            db.session.commit()
            flash("Expense edited!")
            return redirect(url_for("views.expenses"))

    return render_template("expenses_update.html", expense=expense)


@views_blueprint.route("/expenses_delete/<int:id>", methods=["GET"])
@login_required
def delete_expense(id):
    expense = Expenses.query.filter_by(id=id, user_id=current_user.id).first()
    if not expense:
        flash("Invalid expense id")
    else:
        flash("Expense deleted!")
        Expenses.query.filter_by(id=id).delete()
        db.session.commit()
    return redirect(url_for("views.expenses"))


@views_blueprint.route("/history")
@login_required
def history():
    all = list(current_user.incomes) + list(current_user.expenses)
    all.sort(key=lambda x: x.date)
    return render_template("history.html", all=all, isinstance=isinstance, Incomes=Incomes)


def create_table_and_chart(year, data_type):
    months = {1: "January",
              2: "February",
              3: "March",
              4: "April",
              5: "May",
              6: "June",
              7: "July",
              8: "August",
              9: "September",
              10: "October",
              11: "November",
              12: "December"
              }

    amounts = pd.read_sql(
        f"""SELECT sum(amount) AS amount, month(date) AS month FROM expenses.{data_type} 
            WHERE YEAR(date)={year} AND user_id={current_user.id} GROUP BY month(date) ORDER BY month(date) asc""",
        db.engine)
    amounts["month"] = amounts["month"].map(months)

    fig = px.bar(amounts, x="month", y="amount")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    years = pd.read_sql(
        f"SELECT DISTINCT YEAR(date) AS year FROM {data_type} WHERE user_id={current_user.id} ORDER BY year DESC",
        db.engine)
    years = years["year"]

    return amounts, graphJSON, years


@views_blueprint.route('/reports')
@login_required
def reports():
    year = request.args.get("year", datetime.datetime.now().year)
    amounts, graphJSON, years = create_table_and_chart(year, "expenses")

    year1 = request.args.get("year1", datetime.datetime.now().year)
    amounts1, graphJSON1, years1 = create_table_and_chart(year1, "incomes")

    return render_template("reports.html", graphJSON=graphJSON, graphJSON1=graphJSON1, amounts=amounts, amounts1=amounts1, years=years, years1=years1, selected_year=int(year), selected_year1=int(year1))


@views_blueprint.route('/summary')
@login_required
def summary_incomes():
    incomes = pd.read_sql(
        f"""SELECT sum(amount) AS amount, CONCAT(year(date), "-", LPAD(month(date), 2, '0')) as date
        FROM expenses.incomes 
        WHERE user_id={current_user.id} 
        GROUP BY date
        ORDER BY date""",
        db.engine)


    incomes["date"] = pd.to_datetime(incomes["date"], format="%Y-%m")

    expenses = pd.read_sql(
        f"""SELECT sum(amount) AS amount, month(date) as mm, year(date) AS yy 
            FROM expenses.expenses 
            WHERE user_id={current_user.id} 
            GROUP BY mm, yy
            ORDER BY yy, mm""",
        db.engine)

    expenses["date"] = expenses["mm"].astype(str) + " " + expenses["yy"].astype(str)
    expenses["date"] = pd.to_datetime(expenses["date"], format="%m %Y")

    fig = go.Figure()
    fig.add_trace(go.Line(x=incomes["date"], y=incomes["amount"],
                          mode='lines',
                          name='incomes'))
    fig.add_trace(go.Line(x=expenses["date"], y=expenses["amount"],
                          mode='lines+markers',
                          name='expenses'))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    expenses.rename(columns={"amount": "expenses"}, inplace=True)
    incomes.rename(columns={"amount": "incomes"}, inplace=True)
    amounts = pd.merge(incomes, expenses, how="outer")
    amounts.fillna(0, inplace=True)
    return render_template("summary.html", graphJSON=graphJSON, amounts=amounts)


@views_blueprint.route('/summary_expenses')
@login_required
def summary_expenses():
    amounts = pd.read_sql(
        f"""SELECT sum(amount) AS amount, sum(expenses) as expense, month(date) as mm, year(date) AS yy 
        FROM expenses.expenses 
        WHERE user_id={current_user.id} 
        GROUP BY mm, yy
        ORDER BY yy, mm""",
        db.engine)

    amounts["date"] = amounts["mm"].astype(str) + " " + amounts["yy"].astype(str)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=amounts["date"], y=amounts["amount"],
                             mode='lines',
                             name='lines'))
    fig.add_trace(go.Scatter(x="date", y="expense",
                             mode='lines+markers',
                             name='lines+markers'))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("summary_expenses.html", graphJSON=graphJSON, amounts=amounts)


@views_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.login"))
