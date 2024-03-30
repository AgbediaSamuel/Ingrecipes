from flask import Flask, render_template, request, jsonify

app = Flask(__name__) #create a web  server using the Flask framework.

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    ingredients = request.json.get('ingredients')  # Expecting a list of ingredients
    ingredients_str = ', '.join(ingredients)  # Convert list to string separated by commas
    
    app_id = 'your_edamam_app_id' #REPLACE THIS WIRH THE ACTUAL API
    app_key = 'your_edamam_api_key' #REPLACE THIS WITH THE ACTUAL KEY
    
    url = f"https://api.edamam.com/api/recipes/v2?type=public&q={ingredients_str}&app_id={app_id}&app_key={app_key}"
    response = requests.get(url)
    recipes = response.json()

    # Parsing Edamam response to extract relevant recipe information
    recipes_info = []
    for recipe in recipes['hits']:
        recipe_data = recipe['recipe']
        recipes_info.append({
            'title': recipe_data['label'],
            'image': recipe_data['image'],
            'url': recipe_data['url']  # URL to the recipe's instructions
        })

    return jsonify(recipes_info)

if __name__ == "__main__":
    app.run(debug=True)