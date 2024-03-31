# Import necessary libraries
from flask import Flask, request, jsonify, redirect, url_for, flash, render_template_string, render_template
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import openai
import requests
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'Club19ofdagoat'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['EDAMAM_APP_ID'] = os.getenv('EDAMAM_APP_ID')
app.config['EDAMAM_APP_KEY'] = os.getenv('EDAMAM_APP_KEY')


# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login view if unauthorized access

# OpenAI API key setup
openai.api_key = 'Placeholder'

# User model using Flask-SQLAlchemy for database interactions
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database initialization function
@app.before_request
def initialize_database():
    db.create_all()

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email address already exists')
            return redirect(url_for('register'))

        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    # Note: Replace 'Registration Form Here' with your actual registration form template
    return render_template_string('Registration Form Here')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    # Note: Replace 'Login Form Here' with your actual login form template
    return render_template_string('Login Form Here')

# Logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Home page route
@app.route('/')
def index():
    return render_template_string('This is the home page')

# Process ingredients and get recipes route
@app.route('/process_ingredients', methods=['POST'])
def process_ingredients():
    user_input = request.json.get('ingredients', '')
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",  
        prompt=f"Extract a list of ingredients from the following text: {user_input}",
        temperature=0.5,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    ingredients = response.choices[0].text.strip().split(',')
    return jsonify(ingredients)

# Get recipes route
@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    ingredients = request.json.get('ingredients', [])
    ingredients_str = ', '.join(ingredients)
    
    app_id = app.config['f1a5dd2d']
    app_key = app.config['d0f9dbf476b7e1a9082db595a6964781']
    url = f"https://api.edamam.com/api/recipes/v2?type=public&q={ingredients_str}&app_id={app_id}&app_key={app_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises a HTTPError for bad responses
        recipes = response.json()
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch recipes'}), 500

    recipes_info = [{
        'title': recipe['recipe']['label'],
        'image': recipe['recipe']['image'],
        'url': recipe['recipe']['url']
    } for recipe in recipes.get('hits', [])]

    return jsonify(recipes_info)

if __name__ == "__main__":
    app.run(debug=True)
