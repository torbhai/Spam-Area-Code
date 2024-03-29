# Import the libraries
import telebot
import requests
import os
import json

# Get the constants from the environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN") # Get the bot token from the environment variable
COUNTRY_CODE = os.getenv("COUNTRY_CODE") # Get the country code from the environment variable
YOU_API_URL = "https://api.ydc-index.io/search" # You.com web search API URL
YOU_API_TOKEN = os.getenv("YOU_API_TOKEN") # Get the You.com API token from the environment variable

# Create the bot object
bot = telebot.TeleBot(BOT_TOKEN)

# Define the message handler for the /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Send a welcome message and ask the user to enter the name of the bank
    bot.reply_to(message, "Welcome to the Area Codes Grabber Bot! By @TheLogman Please enter the name of the bank.")

# Define the message handler for any message
@bot.message_handler(func=lambda message: True)
def generate_and_send_number_leads(message):
    # Try to split the user input into the bank name
    try:
        bank_name = message.text
    # Catch any errors that might occur if the user input is not valid
    except (ValueError, IndexError) as e:
        # Log the error message
        print(f"Error from user input: {e}")
        # Send a feedback message to the user
        bot.reply_to(message, "Sorry, your input is not valid. Please enter the name of the bank.")
        # Return from the function
        return
    # Try to generate the number leads
    try:
        # Prepare the data for the POST request
        data = {
            "input": {"query": f"List of top 10 cities of {bank_name} with area codes in United States based on highest number of branches:"},
            "output": {"count": 10, "type": "text"}
        }
        headers = {"Authorization": f"Token {YOU_API_TOKEN}"}
        # Send the POST request to the You.com web search API
        response = requests.post(YOU_API_URL, headers=headers, data=json.dumps(data))
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            response_data = response.json()
            # Get the generated text
            generated_text = response_data["output"]["text"]
            cities_with_area_codes = generated_text.split("\n")
            # Send the cities with area codes to the user
            bot.reply_to(message, "\n".join(cities_with_area_codes))
        else:
            # Log the error message
            print(f"Error from You.com web search API: {response.status_code}")
            # Send a feedback message to the user
            bot.reply_to(message, "Sorry, something went wrong with the You.com web search API. Please try again later.")
    # Catch any errors that might occur
    except requests.exceptions.RequestException as e:
        # Log the error message
        print(f"Error from requests: {e}")
        # Send a feedback message to the user
        bot.reply_to(message, "Sorry, something went wrong with the requests library. Please try again later.")

# Start the bot polling
bot.polling()
