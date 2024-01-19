# Import the libraries
import telebot
import requests
import random
import os

# Define the constants
BOT_TOKEN = os.environ["BOT_TOKEN"] # Get the bot token from the environment variable
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
COUNTRY_CODE = "+1" # USA country code
TEMPERATURE = 0.6 # The temperature for the ChatGPT model
MAX_TOKENS = 100 # The maximum number of tokens for the ChatGPT model

# Create the bot object
bot = telebot.TeleBot(BOT_TOKEN)

# Define the message handler for the /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Send a welcome message and ask the user to enter the name of the bank and the number of leads
    bot.reply_to(message, "Welcome to the Bank Number Leads Bot! Please enter the name of the bank and the desired number of leads.")

# Define the message handler for any message
@bot.message_handler(func=lambda message: True)
def generate_number_leads(message):
    # Split the user input into the bank name and the number of leads
    user_input = message.text.split()
    bank_name = user_input[0]
    num_leads = int(user_input[1])
    # Try to generate the number leads
    try:
        # Make a request to the ChatGPT model
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "prompt": f"List of top 10 cities of {bank_name} with area codes in United States based on highest number of branches:",
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE
            }
        )
        # Check if the response is successful
        response.raise_for_status()
        # Parse the response and extract the generated cities with area codes
        generated_text = response.json()["choices"][0]["text"]
        cities_with_area_codes = generated_text.split("\n")
        # Generate the number leads
        number_leads = []
        for i in range(num_leads):
            # Randomly choose a city with an area code from the list
            city_with_area_code = random.choice(cities_with_area_codes)
            area_code = city_with_area_code.split(":")[1].strip()
            # Generate a random phone number with the country code and the last seven digits
            last_seven_digits = str(random.randint(1000000, 9999999))
            number = COUNTRY_CODE + area_code + last_seven_digits
            # Append the generated phone number to the list of number leads
            number_leads.append(number)
        # Save the list of number leads to a text file
        with open("number_leads.txt", "w") as file:
            file.write("\n".join(number_leads))
        # Send the number leads file to the user
        with open("number_leads.txt", "rb") as file:
            bot.send_document(message.chat.id, file)
    # Catch any errors that might occur
    except telebot.apihelper.ApiTelegramException as e:
        # Log the error message
        print(f"Error from Telegram API: {e}")
        # Send a feedback message to the user
        bot.reply_to(message, "Sorry, something went wrong with the Telegram API. Please try again later.")
# Start the bot polling
bot.polling()
