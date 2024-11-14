import os
import requests
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Load environment variables from .env file
load_dotenv()

# Get the token from environment variables
TOKEN = os.getenv('telegram_token')
API_URL = 'http://127.0.0.1:8000/api/get_recipes' # Backend API URL for retrieving recipes

# Define a start command
async def start(update, context):
    await update.message.reply_text("Hello! I am your new bot. How can I assist you today?") #initial message shown to user when they start the bot


# include logic for rate limiting (number of requests)
# Function to retrieve recipes based on user-input
async def get_recipes(update, context):
    user_input = update.message.text

    if len(user_input) >= 250:
        await update.message.reply_text("Please shorten the length of your request.")
    # print(f"User input: {user_input}")  # Log user input for testing purposes
    try:
        response = requests.post(API_URL, json={'ingredients': user_input})
        response.raise_for_status()
        
        if response.status_code == 200:
            recipes = response.json()
            for recipe in recipes:
                title = recipe.get('title', 'No title')
                url = recipe.get('url', '')
                message = f"{title}\n[Link to Recipe]({url})"
                
                # Send the message
                await update.message.reply_text(message, parse_mode='Markdown') #showing the recipe title and link to the recipe 
        else:
            await update.message.reply_text("Sorry, I couldn't fetch recipes at the moment.")
    except requests.RequestException as e:
        await update.message.reply_text(f"Error: {e}")
        print(f"RequestException: {e}")  # Log the exception for testing purposes

# Define a main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))  # Start command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_recipes))  # Process ingredients and get recipes

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()