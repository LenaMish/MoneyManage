from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from .models import Incomes, User, db, Expenses
from flask import request, flash, render_template
from flask_restful import Resource
from sqlalchemy import text
from datetime import datetime, timedelta
from . import app
from .auth import get_user_id_from_token

get_incomes_query = """
SELECT incomes.id, incomes.amount, incomes.date, incomes.user_id, user.email
FROM incomes INNER JOIN user
ON incomes.user_id=user.id
WHERE user_id = :user_id
"""# :user_id jest zewnetrznym parametrem tego zapytania i musi byc w jakis sposob przekazane

get_expenses_query = """
SELECT expenses.id, expenses.name, expenses.category, expenses.amount, expenses.date, expenses.user_id, user.email
FROM expenses INNER JOIN user
ON expenses.user_id=user.id
WHERE user_id = :user_id
"""

# brakuje dodawania income POST ;
# brakuje aktualizacji i usuwania income PUT DELETE
class IncomesAPI(Resource):
    def get(self):
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)): # tworzy zmienna od razu w if a potem sprawdza czy jest None
            return "Invalid authorization", 401
        # result = db.session.query(Incomes.id, Incomes.amount, Incomes.date, Incomes.user_id, User.email) \
        #     .join(User, User.id == Incomes.user_id) \
        #     .all()

        # dostawiamy parametry do zapytania z get_incomes_query
        result = db.session.query(Incomes.id, Incomes.amount, Incomes.date, Incomes.user_id, User.email) \
            .from_statement(text(get_incomes_query)) \
            .params(user_id=user_id)\
            .all()
        output = []
        for item in result:
            output.append({'id': item.id,
                           'amount': item.amount,
                           'date': item.date.strftime("%d-%m-%Y")})
        return output, 200

    def post(self):
        print(request.headers)
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)):
            return "Invalid authorization", 401
        body = request.json
        amount = body["amount"]
        date = body["date"]
        if not amount or not date:
            return "Fill all fields", 400

        income = Incomes(amount=amount, date=date, user_id=user_id)
        db.session.add(income)
        db.session.commit()
        return "OK", 201


class IncomeAPI(Resource):
    def put(self, id):
        # 0 sprawdz token ;
        # 1 Wyszukaj element o danym id Incomes.query.get(id);
        # 2 jesli element nie wystepuje to zwroc not found 404;
        # 3 jesli wystepuje to sprawdz czy w body sa potrzebne parametry
        # 4 zapisz te parametry od obiektu np income.amount = body["amount"]
        # 5 zapisz zmiany
        # 6 zwroc OK

        print(request.headers)
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)):
            return "Invalid authorization", 401
        income = Incomes.query.get(id)
        if not income:
            return {'message': 'Invalid incoming user id'}, 404
        else:
            body = request.json
            fields = ["amount", "date"]
            for field in fields:
                if field not in body:
                    return {"message": f"Invalid request body, {field} is required"}, 400
                if body[field] is None:
                    return {"message": f"Invalid request body, {field}'s value is empty"}, 400

        income.amount = body["amount"]
        income.date = body["date"]

        db.session.commit()

        return "Edited", 201

    def delete(self, id):
        # 1. Sprawdz token
        # 2. znajdz element o danym id
        # 3. jesli go nie ma to 404
        # 4. usun element zapisz zmiany
        # 5. Zwroc OK
        print(request.headers)
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)):
            return "Invalid authorization", 401
        item = Incomes.query.get(id)
        if not item:
            return {'message': 'Invalid incoming id'}, 404

        db.session.delete(item)
        db.session.commit()
        return {'message': 'Deleted!'}, 200

    def get(self, id):
        # zwraca pojedynczy element o danym id
        # 1. Sprawdz token czy jest poprawny
        # 2. Pobierz wydatek z bazy o id podanym w zmiennej id
        # 3. Jesli wydatek nie istnieje to zwroc not found 404
        # 4. Sprawdz czy user_id z wydatku jest takie samo jak user_id z tokena
        # 5. Jesli te user_id sa rozne to zwroc forbidden 403
        # 6. Wrzuc dane z obiektu z bazy do slownika i zwroc z kodem 200
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)):
            return "Invalid authorization", 401
        item = Incomes.query.get(id)
        if not item:
            return {'message': 'Invalid incoming id'}, 404

        if user_id != item.user_id:
            return {"message": "Forbidden"}, 403

        return {"id": item.id, "amount": item.amount, "date": str(item.date)}, 200


class AuthAPI(Resource):
    def post(self):
        body = request.json
        email = body["email"]
        password = body["password"]
        user = User.query.filter_by(email=email).first()
        if not user:
            return "Invalid credentials", 401
        elif check_password_hash(user.password, password):
            token = jwt.encode({  # tworzy token JWT - Json Web Token
                'id': user.id,
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(minutes=60)
            }, app.config["SECRET_KEY"], algorithm="HS256")
            return {"token": token}
        else:
            return "Invalid credentials", 401


class RegisterAPI(Resource):
    def post(self):
        body = request.json
        email = body["email"]
        password = body["password"]
        user = User.query.filter_by(email=email).first()
        if user:
            return "User already exists", 401

        user = User(email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return "OK", 201


class APIExpenses(Resource):
    def get(self):
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)):
            return "Invalid authorization", 401

        result = db.session.query(Expenses.id, Expenses.name, Expenses.category, Expenses.amount, Expenses.date,
                                  Expenses.user_id, User.email) \
            .from_statement(text(get_expenses_query)) \
            .params(user_id=user_id) \
            .all()
        output = []
        for item in result:
            output.append({'id': item.id,
                           'name': item.name,
                           'category': item.category,
                           'amount': item.amount,
                           'date': item.date.strftime("%d-%m-%Y")})
        return output, 200

    def post(self):
        print(request.headers)
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)): # tworzy zmienna od razu w if a potem sprawdza czy jest None
            return "Invalid authorization", 401

        body = request.json
        name = body["name"]
        category = body["category"]
        amount = body["amount"]
        date = body["date"]

        if not name or not category or not amount or not date:
            return "Fill all fields", 400
        else:
            expense = Expenses(name=name, category=category, amount=amount, date=date, user_id=user_id)
            db.session.add(expense)
            db.session.commit()
            return "OK", 201


class ApiExpense(Resource):
    def put(self, id):
        print(request.headers)
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)):
            return "Invalid authorization", 401
        expense = Expenses.query.get(id)
        if not expense:
            return {'message': 'Invalid incoming user id'}, 404
        else:
            body = request.json
            fields = ["name", "category", "amount", "date"]
            for field in fields:
                if field not in body:
                    return {"message": f"Invalid request body, {field} is required"}, 400
                if body[field] is None:
                    return {"message": f"Invalid request body, {field}'s value is empty"}, 400

        expense.name = body["name"]
        expense.category = body["category"]
        expense.amount = body["amount"]
        expense.date = body["date"]

        db.session.commit()

        return "Edited", 201

    def delete(self, id):
        print(request.headers)
        token = request.headers.get("Authorization")
        if not get_user_id_from_token(token):
            return "Invalid authorization", 401
        item = Expenses.query.get(id)
        if not item:
            return {'message': 'Invalid incoming id'}, 404

        db.session.delete(item)
        db.session.commit()
        return {'message': 'Deleted!'}, 200

    def get(self, id):
        #TODO: dopisac kod taki sam jak w wydatkach ale dla przychodow
        token = request.headers.get("Authorization")
        if not (user_id := get_user_id_from_token(token)):
            return "Invalid authorization", 401

        item_id = Expenses.query.get(id)
        if not item_id:
            return {'message': 'Invalid incoming id'}, 404

        result = db.session.query(Expenses.id, Expenses.name, Expenses.category, Expenses.amount, Expenses.date,
                                  Expenses.user_id, User.email) \
            .from_statement(text(get_expenses_query)) \
            .params(user_id=user_id) \
            .all()
        output = []
        for item in result:
            if int(id) == item.id:
                output.append({'id': item.id,
                            'name': item.name,
                            'category': item.category,
                            'amount': item.amount,
                            'date': item.date.strftime("%d-%m-%Y")})
        return output, 200






