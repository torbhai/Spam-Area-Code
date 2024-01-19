# Import the libraries
import telebot
import requests
import random
import os

# Import the transformers classes
from transformers import AutoModelForCausalLM, AutoTokenizer

# Get the constants from the environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN") # Get the bot token from the environment variable
COUNTRY_CODE = os.getenv("COUNTRY_CODE") # Get the country code from the environment variable
TEMPERATURE = float(0.6) # Get the temperature for the Llama 2 model from the environment variable
MAX_TOKENS = int(20000) # Get the maximum number of tokens for the Llama 2 model from the environment variable
# Create the bot object
bot = telebot.TeleBot(BOT_TOKEN)

# Define the message handler for the /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Send a welcome message and ask the user to enter the name of the bank and the number of leads
    bot.reply_to(message, "Welcome to the Bank Number Leads Bot! Please enter the name of the bank and the desired number of leads.")

# Define the message handler for any message
@bot.message_handler(func=lambda message: True)
def generate_and_send_number_leads(message):
    # Try to split the user input into the bank name and the number of leads
    try:
        user_input = message.text.split()
        bank_name = user_input[0]
        num_leads = int(user_input[1])
    # Catch any errors that might occur if the user input is not valid
    except (ValueError, IndexError) as e:
        # Log the error message
        print(f"Error from user input: {e}")
        # Send a feedback message to the user
        bot.reply_to(message, "Sorry, your input is not valid. Please enter the name of the bank and the desired number of leads.")
        # Return from the function
        return
    # Try to generate the number leads
    try:
        # Try to load the Llama 2 model and tokenizer
        try:
            model = AutoModelForCausalLM.from_pretrained("meta/llama-2-7b-chat")
            tokenizer = AutoTokenizer.from_pretrained("meta/llama-2-7b-chat")
        # Catch any errors that might occur when loading the model or tokenizer
        except (OSError, RuntimeError) as e:
            # Log the error message
            print(f"Error from loading the model or tokenizer: {e}")
            # Send a feedback message to the user
            bot.reply_to(message, "Sorry, something went wrong with loading the Llama 2 model or tokenizer. Please try again later.")
            # Return from the function
            return
        # Encode the prompt and generate the cities with area codes
        input_ids = tokenizer(f"List of top 10 cities of {bank_name} with area codes in United States based on highest number of branches:", return_tensors="pt").input_ids
        output_ids = model.generate(input_ids, max_length=MAX_TOKENS, do_sample=True, temperature=TEMPERATURE).squeeze()
        # Decode the output and remove the prompt
        generated_text = tokenizer.decode(output_ids, skip_special_tokens=True).replace(f"List of top 10 cities of {bank_name} with area codes in United States based on highest number of branches:", "")
        cities_with_area_codes = generated_text.split("\n")
        # Generate the number leads
        number_leads = []
        for i in range(num_leads):
            # Randomly choose a city with an area code from the list
            city_with_area_code = random.choice(cities_with_area_codes)
            area_code = city_with_area_code.split(":")[1].strip()
            # Generate a random phone number with the country code and the last seven digits
            last_seven_digits = str(random.randint(1000000, 9999999))
            number = f"{COUNTRY_CODE}{area_code}{last_seven_digits}"
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
