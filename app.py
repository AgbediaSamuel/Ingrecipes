import openai
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

# Replace "your_openai_api_key" with your actual OpenAI API key
openai.api_key = 'your_openai_api_key'

@app.route('/process_ingredients', methods=['POST'])
def process_ingredients():
    user_input = request.json.get('ingredients')
    response = openai.Completion.create(
      engine="text-davinci-003", # Check for the latest and most suitable model
      prompt=f"Extract a list of ingredients from the following text: {user_input}",
      temperature=0.5,
      max_tokens=100,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    # Assuming the AI response is structured as a comma-separated list
    ingredients = response.choices[0].text.strip().split(',')
    return jsonify(ingredients)

if __name__ == "__main__":
    app.run(debug=True)