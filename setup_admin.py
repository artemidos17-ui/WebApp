# setup_admin.py - Run this once to set yourself as admin
from app import app, db
from models import User
from admin_routes import ADMIN_EMAIL

with app.app_context():
    admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
    if admin_user:
        admin_user.role = 'admin'
        admin_user.is_verified = True
        db.session.commit()
        print(f'? {ADMIN_EMAIL} is now admin!')
    else:
        print(f'? User {ADMIN_EMAIL} not found. Sign up first, then run this script.')
