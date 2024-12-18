from app import app, db

try:
    with app.app_context():
        db.create_all()
        print("Database created successfully!")
        print("Database location:", app.config['SQLALCHEMY_DATABASE_URI'])
except Exception as e:
    print("Error creating database:", str(e))