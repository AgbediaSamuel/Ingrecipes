from flask import Blueprint, request, jsonify, current_app
import openai
import requests
from Application import db
from flask_login import login_required, current_user
from ..models import SavedRecipe

api = Blueprint('api', __name__)
main = Blueprint('main', __name__)

def preprocessing(user_input):
    """
    This function uses an LLM to standardize and clean the user's input
    to ensure it's suitable for the API request.
    """

    with current_app.app_context():
        openai.api_key=current_app.config['OPENAI_API_KEY']
    # Call the OpenAI model to clean and standardize the input
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

# @api.route('/process_ingredients', methods=['POST'])
# def process_ingredients():
#     user_input = request.json.get('ingredients', '')
    
#     standardized_ingredients = preprocessing(user_input)
    
#     return jsonify(standardized_ingredients)

@api.route('/get_recipes', methods=['POST'])
def get_recipes():
    user_input = request.json.get('ingredients', '')
    
    # Call the process_ingredients function to standardize the input
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
