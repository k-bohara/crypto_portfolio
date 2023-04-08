from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
import os

from dotenv import load_dotenv
load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")
secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@localhost:5432/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

from crypto_portfolio import routes
