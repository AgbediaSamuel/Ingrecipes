from flask import Blueprint, request, jsonify, current_app, flash, redirect, url_for
import openai
import requests
from Application import db
from flask_login import login_required, current_user
from ..models import SavedRecipe

api = Blueprint('api', __name__)

def preprocessing(user_input):
    """
    This function uses an LLM to standardize and clean the user's input
    to ensure it's suitable for the API request.
    """
    # Call the OpenAI model to clean and standardize the input
    with current_app.app_context():
        openai.api_key = current_app.config['OPENAI_API_KEY']
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"Extract and standardize a list of ingredients from the following text: {user_input}. Make sure the list is in a format suitable for an API query.",
        temperature=0.5,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    
    # Extract and clean the ingredients list
    ingredients = response.choices[0].text.strip().split(',')
    ingredients = [ingredient.strip().lower() for ingredient in ingredients]
    
    return ingredients

@api.route('/process_ingredients', methods=['POST'])
def process_ingredients():
    user_input = request.json.get('ingredients', '')
    
    standardized_ingredients = preprocessing(user_input)
    
    return jsonify(standardized_ingredients)

@api.route('/get_recipes', methods=['POST'])
def get_recipes():
    ingredients = request.json.get('ingredients', [])
    ingredients_str = ', '.join(ingredients)

    with current_app.app_context():
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
