from flask import Blueprint, render_template
from flask_login import login_required, current_user
from Application import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/saved_recipes')
@login_required
def saved_recipes():
    user_saved_recipes = current_user.saved_recipes
    return render_template('saved_recipes.html', recipes=user_saved_recipes)
