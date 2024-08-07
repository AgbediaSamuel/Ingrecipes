from flask import Blueprint, request, jsonify, current_app, flash, redirect, url_for
import openai
import requests
from Application import db
from flask_login import login_required, current_user
from ..models import SavedRecipe

api = Blueprint('api', __name__)

@api.route('/process_ingredients', methods=['POST'])
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

@api.route('/get_recipes', methods=['POST'])
def get_recipes():
    ingredients = request.json.get('ingredients', [])
    ingredients_str = ', '.join(ingredients)
    
    app_id = current_app.config['EDAMAM_APP_ID']
    app_key = current_app.config['EDAMAM_APP_KEY']
    url = f"https://api.edamam.com/api/recipes/v2?type=public&q={ingredients_str}&app_id={app_id}&app_key={app_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        recipes = response.json()
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch recipes'}), 500

    recipes_info = [{
        'title': recipe['recipe']['label'],
        'image': recipe['recipe']['image'],
        'url': recipe['recipe']['url']
    } for recipe in recipes.get('hits', [])]

    return jsonify(recipes_info)

@api.route('/save_recipe', methods=['POST'])
@login_required
def save_recipe():
    recipe_title = request.form.get('recipe_title')
    recipe_image = request.form.get('recipe_image')
    recipe_url = request.form.get('recipe_url')
    
    existing_recipe = SavedRecipe.query.filter_by(user_id=current_user.id, recipe_url=recipe_url).first()
    if existing_recipe:
        flash('You have already saved this recipe.')
        return redirect(url_for('main.index'))

    new_saved_recipe = SavedRecipe(
        user_id=current_user.id,
        recipe_title=recipe_title,
        recipe_image=recipe_image,
        recipe_url=recipe_url
    )
    db.session.add(new_saved_recipe)
    db.session.commit()
    flash('Recipe saved successfully!')
    return redirect(url_for('main.index'))
