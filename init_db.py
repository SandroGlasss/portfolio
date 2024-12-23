from app import app, db
import os

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

try:
    with app.app_context():
        db.create_all()
        print("Database created successfully!")
        print("Database location:", app.config['SQLALCHEMY_DATABASE_URI'])
except Exception as e:
    print("Error creating database:", str(e))