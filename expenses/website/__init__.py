from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
import pymysql

app = Flask(__name__)
app.config["SECRET_KEY"] = "123451fdsfdsfsd"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/expenses"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "views.login"

from .models import User, Incomes, Expenses

from .views import views_blueprint

app.register_blueprint(views_blueprint, url_prefix="/")


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


from .routes import IncomesAPI, AuthAPI, APIExpenses, RegisterAPI, IncomeAPI, ApiExpense

api = Api(app)
api.add_resource(IncomesAPI, "/api/incomes")
api.add_resource(AuthAPI, "/api/auth")
api.add_resource(RegisterAPI, "/api/register")
api.add_resource(APIExpenses, "/api/expenses")
api.add_resource(IncomeAPI, "/api/incomes/<id>")
api.add_resource(ApiExpense, "/api/expenses/<id>")
cors = CORS(app)
