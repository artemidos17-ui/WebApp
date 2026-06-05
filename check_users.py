# check_users.py - Query all users from database
from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    
    if not users:
        print("? No users found in database")
    else:
        print(f"\n? Found {len(users)} user(s):\n")
        print(f"{'ID':<5} {'EMAIL':<30} {'ROLE':<10} {'VERIFIED':<10}")
        print("-" * 60)
        
        for user in users:
            verified = "? Yes" if user.is_verified else "? No"
            print(f"{user.id:<5} {user.email:<30} {user.role:<10} {verified:<10}")
        
        print("\n" + "="*60)
        print(f"Total: {len(users)} users")
