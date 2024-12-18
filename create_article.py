from app import db, app, Article, User
from datetime import datetime

with app.app_context():
    admin = User.query.first()
    if admin:
        article = Article(
            title="Test Article",
            content="This is a test article content",
            publication="BBC",
            date_published=datetime.now(),
            category="Test",
            user_id=admin.id
        )
        db.session.add(article)
        db.session.commit()
        print("Article created successfully!")
        
        # Print all articles to verify
        articles = Article.query.all()
        for article in articles:
            print(f"Title: {article.title}, Publication: {article.publication}")