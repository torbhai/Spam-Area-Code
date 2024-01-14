# Import the libraries
import telebot
import requests
import random
import os
import telebot
import requests
import random
import os
import time  # Added for timestamp

# ... (previous code remains the same)

# Modified message handlers with enhanced tracking and handling interruptions:
@bot.message_handler(content_types=["text"])
def ask_bank_name(message):
    chat_id = message.chat.id
    if chat_id in waiting_for_bank_name and time.time() - waiting_for_bank_name[chat_id] > 60:  # Re-prompt if no response in 60 seconds
        bot.reply_to(message, "Please enter the name of the bank:")
    else:
        waiting_for_bank_name[chat_id] = time.time()  # Store timestamp

@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text == "Please enter the name of the bank:")
def store_bank_name(message):
    chat_id = message.chat.id
    bank_name = message.text
    waiting_for_bank_name.pop(chat_id, None)  # Remove from waiting dictionary
    waiting_for_num_leads[chat_id] = bank_name
    bot.reply_to(message, "Please enter the number of leads:")

@bot.message_handler(content_types=["text"])
def handle_interruptions(message):
    chat_id = message.chat.id
    if chat_id in waiting_for_bank_name and message.text != bank_name:  # Check if user is interrupting
        bot.reply_to(message, "Please provide the bank name first to continue.")

# ... (rest of the code remains the same)


# Define a final message handler for messages that contain numbers
@bot.message_handler(regexp="^[0-9]+$")
def generate_number_leads(message):
    # Get the chat id and the number of leads
    chat_id = message.chat.id
    num_leads = int(message.text)
    # Check if the chat id is in the waiting_for_num_leads dictionary
    if chat_id in waiting_for_num_leads:
        # Get the bank name from the waiting_for_num_leads dictionary
        bank_name = waiting_for_num_leads.pop(chat_id, None)
        # Try to generate the number leads
        try:
            # Make a request to the ChatGPT model
            response = requests.post(
                "https://api.openai.com/v1/engines/davinci-codex/completions",
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
            file_name = f"{bank_name}_number_leads.txt"
            with open(file_name, "w") as file:
                file.write("\n".join(number_leads))
            # Send the number leads file to the user
            with open(file_name, "rb") as file:
                bot.send_document(chat_id, file)
        # Catch any errors that might occur
        except telebot.apihelper.ApiTelegramException as e:
            # Log the error message
            print(f"Error from Telegram API: {e}")
            # Send a feedback message to the user
            bot.reply_to(message, "Sorry, something went wrong with the Telegram API. Please try again later.")
        except requests.exceptions.RequestException as e:
            # Log the error message
            print(f"Error from OpenAI API: {e}")
            # Send a feedback message to the user
            bot.reply_to(message, "Sorry, something went wrong with the OpenAI API. Please try again later.")

# Start the bot polling
bot.polling()
