from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if user already exists
    if not User.query.filter_by(username='admin').first():
        user = User(
            username='admin',
            password=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()
        print("User created successfully!")
    else:
        print("User already exists!")