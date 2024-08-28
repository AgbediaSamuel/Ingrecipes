from flask import Blueprint, request, jsonify, current_app, flash, redirect
import openai
import logging #this line is for testing
import requests
from Application import db
from flask_login import login_required, current_user
from ..models import saved_recipe

api = Blueprint('api', __name__)
main = Blueprint('main', __name__)


# The function below standardizes natural langauge input
def preprocessing(user_input):
    with current_app.app_context():
        openai.api_key=current_app.config['OPENAI_API_KEY']
    # Calling a Large Language model to clean and standardize the input
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract and standardize a list of ingredients from the following text: {user_input}. Make sure the list is in a format suitable for an API query and nothing more."}
        ],
    )
    
    # Extract and clean the ingredients list
    ingredients = response.choices[0].message['content'].strip().split(',')
    ingredients = [ingredient.strip().lower() for ingredient in ingredients]
    
    return ingredients

# The function /api/process_ingredients below is not useful as get_recipes below has been updated to call preprocessing directly to eliminate redundancy here
# @api.route('/process_ingredients', methods=['POST'])
# def process_ingredients():
#     user_input = request.json.get('ingredients', '')
    
#     standardized_ingredients = preprocessing(user_input)
    
#     return jsonify(standardized_ingredients)

@api.route('/get_recipes', methods=['POST'])
# @login_required
def get_recipes():
    user_input = request.json.get('ingredients', '')
    
    standardized_ingredients = preprocessing(user_input)
    ingredients_str = ', '.join(standardized_ingredients)
    
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

# def get_recipes():
#     user_input = request.json.get('ingredients', '')
#     logging.debug(f"User input: {user_input}")
    
#     standardized_ingredients = preprocessing(user_input)
#     logging.debug(f"Standardized ingredients: {standardized_ingredients}")
    
#     ingredients_str = ', '.join(standardized_ingredients)
#     logging.debug(f"Ingredients string: {ingredients_str}")
    
#     with current_app.app_context():
#         app_id = current_app.config['EDAMAM_APP_ID']
#         app_key = current_app.config['EDAMAM_APP_KEY']
#         logging.debug(f"EDAMAM_APP_ID: {app_id}")
#         logging.debug(f"EDAMAM_APP_KEY: {app_key}")
    
#     url = f"https://api.edamam.com/api/recipes/v2?type=public&q={ingredients_str}&app_id={app_id}&app_key={app_key}"
#     logging.debug(f"Request URL: {url}")
    
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         recipes = response.json()
#         logging.debug(f"API response: {recipes}")
#     except requests.RequestException as e:
#         logging.error(f"Failed to fetch recipes: {e}")
#         return jsonify({'error': 'Failed to fetch recipes'}), 500

#     recipes_info = [{
#         'title': recipe['recipe']['label'],
#         'image': recipe['recipe']['image'],
#         'url': recipe['recipe']['url']
#     } for recipe in recipes.get('hits', [])]

#     logging.debug(f"Recipes info: {recipes_info}")
#     return jsonify(recipes_info)


@api.route('/save_recipe', methods=['POST'])
@login_required
def save_recipe():
    recipe_title = request.form.get('recipe_title')
    recipe_image = request.form.get('recipe_image')
    recipe_url = request.form.get('recipe_url')
    
    existing_recipe = saved_recipe.query.filter_by(user_id=current_user.id, recipe_url=recipe_url).first()
    if existing_recipe:
        flash('You have already saved this recipe.')
        return '', 204

    new_saved_recipe = saved_recipe(
        user_id=current_user.id,
        recipe_title=recipe_title,
        recipe_url=recipe_url
    )
    db.session.add(new_saved_recipe)
    db.session.commit()
    flash('Recipe saved successfully!')
    return '', 204