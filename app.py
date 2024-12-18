from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import extract
import os

app = Flask(__name__)
print("Static folder path:", app.static_folder)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'static/article_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Define valid categories, we can add more later
VALID_CATEGORIES = ['News', 'Politics', 'Human Rights', 'Russia']

# Make sure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    articles = db.relationship('Article', backref='author', lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publication = db.Column(db.String(100))
    date_published = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50))
    image_filename = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_content(content):
    # Replace all types of line breaks with newlines
    content = content.replace('\r\n', '\n')
    # Add paragraph markers for double newlines
    content = content.replace('\n\n', '[PARA]')
    # Replace remaining single newlines with spaces
    content = content.replace('\n', ' ')
    # Clean up any duplicate spaces
    content = ' '.join(content.split())
    return content

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    publication = request.args.get('publication')
    year = request.args.get('year')
    category = request.args.get('category')
    
    # Start with base query
    query = Article.query
    
    # Apply filters
    if publication:
        query = query.filter_by(publication=publication)
    if year:
        query = query.filter(extract('year', Article.date_published) == int(year))
    if category:
        query = query.filter_by(category=category)
    
    # Get articles with applied filters
    articles = query.order_by(Article.date_published.desc()).all()
    
    # Get all unique years from articles
    years_query = db.session.query(
        extract('year', Article.date_published).label('year')
    ).distinct().order_by('year').all()
    years = [int(year[0]) for year in years_query if year[0]]
    
    publications = ['BBC', 'Radio Liberty', 'taz']
    
    return render_template('home.html', 
                         articles=articles,
                         publications=publications,
                         years=years,
                         categories=VALID_CATEGORIES,
                         current_publication=publication,
                         current_year=year,
                         current_category=category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out.')
    return redirect(url_for('home'))

@app.route('/new_article', methods=['GET', 'POST'])
@login_required
def new_article():
    if request.method == 'POST':
        if request.form['category'] not in VALID_CATEGORIES:
            flash('Invalid category selected')
            return render_template('new_article.html', categories=VALID_CATEGORIES)

        # Handle image upload
        image = request.files['image']
        image_filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_filename = f"{datetime.now().timestamp()}_{filename}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Format content for proper paragraph spacing
        content = format_content(request.form['content'])

        try:
            date_published = datetime.strptime(request.form['date_published'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD')
            return render_template('new_article.html', categories=VALID_CATEGORIES)

        article = Article(
            title=request.form['title'],
            content=content,
            publication=request.form['publication'],
            category=request.form['category'],
            date_published=date_published,
            image_filename=image_filename,
            user_id=current_user.id
        )
        db.session.add(article)
        db.session.commit()
        flash('Article created successfully!')
        return redirect(url_for('home'))
    return render_template('new_article.html', categories=VALID_CATEGORIES)

@app.route('/article/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    return render_template('article.html', article=article)

@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    if article.user_id != current_user.id:
        flash('You can only edit your own articles.')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if request.form['category'] not in VALID_CATEGORIES:
            flash('Invalid category selected')
            return render_template('edit_article.html', 
                                article=article, 
                                categories=VALID_CATEGORIES)

        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                # Delete old image if it exists
                if article.image_filename:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], article.image_filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(image.filename)
                image_filename = f"{datetime.now().timestamp()}_{filename}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                article.image_filename = image_filename

        # Format content for proper paragraph spacing
        content = format_content(request.form['content'])

        try:
            date_published = datetime.strptime(request.form['date_published'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD')
            return render_template('edit_article.html', article=article, categories=VALID_CATEGORIES)

        article.title = request.form['title']
        article.content = content
        article.publication = request.form['publication']
        article.category = request.form['category']
        article.date_published = date_published
        db.session.commit()
        flash('Article updated successfully!')
        return redirect(url_for('article', id=article.id))
    return render_template('edit_article.html', article=article, categories=VALID_CATEGORIES)

if __name__ == '__main__':
    app.run(debug=True)