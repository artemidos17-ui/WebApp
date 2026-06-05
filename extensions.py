from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'login'
#to extensions.py uparxei gia na kanei import to db kai to login_manager apo models kai admin_routes xwris na kanei circular imports