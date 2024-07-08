from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from config import Config
from flask_cors import CORS


# Initialize Flask extensions (without app context)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
admin = Admin(template_mode='bootstrap3')
bootstrap = Bootstrap()

# Configure the login view
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    # Initialize Flask extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    admin.init_app(app)
    bootstrap.init_app(app)
    CORS(app)

    with app.app_context():
        from . import routes, models  # Import routes and models within app context
        db.create_all()  # Create database tables for our data models

    return app
